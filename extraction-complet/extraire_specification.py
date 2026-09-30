#!/usr/bin/env python3
"""
extraire_specification.py
--------------------------
Étape finale du pipeline. Fusionne :
  - le texte de la charte de design (dynamique : peut changer à chaque exécution)
  - les rapports techniques bruts des SVG de référence (produits par svg_preextract.py)
en UN SEUL fichier `specification.json` contenant uniquement l'information
utile, par extraction Python déterministe, sans réseau et sans clé API.

Usage :
    python3 extraire_specification.py \
                --charte brand-guidelines.md \
                --references references/ \
        --out specification.json
"""

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from svg_preextract import pre_extraire_dossier
except ImportError:
    sys.exit(
        "svg_preextract.py doit se trouver dans le même dossier que ce script."
    )

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
MAX_TENTATIVES = 3
API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
TOOL_NAME = "extraire_specification"


# --------------------------------------------------------------------------
# Schéma de sortie forcé (tool input_schema)
# --------------------------------------------------------------------------
SCHEMA_SPECIFICATION = {
    "type": "object",
    "properties": {
        "marque": {
            "type": "object",
            "properties": {
                "couleurs_officielles_reutilisees": {"type": "array", "items": {"type": "string"}},
                "elements_proteges_interdits": {"type": "array", "items": {"type": "string"}},
                "affiliation_officielle": {"type": "boolean"},
            },
        },
        "format_technique": {
            "type": "object",
            "properties": {
                "viewBox": {"type": "string"},
                "zone_utile": {
                    "type": "object",
                    "properties": {
                        "x_min": {"type": "number"},
                        "x_max": {"type": "number"},
                        "y_min": {"type": "number"},
                        "y_max": {"type": "number"},
                    },
                    "required": ["x_min", "x_max", "y_min", "y_max"],
                },
                "fond_transparent": {"type": "boolean"},
                "max_couleurs_visibles": {"type": "integer"},
                "elements_interdits": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["viewBox", "zone_utile", "max_couleurs_visibles"],
        },
        "palette": {
            "type": "object",
            "properties": {
                "couleurs_prescrites": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "nom": {"type": "string"},
                            "hex": {"type": "string"},
                            "role": {"type": "string"},
                            "statut": {"type": "string"},
                        },
                        "required": ["nom", "hex"],
                    },
                },
                "couleur_dominante_attendue": {"type": ["string", "null"]},
                "couleurs_observees_dans_references": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["couleurs_prescrites"],
        },
        "trait": {
            "type": "object",
            "properties": {
                "epaisseur_prescrite": {"type": ["number", "null"]},
                "epaisseur_observee_dans_references": {"type": "array", "items": {"type": "number"}},
                "linecap_prescrit": {"type": ["string", "null"]},
                "linejoin_prescrit": {"type": ["string", "null"]},
            },
        },
        "grille_construction": {
            "type": "object",
            "properties": {
                "taille": {"type": ["number", "null"]},
                "alignement_strict": {"type": ["boolean", "null"]},
                "note": {"type": ["string", "null"]},
            },
        },
        "style_qualitatif": {
            "type": "object",
            "properties": {
                "criteres_charte": {"type": "array", "items": {"type": "string"}},
                "observations_references": {"type": "object"},
            },
        },
        "coherence_collection": {
            "type": "object",
            "properties": {"criteres": {"type": "array", "items": {"type": "string"}}},
        },
        "interdits_stylistiques": {"type": "array", "items": {"type": "string"}},
        "concepts_references_attendus": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"fichier": {"type": "string"}, "concept": {"type": "string"}},
            },
        },
        "anomalies_detectees": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["format_technique", "palette", "trait", "interdits_stylistiques"],
}


def construire_system_prompt() -> str:
    return (
        "Tu es un extracteur de spécifications techniques. Tu reçois deux types d'entrées : "
        "1) le texte intégral d'une charte de design (Markdown), potentiellement différente à "
        "chaque exécution ; 2) une liste de fichiers SVG de référence, chacun accompagné d'un "
        "pré-rapport technique déjà calculé de façon déterministe (couleurs utilisées, épaisseurs "
        "de trait, éléments interdits détectés, viewBox déclaré, bounding box réelle) et du code "
        "source SVG brut.\n\n"
        "Ta tâche : appeler l'outil fourni pour produire UNE SEULE spécification structurée. "
        "Règles strictes :\n"
        "- N'invente aucune valeur absente de la charte : utilise null ou un tableau vide.\n"
        "- Les faits numériques (couleurs hex, épaisseurs de trait, viewBox, zone utile) "
        "proviennent en priorité du texte de la charte.\n"
        "- Les valeurs des pré-rapports SVG servent UNIQUEMENT à remplir les champs contenant "
        "'observee'/'observees' et à peupler 'anomalies_detectees' en cas d'écart avec la charte. "
        "Ne recalcule jamais toi-même une bounding box ou une couleur hex à partir du SVG brut : "
        "utilise exclusivement les valeurs déjà présentes dans le pré-rapport pour ces faits.\n"
        "- Le code SVG brut sert uniquement à juger des critères qualitatifs (style, concept "
        "illustré, ambiance, niveau de détail, asymétrie, technique d'ombre) que le pré-rapport "
        "ne capture pas.\n"
        "- Si la charte indique qu'une règle est recommandée mais non éliminatoire, reflète cette "
        "nuance (par exemple alignement_strict=false), ne la transforme pas en booléen absolu.\n"
        "- Si un fichier de référence contredit une règle écrite de la charte, n'arbitre pas "
        "toi-même : ajoute une entrée dans 'anomalies_detectees' décrivant l'écart.\n"
        "- Toute couleur hex doit être au format '#RRGGBB' (6 chiffres, avec le dièse).\n"
        "- Réponds uniquement via l'appel de l'outil fourni. Aucun texte libre hors de l'appel."
    )


def construire_message_utilisateur(charte_texte: str, rapports_svg: list[dict]) -> str:
    parties = [f"[CHARTE_TEXTE]\n{charte_texte}\n[/CHARTE_TEXTE]\n", "[REFERENCES]"]
    for rapport in rapports_svg:
        chemin = Path(rapport["chemin"])
        source = chemin.read_text(encoding="utf-8") if chemin.exists() else ""
        parties.append(
            f"\n--- Fichier: {rapport['fichier']} ---\n"
            "Pré-rapport technique (faits vérifiés, à utiliser tels quels pour toute valeur "
            f"numérique) :\n{json.dumps(rapport, ensure_ascii=False, indent=2)}\n"
            "Code source SVG brut (UNIQUEMENT pour juger le style/concept, jamais pour "
            f"recalculer des chiffres) :\n{source}\n"
        )
    parties.append("[/REFERENCES]")
    return "\n".join(parties)


def appeler_api(messages: list[dict], api_key: str, modele: str) -> dict:
    """Effectue l'appel réel à l'API Claude. Isolé dans sa propre fonction pour
    pouvoir être remplacé par une fausse fonction lors des tests (--self-test)."""
    corps = {
        "model": modele,
        "max_tokens": 4096,
        "system": construire_system_prompt(),
        "tools": [
            {
                "name": TOOL_NAME,
                "description": "Enregistre la spécification extraite et fusionnée.",
                "input_schema": SCHEMA_SPECIFICATION,
            }
        ],
        "tool_choice": {"type": "tool", "name": TOOL_NAME},
        "messages": messages,
    }
    requete = urllib.request.Request(
        API_URL,
        data=json.dumps(corps).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": API_VERSION,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(requete, timeout=120) as reponse:
            return json.loads(reponse.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Erreur API ({e.code}) : {detail}") from e


def extraire_tool_use(reponse: dict) -> tuple[dict, str]:
    for bloc in reponse.get("content", []):
        if bloc.get("type") == "tool_use" and bloc.get("name") == TOOL_NAME:
            return bloc["input"], bloc["id"]
    raise RuntimeError("Aucun appel d'outil trouvé dans la réponse de l'API.")


def valider_specification(spec: dict) -> list[str]:
    """Valide la sortie du LLM. Retourne une liste de problèmes (vide = OK).
    Ne fait confiance à AUCUNE valeur numérique produite par le modèle sans
    la revérifier ici : c'est la dernière ligne de défense avant écriture."""
    problemes = []

    for champ in ("format_technique", "palette", "trait", "interdits_stylistiques"):
        if champ not in spec:
            problemes.append(f"Champ obligatoire manquant : '{champ}'")

    for c in spec.get("palette", {}).get("couleurs_prescrites", []):
        hexv = c.get("hex", "")
        if not HEX_RE.match(hexv):
            problemes.append(f"Couleur hex invalide : '{hexv}' pour '{c.get('nom')}'")

    ft = spec.get("format_technique", {})
    largeur = hauteur = None
    vb = ft.get("viewBox")
    if vb:
        parts = vb.replace(",", " ").split()
        if len(parts) != 4:
            problemes.append(f"viewBox mal formé : '{vb}'")
        else:
            try:
                _, _, largeur, hauteur = (float(x) for x in parts)
            except ValueError:
                problemes.append(f"viewBox contient des valeurs non numériques : '{vb}'")

    zu = ft.get("zone_utile")
    if zu:
        for cle in ("x_min", "x_max", "y_min", "y_max"):
            if cle not in zu:
                problemes.append(f"zone_utile.{cle} manquant")
        if "x_min" in zu and "x_max" in zu and zu["x_min"] >= zu["x_max"]:
            problemes.append("zone_utile : x_min doit être strictement inférieur à x_max")
        if "y_min" in zu and "y_max" in zu and zu["y_min"] >= zu["y_max"]:
            problemes.append("zone_utile : y_min doit être strictement inférieur à y_max")
        if largeur is not None and zu.get("x_max", 0) > largeur:
            problemes.append(f"zone_utile.x_max ({zu.get('x_max')}) dépasse la largeur du viewBox ({largeur})")
        if hauteur is not None and zu.get("y_max", 0) > hauteur:
            problemes.append(f"zone_utile.y_max ({zu.get('y_max')}) dépasse la hauteur du viewBox ({hauteur})")

    ep = spec.get("trait", {}).get("epaisseur_prescrite")
    if ep is not None and (not isinstance(ep, (int, float)) or ep <= 0):
        problemes.append(f"trait.epaisseur_prescrite invalide : {ep}")

    return problemes


def executer_extraction(
    charte_texte: str,
    rapports_svg: list[dict],
    api_key: str,
    modele: str,
    max_tentatives: int = MAX_TENTATIVES,
    appel_api_fn=appeler_api,
) -> tuple[dict, int]:
    """Boucle d'extraction avec auto-correction : si la sortie du modèle ne
    passe pas la validation déterministe, on renvoie les erreurs précises au
    modèle sous forme de tool_result d'erreur et on lui redonne une chance de
    corriger, jusqu'à `max_tentatives`."""
    messages = [
        {"role": "user", "content": construire_message_utilisateur(charte_texte, rapports_svg)}
    ]
    derniere_spec = None

    for tentative in range(1, max_tentatives + 1):
        reponse = appel_api_fn(messages, api_key, modele)
        spec, tool_id = extraire_tool_use(reponse)
        problemes = valider_specification(spec)

        if not problemes:
            return spec, tentative

        derniere_spec = spec
        messages.append({"role": "assistant", "content": reponse["content"]})
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "is_error": True,
                        "content": (
                            "Validation échouée. Corrige STRICTEMENT ces problèmes et "
                            "rappelle l'outil avec un objet complet corrigé :\n- "
                            + "\n- ".join(problemes)
                        ),
                    }
                ],
            }
        )

    raise RuntimeError(
        f"Échec de validation après {max_tentatives} tentatives. "
        f"Dernière sortie : {json.dumps(derniere_spec, ensure_ascii=False)[:500]}..."
    )


def _section(charte: str, titre: str) -> str:
    match = re.search(
        rf"^##\s+[^\n]*{re.escape(titre)}[^\n]*$([\s\S]*?)(?=^##\s|\Z)",
        charte,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    return match.group(1) if match else ""


def _nombres(pattern: str, texte: str) -> list[float]:
    return [float(value.replace(",", ".")) for value in re.findall(pattern, texte, re.IGNORECASE)]


def extraire_specification_locale(charte: str, rapports_svg: list[dict]) -> dict:
    """Extrait les faits écrits dans la charte et les observations SVG sans IA."""
    format_technique = _section(charte, "Format SVG")
    palette_texte = _section(charte, "Palette")
    trait_texte = _section(charte, "Langage graphique")
    grille_texte = _section(charte, "Grille de construction")
    interdits_texte = _section(charte, "Interdictions stylistiques")
    references_texte = _section(charte, "Références fournies")

    viewbox_match = re.search(r'viewBox\s*=\s*["`]([^"`]+)', format_technique, re.IGNORECASE)
    viewbox = viewbox_match.group(1).strip() if viewbox_match else None
    zone_match = re.search(
        r"x\s*=\s*([\d.]+)\s*[.…-]+\s*([\d.]+).*?y\s*=\s*([\d.]+)\s*[.…-]+\s*([\d.]+)",
        format_technique,
        re.IGNORECASE | re.DOTALL,
    )
    zone = (
        {"x_min": float(zone_match.group(1)), "x_max": float(zone_match.group(2)),
         "y_min": float(zone_match.group(3)), "y_max": float(zone_match.group(4))}
        if zone_match else None
    )

    couleurs = []
    for ligne in palette_texte.splitlines():
        codes = re.findall(r"#[0-9A-Fa-f]{3,6}", ligne)
        if codes:
            cellules = [cell.strip() for cell in ligne.strip().strip("|").split("|")]
            couleurs.append({
                "nom": cellules[0] if cellules else "",
                "hex": codes[0].upper(),
                "role": cellules[1] if len(cellules) > 1 else "",
                "statut": cellules[2] if len(cellules) > 2 else "",
            })

    rapports_couleurs = sorted({c for r in rapports_svg for c in r.get("couleurs_utilisees", [])})
    rapports_epaisseurs = sorted({e for r in rapports_svg for e in r.get("epaisseurs_trait_utilisees", [])})
    linecaps = sorted({c for r in rapports_svg for c in r.get("linecap_utilises", [])})
    linejoins = sorted({j for r in rapports_svg for j in r.get("linejoin_utilises", [])})
    anomalies = []
    prescrites = {c["hex"] for c in couleurs}
    for rapport in rapports_svg:
        for couleur in rapport.get("couleurs_utilisees", []):
            if couleur not in prescrites:
                anomalies.append(f"{rapport['fichier']} utilise une couleur absente de la charte : {couleur}")
        if rapport.get("elements_interdits_detectes"):
            anomalies.append(f"{rapport['fichier']} contient : {', '.join(rapport['elements_interdits_detectes'])}")

    concepts = []
    for ligne in references_texte.splitlines():
        match = re.match(r"\s*-\s*`([^`]+)`\s*[—-]\s*(.+)", ligne)
        if match:
            concepts.append({"fichier": match.group(1), "concept": match.group(2).strip()})

    return {
        "marque": {
            "couleurs_officielles_reutilisees": [c["hex"] for c in couleurs if "officielle" in c.get("statut", "").lower()],
            "elements_proteges_interdits": [line.strip(" -*") for line in _section(charte, "Utilisation de la marque").splitlines() if line.strip().startswith("-")],
            "affiliation_officielle": False,
        },
        "format_technique": {
            "viewBox": viewbox,
            "zone_utile": zone,
            "fond_transparent": "transparent" in format_technique.lower(),
            "max_couleurs_visibles": int(_nombres(r"maximum\s+\**(\d+)\**\s+couleurs", format_technique)[0]) if _nombres(r"maximum\s+\**(\d+)\**\s+couleurs", format_technique) else None,
            "elements_interdits": [line.strip(" -*") for line in format_technique.splitlines() if line.strip().startswith("-") and ("aucune" in line.lower() or "aucun" in line.lower())],
        },
        "palette": {"couleurs_prescrites": couleurs, "couleur_dominante_attendue": "jaune" if "jaune" in palette_texte.lower() else None, "couleurs_observees_dans_references": rapports_couleurs},
        "trait": {
            "epaisseur_prescrite": _nombres(r"contours?\s+sombres?\s+de\s+[`*]*([\d.]+)", trait_texte)[0] if _nombres(r"contours?\s+sombres?\s+de\s+[`*]*([\d.]+)", trait_texte) else None,
            "epaisseur_observee_dans_references": rapports_epaisseurs,
            "linecap_prescrit": "round" if "stroke-linecap=\"round\"" in trait_texte else None,
            "linejoin_prescrit": "round" if "stroke-linejoin=\"round\"" in trait_texte else None,
        },
        "grille_construction": {"taille": _nombres(r"grille logique de\s+(\d+)", grille_texte)[0] if _nombres(r"grille logique de\s+(\d+)", grille_texte) else None, "alignement_strict": False, "note": grille_texte.strip() or None},
        "style_qualitatif": {"criteres_charte": [line.strip(" -*") for line in trait_texte.splitlines() if line.strip().startswith("-")], "observations_references": {r["fichier"]: {"couleurs": r.get("couleurs_utilisees", []), "bbox": r.get("bbox_reelle_contenu")} for r in rapports_svg}},
        "coherence_collection": {"criteres": [line.strip(" -*") for line in _section(charte, "Cohérence de collection").splitlines() if line.strip().startswith("-")]},
        "interdits_stylistiques": [line.strip(" -*") for line in interdits_texte.splitlines() if line.strip().startswith("-")],
        "concepts_references_attendus": concepts,
        "anomalies_detectees": anomalies,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fusionne une charte de design + des SVG de référence en une spécification JSON unique."
    )
    parser.add_argument("--charte", type=Path, help="Chemin du fichier charte (.md)")
    parser.add_argument("--references", type=Path, help="Dossier contenant les .svg de référence")
    parser.add_argument("--out", type=Path, default=Path("specification.json"))
    args = parser.parse_args()

    if not args.charte or not args.references:
        sys.exit("Erreur : --charte et --references sont requis (ou utilisez --self-test).")

    if not args.charte.is_file():
        sys.exit(f"Erreur : fichier charte introuvable : {args.charte}")
    if not args.references.is_dir():
        sys.exit(f"Erreur : dossier de références introuvable : {args.references}")

    charte_texte = args.charte.read_text(encoding="utf-8")
    rapports_svg = pre_extraire_dossier(args.references)

    spec = extraire_specification_locale(charte_texte, rapports_svg)

    spec.setdefault("meta", {})
    spec["meta"]["hash_charte"] = hashlib.sha256(charte_texte.encode("utf-8")).hexdigest()
    spec["meta"]["fichiers_references_analyses"] = [r["fichier"] for r in rapports_svg]
    spec["meta"]["date_extraction"] = datetime.now(timezone.utc).isoformat()
    spec["meta"]["methode"] = "extraction Python déterministe"

    args.out.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK -> {args.out} (extraction locale déterministe)")


if __name__ == "__main__":
    main()
