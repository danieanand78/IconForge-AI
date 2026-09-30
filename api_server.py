#!/usr/bin/env python3
"""API HTTP locale pour connecter l'interface IconForge au pipeline Python."""

from __future__ import annotations

import json
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import generate  # noqa: E402

HOST = "127.0.0.1"
PORT = 8000


def error_response(message: str, status: int = 400) -> tuple[int, dict]:
    return status, {"error": message}


class ApiHandler(BaseHTTPRequestHandler):
    server_version = "IconForgeAPI/1.0"

    def log_message(self, format: str, *args: object) -> None:
        print(f"[api] {format % args}")

    def send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/api/v1/health":
            self.send_json(200, {"status": "ok", "service": "iconforge-api"})
            return
        self.send_json(404, {"error": "Endpoint introuvable"})

    def do_POST(self) -> None:
        if self.path != "/api/v1/generate":
            self.send_json(404, {"error": "Endpoint introuvable"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 64_000:
                raise ValueError("corps de requête vide ou trop volumineux")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            concept = str(payload.get("concept", "")).strip()
            if not concept:
                raise ValueError("le champ concept est obligatoire")
            request = {
                "id": "interface-generation",
                "concept": concept,
                "context": str(payload.get("context", "")),
                "keywords": payload.get("keywords", []),
            }
            if not isinstance(request["keywords"], list):
                request["keywords"] = []
            generate.load_env_file()
            specification, profile = generate.load_specification()
            with tempfile.TemporaryDirectory(prefix="iconforge-api-") as directory:
                output = Path(directory) / "generated.svg"
                result = generate.generate_one(
                    request,
                    specification,
                    profile,
                    output,
                    None,
                    generate.os.getenv("GEMINI_API_KEY"),
                    generate.os.getenv("GEMINI_MODEL", generate.DEFAULT_MODEL),
                )
                svg = output.read_text(encoding="utf-8")
            self.send_json(200, {
                "svg": svg,
                "concept": concept,
                "score": 100 if result["validation"]["valid"] else 0,
                "source": result["source"],
                "attempts": result.get("attempts", 1),
                "validation": result["validation"],
            })
        except json.JSONDecodeError:
            self.send_json(*error_response("JSON invalide"))
        except (OSError, RuntimeError, ValueError) as error:
            self.send_json(*error_response(str(error), 500))


def main() -> None:
    generate.load_env_file()
    server = ThreadingHTTPServer((HOST, PORT), ApiHandler)
    print(f"IconForge API disponible sur http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt de l'API IconForge")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
