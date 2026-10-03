"""Public virtual-lab client. It has no raw-oracle path or lookup methods."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from ..errors import LabClientError


class LabClient:
    def __init__(self, base_url: str, token: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self._token = token
        self.timeout = timeout
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("lab URL must use http or https")
        if not token:
            raise ValueError("lab token is required")

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = None if body is None else json.dumps(body).encode("utf-8")
        request = Request(
            self.base_url + path,
            data=payload,
            method=method,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise LabClientError(f"lab rejected request ({exc.code}): {detail}") from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise LabClientError(f"lab request failed: {exc}") from exc

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def create_run(self, run_id: str, strategy: str, seed: int) -> dict[str, Any]:
        return self._request("POST", "/v1/runs", {"run_id": run_id, "strategy": strategy, "seed": seed})

    def status(self, run_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/runs/{quote(run_id, safe='')}/status")

    def observations(self, run_id: str) -> list[dict[str, Any]]:
        result = self._request("GET", f"/v1/runs/{quote(run_id, safe='')}/observations")
        return result["observations"]

    def measure_batch(
        self,
        run_id: str,
        round_number: int,
        proposals: list[dict[str, Any]],
        planner_batch_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/v1/runs/{quote(run_id, safe='')}/measure",
            {"round": round_number, "proposals": proposals, "planner_batch_id": planner_batch_id},
        )
