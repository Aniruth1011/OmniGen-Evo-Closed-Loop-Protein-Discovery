#!/usr/bin/env python3
"""Materialize short-lived Databricks auth only inside a temporary agent image."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: materialize_runtime_auth.py AGENT_IMAGE")
    root = Path(sys.argv[1]).resolve()
    if not (root / "config.yaml").is_file() or not (root / "agents").is_dir():
        raise SystemExit("target is not a staged OmniEvo agent image")
    token = os.environ.get("OMNIEVO_DATABRICKS_TOKEN", "")
    base_url = os.environ.get("OMNIEVO_DATABRICKS_BASE_URL", "")
    specialist_model = os.environ.get("OMNIEVO_SPECIALIST_MODEL", "").strip()
    if not token or not base_url:
        raise SystemExit("short-lived Databricks runtime auth is unavailable")

    # Root placeholders can be safely resolved in the ephemeral copy.
    root_config = root / "config.yaml"
    text = root_config.read_text(encoding="utf-8")
    text = text.replace("${OMNIEVO_DATABRICKS_TOKEN}", token)
    text = text.replace("${OMNIEVO_DATABRICKS_BASE_URL}", base_url)
    root_config.write_text(text, encoding="utf-8")

    # Omnigent 0.16 does not expand auth placeholders in nested agent specs.
    # Inject explicit auth after the model line in the temporary image only.
    auth = (
        "  auth:\n"
        "    type: api_key\n"
        f"    api_key: {json.dumps(token)}\n"
        f"    base_url: {json.dumps(base_url)}\n"
    )
    for config in sorted((root / "agents").glob("*/config.yaml")):
        child = config.read_text(encoding="utf-8")
        if specialist_model:
            lines = child.splitlines(keepends=True)
            model_lines = [i for i, line in enumerate(lines) if line.startswith("  model: ")]
            if len(model_lines) != 1:
                raise SystemExit(f"expected one model declaration: {config}")
            lines[model_lines[0]] = f"  model: {specialist_model}\n"
            child = "".join(lines)
        if "\n  auth:\n" not in child:
            marker = next(
                (line for line in child.splitlines(keepends=True) if line.startswith("  model: ")),
                None,
            )
            if marker is None:
                raise SystemExit(f"expected model declaration is missing: {config}")
            child = child.replace(marker, marker + auth, 1)
        config.write_text(child, encoding="utf-8")
        config.chmod(0o600)
    root_config.chmod(0o600)
    print("Materialized short-lived Databricks auth in ephemeral agent image")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
