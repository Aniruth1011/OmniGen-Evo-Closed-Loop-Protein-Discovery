"""Private CSV oracle. Import this module only in the isolated lab process."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

from ..errors import OracleIntegrityError
from ..space import validate_sequence


@dataclass(frozen=True)
class OracleAudit:
    row_count: int
    checksum_sha256: str
    sequence_column: str
    fitness_column: str


class PrivateOracle:
    """In-memory lookup used only behind the virtual-lab service boundary."""

    def __init__(self, values: dict[str, float], audit: OracleAudit):
        self._values = values
        self.audit = audit

    @classmethod
    def from_csv(
        cls,
        path: str | Path,
        sequence_column: str = "sequence",
        fitness_column: str = "fitness",
    ) -> "PrivateOracle":
        source = Path(path).expanduser().resolve(strict=True)
        checksum = hashlib.sha256(source.read_bytes()).hexdigest()
        values: dict[str, float] = {}
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise OracleIntegrityError("oracle CSV has no header")
            missing = {sequence_column, fitness_column}.difference(reader.fieldnames)
            if missing:
                raise OracleIntegrityError(f"oracle CSV is missing columns: {sorted(missing)}")
            for row_number, row in enumerate(reader, start=2):
                try:
                    sequence = validate_sequence(row[sequence_column])
                    fitness = float(row[fitness_column])
                except (TypeError, ValueError) as exc:
                    raise OracleIntegrityError(f"invalid oracle row {row_number}") from exc
                if sequence in values:
                    raise OracleIntegrityError(f"duplicate oracle sequence at row {row_number}")
                values[sequence] = fitness
        if not values:
            raise OracleIntegrityError("oracle CSV contains no measurements")
        return cls(
            values,
            OracleAudit(len(values), checksum, sequence_column, fitness_column),
        )

    def lookup(self, sequence: str) -> float | None:
        return self._values.get(validate_sequence(sequence))

