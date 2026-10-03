"""Private, deterministic preparation of the ProteinGym Wu 2016 GB1 assay."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from .constants import WILD_TYPE_SEQUENCE
from .errors import OracleIntegrityError
from .space import validate_sequence


PROTEINGYM_ASSAY_ID = "SPG1_STRSG_Wu_2016"
PROTEINGYM_FULL_SEQUENCE_POSITIONS = (265, 266, 267, 280)
EXPECTED_PROTEINGYM_ROWS = 149_360
_MUTATION = re.compile(r"([A-Z])(\d+)([A-Z])")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare_proteingym_gb1(source: str | Path, destination: str | Path) -> dict[str, Any]:
    """Convert the official ProteinGym assay to the lab's private four-site format.

    This steward-only function deliberately reports structural integrity metadata, not
    fitness distribution summaries, optima, rankings, or individual measurements.
    """
    source_path = Path(source).expanduser().resolve(strict=True)
    destination_path = Path(destination).expanduser().resolve()
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    if source_path == destination_path:
        raise OracleIntegrityError("source and destination must be different files")

    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    with source_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"mutant", "mutated_sequence", "DMS_score"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise OracleIntegrityError(
                f"ProteinGym source is missing columns: {sorted(required.difference(reader.fieldnames or []))}"
            )
        for row_number, row in enumerate(reader, start=2):
            full_sequence = row["mutated_sequence"].strip().upper()
            if len(full_sequence) < max(PROTEINGYM_FULL_SEQUENCE_POSITIONS):
                raise OracleIntegrityError(f"full sequence is too short at row {row_number}")
            sequence = validate_sequence(
                "".join(full_sequence[position - 1] for position in PROTEINGYM_FULL_SEQUENCE_POSITIONS)
            )
            if sequence == WILD_TYPE_SEQUENCE:
                raise OracleIntegrityError("ProteinGym mutant table unexpectedly contains wild type")
            if sequence in seen:
                raise OracleIntegrityError(f"duplicate four-site sequence at row {row_number}")

            mutations: dict[int, tuple[str, str]] = {}
            for token in row["mutant"].split(":"):
                match = _MUTATION.fullmatch(token)
                if not match:
                    raise OracleIntegrityError(f"malformed mutation at row {row_number}")
                position = int(match.group(2))
                if position not in PROTEINGYM_FULL_SEQUENCE_POSITIONS:
                    raise OracleIntegrityError(f"unexpected mutated position at row {row_number}")
                mutations[position] = (match.group(1), match.group(3))
            expected_mutations = {
                position
                for position, residue, wild_type in zip(
                    PROTEINGYM_FULL_SEQUENCE_POSITIONS, sequence, WILD_TYPE_SEQUENCE
                )
                if residue != wild_type
            }
            if set(mutations) != expected_mutations:
                raise OracleIntegrityError(f"mutation label/sequence mismatch at row {row_number}")
            for position, (before, after) in mutations.items():
                index = PROTEINGYM_FULL_SEQUENCE_POSITIONS.index(position)
                if before != WILD_TYPE_SEQUENCE[index] or after != sequence[index]:
                    raise OracleIntegrityError(f"mutation residue mismatch at row {row_number}")

            score_text = row["DMS_score"].strip()
            try:
                score = float(score_text)
            except ValueError as exc:
                raise OracleIntegrityError(f"nonnumeric DMS score at row {row_number}") from exc
            if not math.isfinite(score):
                raise OracleIntegrityError(f"non-finite DMS score at row {row_number}")
            seen.add(sequence)
            rows.append((sequence, score_text))

    if len(rows) != EXPECTED_PROTEINGYM_ROWS:
        raise OracleIntegrityError(
            f"expected {EXPECTED_PROTEINGYM_ROWS} ProteinGym rows, found {len(rows)}"
        )

    descriptor = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        prefix=f".{destination_path.name}.",
        suffix=".tmp",
        dir=destination_path.parent,
        delete=False,
    )
    temporary_path = Path(descriptor.name)
    try:
        with descriptor:
            writer = csv.writer(descriptor, lineterminator="\n")
            writer.writerow(["sequence", "fitness"])
            writer.writerows(rows)
            descriptor.flush()
            os.fsync(descriptor.fileno())
        os.replace(temporary_path, destination_path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise

    audit = {
        "assay_id": PROTEINGYM_ASSAY_ID,
        "source_sha256": _sha256(source_path),
        "oracle_sha256": _sha256(destination_path),
        "measured_mutant_rows": len(rows),
        "unique_four_site_sequences": len(seen),
        "theoretical_sequence_count": 20**4,
        "unavailable_or_prior_known_count": 20**4 - len(seen),
        "full_sequence_positions": list(PROTEINGYM_FULL_SEQUENCE_POSITIONS),
        "gb1_domain_positions": [39, 40, 41, 54],
        "wild_type_sequence": WILD_TYPE_SEQUENCE,
        "wild_type_in_oracle": False,
        "wild_type_role": "public prior; excluded from paid assay candidates",
        "columns": {"sequence": "sequence", "fitness": "fitness"},
    }
    manifest_path = destination_path.with_suffix(destination_path.suffix + ".audit.json")
    manifest_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {**audit, "oracle_path": str(destination_path), "audit_path": str(manifest_path)}
