#!/usr/bin/env python3
"""Générateur IconForge : Gemini 3.6 Flash avec fallback SVG local déterministe."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "extraction-complet"))
from validate_svg import profile_from_specification, validate_file  # type: ignore[import-not-found] # noqa: E402

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = "gemini-3.6-flash"
GEMINI_MAX_RETRIES = 3
GEMINI_RETRY_DELAYS = (2, 5, 10)
SVG_MAX_ATTEMPTS = 3
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
SVG_RE = re.compile(r"<svg\b[\s\S]*?</svg>", re.IGNORECASE)
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def load_env_file(path: Path = ROOT / ".env") -> None:
    """Charge les variables du fichier .env sans remplacer l'environnement."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in {"GEMINI_API_KEY", "GEMINI_MODEL"} and key not in os.environ:
            os.environ[key] = value


def read_requests(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    requests = data.get("requests")
    if not isinstance(requests, list) or not requests:
        raise ValueError("requests.json doit contenir une liste requests non vide")
    for request in requests:
        if not isinstance(request, dict) or not ID_RE.fullmatch(str(request.get("id", ""))):
            raise ValueError("chaque id doit respecter le format ^[a-z0-9][a-z0-9-]*$")
        if not str(request.get("concept", "")).strip():
            raise ValueError(f"concept vide pour {request['id']}")
    return requests


def load_specification() -> tuple[dict, dict]:
    charte = ROOT / "brand-guidelines.md"
    references = ROOT / "references"
    specification_path = ROOT / "specification.json"
    if not charte.is_file() or not references.is_dir():
        raise ValueError("brand-guidelines.md ou references/ est introuvable")

    try:
        from extraire_specification import extraire_specification_locale  # type: ignore[import-not-found]
        from svg_preextract import pre_extraire_dossier  # type: ignore[import-not-found]

        charte_text = charte.read_text(encoding="utf-8")
        reports = pre_extraire_dossier(references)
        specification = extraire_specification_locale(charte_text, reports)
    except (ImportError, OSError, ValueError):
        if not specification_path.is_file():
            raise ValueError("impossible d'extraire la charte : installez svgelements")
        specification = json.loads(specification_path.read_text(encoding="utf-8"))

    profile = profile_from_specification(specification)
    profile["allowed_colors"] = [str(value).upper() for value in profile["allowed_colors"]]
    profile["required_colors"] = [str(value).upper() for value in profile["required_colors"]]
    profile["max_colors"] = int(profile["max_colors"])
    profile["safe_min"] = float(profile["safe_min"])
    profile["safe_max"] = float(profile["safe_max"])
    profile["safe_y_min"] = float(profile["safe_y_min"])
    profile["safe_y_max"] = float(profile["safe_y_max"])
    profile["stroke_widths"] = [float(value) for value in profile["stroke_widths"]]
    return specification, profile


def palette(specification: dict) -> list[str]:
    colors = []
    for item in specification.get("palette", {}).get("couleurs_prescrites", []):
        value = item.get("hex") if isinstance(item, dict) else None
        if isinstance(value, str) and HEX_RE.fullmatch(value):
            colors.append(value.upper())
    if len(colors) < 2:
        raise ValueError("la spécification ne contient pas au moins deux couleurs hexadécimales")
    return colors


def build_prompt(request: dict, specification: dict, feedback: dict | None) -> str:
    technical = specification.get("format_technique", {})
    trait = specification.get("trait", {})
    prompt = f"""Tu es un générateur SVG strict pour IconForge AI.
Concept : {request['concept']}
Contexte : {request.get('context', '')}
Mots-clés : {', '.join(request.get('keywords', []))}

Spécification active, lue à l'exécution :
{json.dumps(specification, ensure_ascii=False, indent=2)}

Contraintes obligatoires :
- produire uniquement un document SVG autonome, sans Markdown ni explication ;
- viewBox exactement {technical.get('viewBox')};
- fond transparent ;
- couleurs uniquement celles de la spécification ;
- maximum {technical.get('max_couleurs_visibles')} couleurs visibles ;
- stroke-width {trait.get('epaisseur_prescrite')};
- stroke-linecap {trait.get('linecap_prescrit')};
- stroke-linejoin {trait.get('linejoin_prescrit')};
- déclarer explicitement fill, stroke et tous les attributs de trait sur chaque forme visible ;
- ne jamais utiliser le remplissage SVG implicite noir : utiliser fill="none" ou une couleur autorisée ;
- ne jamais utiliser stroke-width="2" : la valeur prescrite est obligatoire partout où un contour existe ;
- appliquer stroke-linecap et stroke-linejoin à chaque forme avec contour, sauf stroke-linejoin sur une balise line ;
- aucune balise text, image, script, style, filter, mask, gradient ou animation ;
- silhouette simple, compacte et lisible à petite taille ;
- ne jamais copier un logo ou une marque.
"""
    if feedback:
        prompt += "\nFeedback de validation à corriger :\n" + json.dumps(feedback, ensure_ascii=False, indent=2)
    return prompt


def gemini_generate(prompt: str, api_key: str, model: str) -> str:
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "text/plain"},
    }
    request = urllib.request.Request(
        GEMINI_ENDPOINT.format(model=model) + "?key=" + urllib.parse.quote(api_key),
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(GEMINI_MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            if error.code not in {429, 500, 503} or attempt == GEMINI_MAX_RETRIES:
                raise RuntimeError(f"Gemini HTTP {error.code}: {detail}") from error
            delay = GEMINI_RETRY_DELAYS[attempt]
            print(
                f"Gemini temporairement indisponible (HTTP {error.code}), nouvelle tentative dans {delay}s...",
                file=sys.stderr,
            )
            time.sleep(delay)
        except urllib.error.URLError as error:
            if attempt == GEMINI_MAX_RETRIES:
                raise RuntimeError(f"Gemini inaccessible: {error.reason}") from error
            delay = GEMINI_RETRY_DELAYS[attempt]
            print(f"Gemini inaccessible, nouvelle tentative dans {delay}s...", file=sys.stderr)
            time.sleep(delay)
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError(f"réponse Gemini sans SVG: {data}") from error


def extract_svg(text: str) -> str:
    match = SVG_RE.search(text)
    if not match:
        raise ValueError("la réponse du générateur ne contient pas de document SVG")
    return match.group(0).strip()


def local_svg(concept: str, specification: dict) -> str:
    colors = palette(specification)
    viewbox = specification.get("format_technique", {}).get("viewBox") or "0 0 64 64"
    trait = specification.get("trait", {})
    width = trait.get("epaisseur_prescrite") or 2.5
    cap = trait.get("linecap_prescrit") or "round"
    join = trait.get("linejoin_prescrit") or "round"
    digest = hashlib.sha256(concept.encode("utf-8")).digest()
    radius = 16 + digest[0] % 7
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" fill="none">
  <circle cx="32" cy="32" r="{radius}" fill="{colors[0]}" stroke="{colors[1]}" stroke-width="{width}" stroke-linecap="{cap}" stroke-linejoin="{join}"/>
  <path d="M22 33l7 7 14-16" stroke="{colors[2] if len(colors) > 2 else colors[1]}" stroke-width="{width}" stroke-linecap="{cap}" stroke-linejoin="{join}"/>
</svg>'''


def generate_one(request: dict, specification: dict, profile: dict, output: Path, feedback_path: Path | None, api_key: str | None, model: str) -> dict:
    feedback = json.loads(feedback_path.read_text(encoding="utf-8")) if feedback_path else None
    feedback_data = feedback
    for attempt in range(1, SVG_MAX_ATTEMPTS + 1):
        if api_key:
            try:
                raw_svg = gemini_generate(build_prompt(request, specification, feedback_data), api_key, model)
                source = "gemini"
            except RuntimeError as error:
                if not any(f"Gemini HTTP {code}" in str(error) for code in (429, 500, 503)):
                    raise
                print(f"Gemini indisponible après plusieurs tentatives : {error}", file=sys.stderr)
                print("Utilisation du fallback local déterministe.", file=sys.stderr)
                raw_svg = local_svg(request["concept"], specification)
                source = "local-fallback-after-gemini-error"
        else:
            raw_svg = local_svg(request["concept"], specification)
            source = "local-fallback"
        svg = extract_svg(raw_svg)
        temporary = output.with_suffix(".candidate.svg")
        temporary.write_text(svg, encoding="utf-8")
        report = validate_file(temporary, profile)
        temporary.unlink(missing_ok=True)
        if report["valid"]:
            output.write_text(svg, encoding="utf-8")
            return {"id": request["id"], "source": source, "attempts": attempt, "validation": report}
        if not api_key or attempt == SVG_MAX_ATTEMPTS:
            raise RuntimeError(f"SVG invalide pour {request['id']}: {'; '.join(report['errors'])}")
        feedback_data = {"validation_errors": report["errors"], "attempt": attempt}
        print(f"SVG invalide pour {request['id']}, nouvelle génération ({attempt + 1}/{SVG_MAX_ATTEMPTS})...", file=sys.stderr)
    raise RuntimeError(f"SVG invalide pour {request['id']}")


def main() -> int:
    load_env_file()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", default=os.getenv("GEMINI_MODEL", DEFAULT_MODEL))
    parser.add_argument("--seed", type=int, default=0, help="graine documentée pour le fallback local")
    args = parser.parse_args()
    try:
        requests = read_requests(args.input)
        specification, profile = load_specification()
        args.output.mkdir(parents=True, exist_ok=True)
        api_key = os.getenv("GEMINI_API_KEY")
        results = []
        for request in requests:
            results.append(generate_one(request, specification, profile, args.output / f"{request['id']}.svg", None, api_key, args.model))
        print(json.dumps({"model": args.model if api_key else "local-fallback", "seed": args.seed, "results": results}, ensure_ascii=False, indent=2))
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"Erreur de génération: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
