"""Auditable artifact helpers for agent handoffs and scientific state."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .constants import ACTIONS, ROUND_SIZE
from .errors import ProtocolError
from .space import assert_unique_unmeasured, validate_sequence


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def write_json(path: str | Path, value: Any) -> Path:
    destination = Path(path)
    _atomic_text(destination, json.dumps(value, indent=2, sort_keys=True) + "\n")
    return destination


def write_yaml_compatible(path: str | Path, value: Any) -> Path:
    """Write JSON, which is a strict YAML subset and needs no runtime YAML dependency."""
    return write_json(path, value)


def append_jsonl(path: str | Path, value: dict[str, Any]) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return destination


def write_csv(path: str | Path, records: Iterable[dict[str, Any]], fieldnames: list[str]) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent, text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(records)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise
    return destination


def validate_planner_decision(
    decision: dict[str, Any],
    measured_sequences: Iterable[str],
    require_selected: bool = True,
) -> dict[str, Any]:
    if int(decision.get("budget", decision.get("budget_total", -1))) != ROUND_SIZE:
        raise ProtocolError(f"planner budget must equal {ROUND_SIZE}")
    allocation = decision.get("allocation")
    if not isinstance(allocation, dict) or not allocation:
        raise ProtocolError("planner allocation is required")
    unknown = set(allocation).difference(ACTIONS)
    if unknown:
        raise ProtocolError(f"planner allocation contains unknown actions: {sorted(unknown)}")
    if any(not isinstance(value, int) or value < 0 for value in allocation.values()):
        raise ProtocolError("planner allocation values must be non-negative integers")
    if sum(allocation.values()) != ROUND_SIZE:
        raise ProtocolError(f"planner allocation must sum to {ROUND_SIZE}")
    selected = decision.get("selected_sequences", [])
    if require_selected and len(selected) != ROUND_SIZE:
        raise ProtocolError(f"planner must select exactly {ROUND_SIZE} candidates")
    if selected:
        sequences = [validate_sequence(item["sequence"]) for item in selected]
        assert_unique_unmeasured(sequences, measured_sequences)
        selected_counts: dict[str, int] = {}
        for item in selected:
            action = item.get("source_action")
            if action not in allocation:
                raise ProtocolError(f"selected candidate uses unallocated action: {action}")
            selected_counts[action] = selected_counts.get(action, 0) + 1
        for action, slots in allocation.items():
            if selected_counts.get(action, 0) != slots:
                raise ProtocolError(f"selected candidate count does not match allocation for {action}")
    return decision

