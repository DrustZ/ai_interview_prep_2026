#!/usr/bin/env python3
"""Serve the local interview index without third-party dependencies."""

from __future__ import annotations

import argparse
import contextlib
import http.server
import os
import socket
import threading
import urllib.parse
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PREP_ROOT = ROOT.parent / "my_interview_prep"


class LocalHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        # Chrome probes this optional DevTools metadata path on localhost.
        # It is unrelated to the course site, so return an empty success
        # instead of printing a misleading 404 in the user's terminal.
        if urllib.parse.urlparse(self.path).path in {
            "/.well-known/appspecific/com.chrome.devtools.json",
            "/favicon.ico",
        }:
            self.send_response(204)
            self.end_headers()
            return
        super().do_GET()

    def translate_path(self, path: str) -> str:
        request_path = urllib.parse.unquote(urllib.parse.urlparse(path).path)
        if request_path.startswith("/prep/"):
            relative_path = request_path.removeprefix("/prep/").lstrip("/")
            candidate = (PREP_ROOT / relative_path).resolve()
            try:
                candidate.relative_to(PREP_ROOT.resolve())
            except ValueError:
                return str(ROOT / "__not_found__")
            return str(candidate)
        return super().translate_path(path)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def log_message(self, format: str, *args: object) -> None:
        print(f"[local] {self.address_string()} - {format % args}")


def available_port(preferred: int) -> int:
    for port in range(preferred, preferred + 20):
        with contextlib.closing(socket.socket()) as probe:
            # Match ThreadingHTTPServer's reuse behavior so a recently stopped
            # instance does not make the probe skip the preferred port merely
            # because old client connections are still in TIME_WAIT.
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError("Could not find an available local port")


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the local interview question index")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true", help="Do not open a browser tab")
    args = parser.parse_args()

    os.chdir(ROOT)
    port = available_port(args.port)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), LocalHandler)
    url = f"http://127.0.0.1:{port}/"
    print(f"Local interview index: {url}")
    print("Press Ctrl+C to stop.")

    if not args.no_open:
        threading.Timer(0.35, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping local server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
