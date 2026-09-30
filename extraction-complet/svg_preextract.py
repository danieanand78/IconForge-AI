#!/usr/bin/env python3
"""
svg_preextract.py
------------------
Pré-extraction DÉTERMINISTE de faits techniques depuis des fichiers SVG de
référence, en amont d'un prompt LLM d'extraction de spécification.

Objectif : ne jamais laisser un LLM recalculer lui-même des valeurs
géométriques ou lister des couleurs par lecture visuelle du XML. Ce script
produit un rapport factuel, exact et reproductible par fichier, qui sera
ensuite injecté comme contexte (et non comme "source à recalculer") dans le
prompt d'extraction de spécification.

Faits extraits (100% déterministes, aucune interprétation) :
  - couleurs réellement utilisées (fill / stroke, hex 3 ou 6 chiffres)
  - épaisseurs de trait réellement utilisées (stroke-width)
  - linecap / linejoin réellement utilisés
  - viewBox déclaré
  - bounding box RÉELLE du contenu dessiné (via svgelements), à comparer à la
    zone utile prescrite par la charte
  - éléments/techniques interdits détectés (raster embarqué, texte, script,
    gradient, filtre, masque, animation)
  - nombre de couleurs visibles distinctes
  - validité XML de base

Usage :
    python3 svg_preextract.py <dossier_references> [--out rapport.json]

Dépendance : pip install svgelements --break-system-packages
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from svgelements import SVG
except ImportError:
    sys.exit(
        "Dépendance manquante : pip install svgelements --break-system-packages"
    )


# --------------------------------------------------------------------------
# Détection d'éléments / techniques interdits par la charte
# --------------------------------------------------------------------------
# Chaque entrée : (clé de sortie, regex insensible à la casse)
INTERDITS_PATTERNS = {
    "image_matricielle": r"<image\b",
    "texte": r"<text\b|<tspan\b",
    "police_externe": r"@font-face|font-family\s*=",
    "script": r"<script\b|on\w+\s*=",
    "lien_externe": r"<a\b[^>]*href",
    "gradient": r"<linearGradient\b|<radialGradient\b|fill\s*=\s*\"url\(#|stroke\s*=\s*\"url\(#",
    "filtre": r"<filter\b|filter\s*=\s*\"url\(",
    "masque": r"<mask\b|<clipPath\b",
    "animation": r"<animate\b|<animateTransform\b|<animateMotion\b|<set\b",
}

COULEUR_HEX_RE = re.compile(r"#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b")

def extraire_attributs(svg_text: str, attribut: str) -> list[str]:
    motif = rf'\b{re.escape(attribut)}\s*=\s*(["\'])(.*?)\1'
    valeurs = re.findall(motif, svg_text, flags=re.IGNORECASE | re.DOTALL)
    return [valeur for _, valeur in valeurs]


def extraire_proprietes_css(svg_text: str, propriete: str) -> list[str]:
    motif = rf'(?:^|[;{{\s]){re.escape(propriete)}\s*:\s*([^;}}]+)'
    return [valeur.strip() for valeur in re.findall(motif, svg_text, flags=re.IGNORECASE)]


VIEWBOX_RE = re.compile(r"\bviewBox\s*=\s*([\"'])(.*?)\1", re.IGNORECASE | re.DOTALL)


# Attributs dans lesquels chercher des couleurs (on ignore les valeurs
# spéciales "none" et "currentColor" qui ne sont pas des couleurs visibles).
ATTRS_COULEUR = ["fill", "stroke", "stop-color"]


def normaliser_hex(hex_code: str) -> str:
    """Étend un hex 3 chiffres (#abc) en 6 chiffres (#aabbcc), en majuscules."""
    h = hex_code.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h.upper()


def extraire_couleurs(svg_text: str) -> list[str]:
    """Retourne la liste triée des couleurs hex distinctes réellement présentes
    dans les attributs fill/stroke/stop-color du document et les propriétés CSS
    équivalentes dans style ou <style>."""
    couleurs = set()
    for attr in ATTRS_COULEUR:
        valeurs = extraire_attributs(svg_text, attr)
        valeurs += extraire_proprietes_css(svg_text, attr)
        for valeur in valeurs:
            for hexm in COULEUR_HEX_RE.finditer(valeur):
                couleurs.add(normaliser_hex(hexm.group(0)))
    return sorted(couleurs)


def extraire_interdits(svg_text: str) -> list[str]:
    trouves = []
    for cle, pattern in INTERDITS_PATTERNS.items():
        if re.search(pattern, svg_text, flags=re.IGNORECASE):
            trouves.append(cle)
    return trouves


def extraire_viewbox(svg_text: str):
    m = VIEWBOX_RE.search(svg_text)
    if not m:
        return None
    try:
        parts = [float(x) for x in m.group(2).replace(",", " ").split()]
        if len(parts) == 4:
            return {"min_x": parts[0], "min_y": parts[1], "width": parts[2], "height": parts[3]}
    except ValueError:
        pass
    return None


def valider_xml(svg_text: str):
    """Retourne (True, None) si le XML est bien formé, sinon (False, message)."""
    try:
        ET.fromstring(svg_text)
        return True, None
    except ET.ParseError as e:
        return False, str(e)


def calculer_bbox_reelle(chemin_fichier: Path):
    """Calcule la bounding box réelle du contenu dessiné (tous les éléments
    géométriques : path, rect, circle, ellipse, polygon, polyline, line),
    via svgelements, qui résout correctement les transform, les arcs et les
    courbes de Bézier — contrairement à une simple lecture des attributs
    x/y/cx/cy qui ignore les transformations.

    Retourne None si le document ne contient aucun élément géométrique
    exploitable (cas d'un SVG vide ou invalide).
    """
    try:
        svg = SVG.parse(str(chemin_fichier))
    except Exception as e:
        return {"erreur": f"échec de parsing géométrique : {e}"}

    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    trouve = False

    for element in svg.elements():
        # On ignore les conteneurs purs (groupes, le SVG racine lui-même) qui
        # n'ont pas de géométrie propre exploitable directement.
        bbox = None
        try:
            bbox = element.bbox()
        except Exception:
            bbox = None
        if bbox is None:
            continue
        bx_min, by_min, bx_max, by_max = bbox
        # svgelements peut renvoyer des bbox non ordonnées selon l'orientation
        bx_min, bx_max = sorted((bx_min, bx_max))
        by_min, by_max = sorted((by_min, by_max))
        min_x, max_x = min(min_x, bx_min), max(max_x, bx_max)
        min_y, max_y = min(min_y, by_min), max(max_y, by_max)
        trouve = True

    if not trouve:
        return None

    return {
        "x_min": round(min_x, 3),
        "x_max": round(max_x, 3),
        "y_min": round(min_y, 3),
        "y_max": round(max_y, 3),
        "largeur": round(max_x - min_x, 3),
        "hauteur": round(max_y - min_y, 3),
    }


def pre_extraire_fichier(chemin_fichier: Path) -> dict:
    svg_text = chemin_fichier.read_text(encoding="utf-8")

    xml_valide, erreur_xml = valider_xml(svg_text)
    couleurs = extraire_couleurs(svg_text)
    epaisseurs = {
        float(value) for value in extraire_attributs(svg_text, "stroke-width")
        if re.fullmatch(r"[\d.]+", value.strip())
    }
    epaisseurs.update(
        float(value) for value in extraire_proprietes_css(svg_text, "stroke-width")
        if re.fullmatch(r"[\d.]+", value.strip())
    )
    linecaps = set(extraire_attributs(svg_text, "stroke-linecap"))
    linecaps.update(extraire_proprietes_css(svg_text, "stroke-linecap"))
    linejoins = set(extraire_attributs(svg_text, "stroke-linejoin"))
    linejoins.update(extraire_proprietes_css(svg_text, "stroke-linejoin"))
    viewbox = extraire_viewbox(svg_text)
    interdits = extraire_interdits(svg_text)
    bbox_reelle = calculer_bbox_reelle(chemin_fichier) if xml_valide else None

    rapport = {
        "fichier": chemin_fichier.name,
        "chemin": str(chemin_fichier),
        "xml_valide": xml_valide,
        "erreur_xml": erreur_xml,
        "viewbox_declare": viewbox,
        "bbox_reelle_contenu": bbox_reelle,
        "couleurs_utilisees": couleurs,
        "nombre_couleurs_visibles": len(couleurs),
        "epaisseurs_trait_utilisees": sorted(epaisseurs),
        "linecap_utilises": sorted(linecaps),
        "linejoin_utilises": sorted(linejoins),
        "elements_interdits_detectes": interdits,
        "conforme_sans_interdit": len(interdits) == 0,
        "taille_octets": len(svg_text.encode("utf-8")),
    }
    return rapport


def pre_extraire_dossier(dossier: Path) -> list[dict]:
    fichiers = sorted(dossier.rglob("*.svg"))
    if not fichiers:
        print(f"Attention : aucun fichier .svg trouvé dans {dossier}", file=sys.stderr)
    return [pre_extraire_fichier(f) for f in fichiers]


def main():
    parser = argparse.ArgumentParser(
        description="Pré-extraction déterministe de faits techniques SVG."
    )
    parser.add_argument("dossier", type=Path, help="Dossier contenant les .svg de référence")
    parser.add_argument(
        "--out", type=Path, default=Path("pre_extraction_svg.json"),
        help="Chemin du fichier JSON de sortie (défaut: pre_extraction_svg.json)"
    )
    args = parser.parse_args()

    if not args.dossier.is_dir():
        sys.exit(f"Erreur : {args.dossier} n'est pas un dossier valide.")

    rapports = pre_extraire_dossier(args.dossier)

    sortie = {
        "nombre_fichiers_analyses": len(rapports),
        "rapports": rapports,
    }

    args.out.write_text(json.dumps(sortie, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK : {len(rapports)} fichier(s) analysé(s) -> {args.out}")


if __name__ == "__main__":
    main()
