"""Authenticated HTTP boundary around the private GB1 oracle."""

from __future__ import annotations

import hmac
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import unquote, urlparse

from ..errors import OmniEvoError
from .oracle import PrivateOracle
from .state import LabState


class LabHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], oracle: PrivateOracle, state: LabState, token: str):
        if not token:
            raise ValueError("a non-empty lab bearer token is required")
        super().__init__(address, LabRequestHandler)
        self.oracle = oracle
        self.state_store = state
        self.token = token


class LabRequestHandler(BaseHTTPRequestHandler):
    server: LabHTTPServer

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _authorized(self) -> bool:
        supplied = self.headers.get("Authorization", "")
        expected = f"Bearer {self.server.token}"
        return hmac.compare_digest(supplied, expected)

    def _json_body(self) -> dict[str, Any]:
        size = int(self.headers.get("Content-Length", "0"))
        if size <= 0 or size > 2_000_000:
            raise ValueError("invalid request body size")
        value = json.loads(self.rfile.read(size).decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("request body must be a JSON object")
        return value

    def _send(self, status: HTTPStatus, body: dict[str, Any]) -> None:
        payload = json.dumps(body, sort_keys=True).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _guard(self) -> bool:
        if not self._authorized():
            self._send(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
            return False
        return True

    def do_GET(self) -> None:
        if not self._guard():
            return
        path = urlparse(self.path).path
        try:
            if path == "/health":
                self._send(HTTPStatus.OK, {"status": "ok"})
                return
            parts = path.strip("/").split("/")
            if len(parts) == 4 and parts[:2] == ["v1", "runs"] and parts[3] in {"status", "observations"}:
                run_id = unquote(parts[2])
                result = (
                    self.server.state_store.status(run_id)
                    if parts[3] == "status"
                    else {"run_id": run_id, "observations": self.server.state_store.observations(run_id)}
                )
                self._send(HTTPStatus.OK, result)
                return
            self._send(HTTPStatus.NOT_FOUND, {"error": "not found"})
        except OmniEvoError as exc:
            self._send(HTTPStatus.CONFLICT, {"error": str(exc), "error_type": type(exc).__name__})

    def do_POST(self) -> None:
        if not self._guard():
            return
        path = urlparse(self.path).path
        try:
            body = self._json_body()
            if path == "/v1/runs":
                result = self.server.state_store.create_run(body["run_id"], body["strategy"], body["seed"])
                self._send(HTTPStatus.CREATED, result)
                return
            parts = path.strip("/").split("/")
            if len(parts) == 4 and parts[:2] == ["v1", "runs"] and parts[3] == "measure":
                result = self.server.state_store.measure(
                    self.server.oracle,
                    unquote(parts[2]),
                    int(body["round"]),
                    body["proposals"],
                    str(body["planner_batch_id"]),
                )
                self._send(HTTPStatus.OK, result)
                return
            self._send(HTTPStatus.NOT_FOUND, {"error": "not found"})
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self._send(HTTPStatus.BAD_REQUEST, {"error": str(exc), "error_type": type(exc).__name__})
        except OmniEvoError as exc:
            self._send(HTTPStatus.CONFLICT, {"error": str(exc), "error_type": type(exc).__name__})


def create_server(
    host: str,
    port: int,
    oracle: PrivateOracle,
    state: LabState,
    token: str,
) -> LabHTTPServer:
    return LabHTTPServer((host, port), oracle, state, token)

