#!/usr/bin/env python3
"""Validateur déterministe des SVG du challenge IconForge AI."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PUBLIC_PROFILE = {
    "name": "public-huggingface-inspired-v1",
    "view_box": "0 0 64 64",
    "allowed_colors": ["#FFD21E", "#FF9D00", "#6B7280", "#111827", "#FFFFFF"],
    "required_colors": ["#FFD21E"],
    "max_colors": 4,
    "safe_min": 5.0,
    "safe_max": 59.0,
    "stroke_widths": [2.5],
    "stroke_linecap": "round",
    "stroke_linejoin": "round",
}
FORBIDDEN_TAGS = {
    "animate",
    "animateMotion",
    "animateTransform",
    "filter",
    "foreignObject",
    "image",
    "linearGradient",
    "mask",
    "radialGradient",
    "script",
    "style",
    "text",
}
GRAPHIC_TAGS = {"circle", "ellipse", "line", "path", "polygon", "polyline", "rect"}
FILLED_TAGS = {"circle", "ellipse", "path", "polygon", "polyline", "rect"}
PRESENTATION_ATTRS = {
    "fill",
    "stroke",
    "stroke-width",
    "stroke-linecap",
    "stroke-linejoin",
    "opacity",
    "fill-opacity",
    "stroke-opacity",
    "display",
    "visibility",
}
URL_PATTERN = re.compile(r"url\s*\(", re.IGNORECASE)
HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")
BOUND_TOLERANCE = 0.01

DEFAULT_STYLE = {
    "fill": "#000000",
    "stroke": "none",
    "stroke-width": "1",
    "stroke-linecap": "butt",
    "stroke-linejoin": "miter",
    "opacity": "1",
    "fill-opacity": "1",
    "stroke-opacity": "1",
    "display": "inline",
    "visibility": "visible",
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_style(style: str) -> tuple[dict[str, str], list[str]]:
    result: dict[str, str] = {}
    errors: list[str] = []
    for declaration in style.split(";"):
        declaration = declaration.strip()
        if not declaration:
            continue
        if ":" not in declaration:
            errors.append(f"Déclaration CSS invalide: {declaration}.")
            continue
        key, value = declaration.split(":", 1)
        result[key.strip()] = value.strip()
    return result, errors


def profile_from_specification(data: dict) -> dict:
    """Convertit specification.json en profil interne du validateur."""
    technique = data.get("format_technique", {})
    palette = data.get("palette", {})
    trait = data.get("trait", {})
    if not isinstance(technique, dict) or not isinstance(palette, dict) or not isinstance(trait, dict):
        raise ValueError("la spécification doit contenir des objets format_technique, palette et trait")
    zone_utile = technique.get("zone_utile", {})
    couleurs = palette.get("couleurs_prescrites", [])
    if not isinstance(zone_utile, dict):
        raise ValueError("format_technique.zone_utile doit être un objet")
    if not isinstance(couleurs, list):
        raise ValueError("palette.couleurs_prescrites doit être une liste")

    profile = {
        "name": "extracted-specification",
        "view_box": technique.get("viewBox"),
        "allowed_colors": [color.get("hex") for color in couleurs if isinstance(color, dict)],
        "required_colors": [],
        "max_colors": technique.get("max_couleurs_visibles"),
        "safe_min": zone_utile.get("x_min"),
        "safe_max": zone_utile.get("x_max"),
        "safe_y_min": zone_utile.get("y_min"),
        "safe_y_max": zone_utile.get("y_max"),
        "stroke_widths": [trait["epaisseur_prescrite"]]
        if trait.get("epaisseur_prescrite") is not None
        else [],
        "stroke_linecap": trait.get("linecap_prescrit"),
        "stroke_linejoin": trait.get("linejoin_prescrit"),
    }
    required = technique.get("couleurs_obligatoires", [])
    if isinstance(required, list):
        profile["required_colors"] = required
    return profile


def load_profile(path: Path | None) -> dict:
    profile = dict(PUBLIC_PROFILE)
    if path is not None:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("le profil doit être un objet JSON")
        profile.update(profile_from_specification(data) if "format_technique" in data else data)

    profile["name"] = str(profile["name"])
    profile["view_box"] = str(profile["view_box"])
    profile["allowed_colors"] = [str(value).upper() for value in profile["allowed_colors"]]
    profile["required_colors"] = [str(value).upper() for value in profile.get("required_colors", [])]
    profile["max_colors"] = int(profile["max_colors"])
    profile["safe_min"] = float(profile["safe_min"])
    profile["safe_max"] = float(profile["safe_max"])
    profile["safe_y_min"] = float(profile.get("safe_y_min", profile["safe_min"]))
    profile["safe_y_max"] = float(profile.get("safe_y_max", profile["safe_max"]))
    profile["stroke_widths"] = [float(value) for value in profile["stroke_widths"]]
    profile["stroke_linecap"] = str(profile["stroke_linecap"])
    profile["stroke_linejoin"] = str(profile["stroke_linejoin"])

    if not profile["allowed_colors"]:
        raise ValueError("allowed_colors ne peut pas être vide")
    if profile["max_colors"] < 1:
        raise ValueError("max_colors doit être positif")
    if profile["safe_min"] >= profile["safe_max"]:
        raise ValueError("safe_min doit être inférieur à safe_max")
    if profile["safe_y_min"] >= profile["safe_y_max"]:
        raise ValueError("safe_y_min doit être inférieur à safe_y_max")
    if not profile["stroke_widths"]:
        raise ValueError("stroke_widths ne peut pas être vide")
    for color in profile["allowed_colors"] + profile["required_colors"]:
        if not HEX_COLOR_PATTERN.fullmatch(color):
            raise ValueError(f"couleur invalide dans le profil: {color}")
    return profile


def color_value(
    value: str,
    context: str,
    errors: list[str],
    allowed_colors: set[str],
) -> str | None:
    normalized = value.strip().upper()
    if normalized in {"NONE", "TRANSPARENT"}:
        return None
    if not HEX_COLOR_PATTERN.fullmatch(normalized):
        errors.append(f"Couleur non hexadécimale ou indirecte dans {context}: {value}.")
        return None
    if normalized not in allowed_colors:
        errors.append(f"Couleur hors palette dans {context}: {normalized}.")
    return normalized


def walk_elements(
    element: ET.Element,
    inherited: dict[str, str],
    errors: list[str],
    colors: set[str],
    profile: dict,
) -> None:
    tag = local_name(element.tag)
    if tag in FORBIDDEN_TAGS:
        errors.append(f"Élément interdit: <{tag}>.")

    direct = {key: value for key, value in element.attrib.items() if key in PRESENTATION_ATTRS}
    inline, style_errors = parse_style(element.attrib.get("style", ""))
    errors.extend(f"<{tag}>: {message}" for message in style_errors)
    direct.update({key: value for key, value in inline.items() if key in PRESENTATION_ATTRS})

    effective = dict(inherited)
    effective.update(direct)

    for key, value in element.attrib.items():
        key_name = local_name(key)
        if key_name.lower().startswith("on"):
            errors.append(f"Gestionnaire d’événement interdit dans <{tag}>: {key_name}.")
        if key_name == "href":
            errors.append(f"Référence href interdite dans <{tag}>.")
        if key_name == "class":
            errors.append(f"Attribut class interdit dans <{tag}>; utilisez des attributs SVG explicites.")
        if URL_PATTERN.search(value):
            errors.append(f"Référence url(...) interdite dans <{tag}>.")

    if tag in GRAPHIC_TAGS:
        visible = effective.get("display") != "none" and effective.get("visibility") != "hidden"
        if visible:
            fill = effective.get("fill", DEFAULT_STYLE["fill"])
            stroke = effective.get("stroke", DEFAULT_STYLE["stroke"])

            if tag in FILLED_TAGS:
                if "fill" not in direct and inherited.get("fill") == DEFAULT_STYLE["fill"]:
                    errors.append(f"<{tag}> utilise le remplissage noir SVG implicite; déclarez fill explicitement.")
                fill_color = color_value(fill, f"fill de <{tag}>", errors, set(profile["allowed_colors"]))
                if fill_color:
                    colors.add(fill_color)

            stroke_color = color_value(stroke, f"stroke de <{tag}>", errors, set(profile["allowed_colors"]))
            if stroke_color:
                colors.add(stroke_color)
                width = effective.get("stroke-width", DEFAULT_STYLE["stroke-width"])
                try:
                    width_value = float(width)
                except ValueError:
                    width_value = float("nan")
                if not any(abs(width_value - expected) <= 1e-9 for expected in profile["stroke_widths"]):
                    expected = ", ".join(f"{value:g}" for value in profile["stroke_widths"])
                    errors.append(f"stroke-width non conforme dans <{tag}>: {width}; attendu: {expected}.")
                expected_cap = profile["stroke_linecap"]
                if effective.get("stroke-linecap") != expected_cap:
                    errors.append(f"stroke-linecap non conforme dans <{tag}>; attendu: {expected_cap}.")
                # Une balise line ne possède pas de jonction ; stroke-linejoin
                # ne s'applique qu'aux formes composées de plusieurs segments.
                if tag != "line":
                    expected_join = profile["stroke_linejoin"]
                    if effective.get("stroke-linejoin") != expected_join:
                        errors.append(f"stroke-linejoin non conforme dans <{tag}>; attendu: {expected_join}.")

    for child in element:
        walk_elements(child, effective, errors, colors, profile)


def rendered_bounds(path: Path) -> tuple[tuple[float, float, float, float] | None, str | None]:
    inkscape = shutil.which("inkscape")
    if not inkscape:
        return None, "Inkscape est requis pour vérifier la zone utile stricte."
    process = subprocess.run(
        [inkscape, str(path), "--query-all"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if process.returncode != 0:
        detail = process.stderr.strip() or "échec sans message"
        return None, f"Échec du calcul d’emprise avec Inkscape: {detail}"

    boxes: list[tuple[float, float, float, float]] = []
    for line in process.stdout.splitlines():
        parts = line.rsplit(",", 4)
        if len(parts) != 5:
            continue
        try:
            x, y, width, height = map(float, parts[1:])
        except ValueError:
            continue
        if width > 0 and height > 0:
            boxes.append((x, y, x + width, y + height))

    if not boxes:
        return None, "Aucune forme visible détectée par Inkscape."
    return (
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    ), None


def validate_file(path: Path, profile: dict, xml_only: bool = False) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    colors: set[str] = set()
    bounds: tuple[float, float, float, float] | None = None

    try:
        raw = path.read_bytes()
    except OSError as exc:
        return {"file": str(path), "valid": False, "errors": [f"Lecture impossible: {exc}"], "warnings": []}

    upper_raw = raw.upper()
    if b"<!DOCTYPE" in upper_raw or b"<!ENTITY" in upper_raw:
        errors.append("DOCTYPE et ENTITY sont interdits.")

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        return {"file": str(path), "valid": False, "errors": [f"XML invalide: {exc}"], "warnings": []}

    if local_name(root.tag) != "svg":
        errors.append("L’élément racine doit être <svg>.")
    expected_view_box = profile["view_box"].split()
    if root.attrib.get("viewBox", "").split() != expected_view_box:
        errors.append(f'Le viewBox doit être exactement "{profile["view_box"]}".')

    walk_elements(root, DEFAULT_STYLE, errors, colors, profile)

    max_colors = profile["max_colors"]
    if len(colors) > max_colors:
        errors.append(f"Maximum {max_colors} couleurs visibles; {len(colors)} détectées.")
    for required_color in profile["required_colors"]:
        if required_color not in colors:
            warnings.append(f"La couleur principale {required_color} n’a pas été détectée.")

    if xml_only:
        warnings.append("Contrôle d’emprise ignoré (--xml-only).")
    else:
        bounds, bound_error = rendered_bounds(path)
        if bound_error:
            errors.append(bound_error)
        elif bounds:
            x_min, y_min, x_max, y_max = bounds
            safe_min = profile["safe_min"]
            safe_max = profile["safe_max"]
            if x_min < safe_min - BOUND_TOLERANCE or y_min < profile["safe_y_min"] - BOUND_TOLERANCE:
                errors.append(f"Emprise hors zone utile en haut/gauche: ({x_min:.2f}, {y_min:.2f}); minimum: {safe_min:.2f}.")
            if x_max > safe_max + BOUND_TOLERANCE or y_max > profile["safe_y_max"] + BOUND_TOLERANCE:
                errors.append(f"Emprise hors zone utile en bas/droite: ({x_max:.2f}, {y_max:.2f}); maximum: {safe_max:.2f}.")

    report = {
        "file": str(path),
        "valid": not errors,
        "colors": sorted(colors),
        "errors": errors,
        "warnings": warnings,
    }
    if bounds:
        report["bounds"] = [round(value, 3) for value in bounds]
    return report


def svg_files(target: Path) -> list[Path]:
    return [target] if target.is_file() else sorted(target.rglob("*.svg"))


def validate_collection(target: Path, requests_path: Path | None) -> list[str]:
    if requests_path is None:
        return []
    if not target.is_dir():
        return ["--requests nécessite un dossier de sortie comme cible."]
    try:
        data = json.loads(requests_path.read_text(encoding="utf-8"))
        expected_ids = [item["id"] for item in data["requests"]]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        return [f"Fichier de requêtes invalide: {exc}"]

    expected = {f"{item_id}.svg" for item_id in expected_ids}
    found = {str(path.relative_to(target).as_posix()) for path in target.rglob("*.svg")}
    errors: list[str] = []
    missing = sorted(expected - found)
    extra = sorted(found - expected)
    if len(expected_ids) != len(set(expected_ids)):
        errors.append("Le fichier de requêtes contient des id dupliqués.")
    if missing:
        errors.append(f"SVG manquants: {', '.join(missing)}.")
    if extra:
        errors.append(f"SVG supplémentaires ou mal placés: {', '.join(extra)}.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Fichier SVG ou dossier à valider")
    parser.add_argument("--requests", type=Path, help="JSON des requêtes pour vérifier noms et cardinalité")
    parser.add_argument("--profile", type=Path, help="Profil JSON confidentiel des contraintes déterministes")
    parser.add_argument("--xml-only", action="store_true", help="Ignorer le contrôle d’emprise Inkscape")
    parser.add_argument("--json", action="store_true", help="Afficher un rapport JSON")
    args = parser.parse_args()

    try:
        profile = load_profile(args.profile)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"Profil de validation invalide: {exc}", file=sys.stderr)
        return 2

    files = svg_files(args.target)
    if not files:
        print("Aucun fichier SVG trouvé.", file=sys.stderr)
        return 2

    reports = [validate_file(path, profile, xml_only=args.xml_only) for path in files]
    collection_errors = validate_collection(args.target, args.requests)
    valid = all(report["valid"] for report in reports) and not collection_errors

    if args.json:
        print(json.dumps({"valid": valid, "profile": profile["name"], "files": reports, "collection_errors": collection_errors}, ensure_ascii=False, indent=2))
    else:
        for report in reports:
            print(f"[{'OK' if report['valid'] else 'ECHEC'}] {report['file']}")
            if "bounds" in report:
                print(f"  emprise: {report['bounds']}")
            for message in report["errors"]:
                print(f"  erreur: {message}")
            for message in report["warnings"]:
                print(f"  avertissement: {message}")
        for message in collection_errors:
            print(f"[COLLECTION] {message}")

    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
