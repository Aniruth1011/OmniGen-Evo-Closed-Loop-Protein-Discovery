"""Allowed sequence-space operations that never access the hidden oracle."""

from __future__ import annotations

import hashlib
import itertools
from functools import lru_cache
from typing import Iterable, Sequence

from .constants import AMINO_ACIDS, SEQUENCE_LENGTH
from .errors import ProtocolError


def validate_sequence(sequence: str) -> str:
    sequence = str(sequence).strip().upper()
    if len(sequence) != SEQUENCE_LENGTH:
        raise ProtocolError(f"sequence must contain exactly {SEQUENCE_LENGTH} residues")
    invalid = sorted(set(sequence).difference(AMINO_ACIDS))
    if invalid:
        raise ProtocolError(f"sequence contains residues outside the allowed alphabet: {invalid}")
    return sequence


@lru_cache(maxsize=1)
def theoretical_sequences() -> tuple[str, ...]:
    """Enumerate allowed theoretical variants without revealing availability."""
    return tuple("".join(parts) for parts in itertools.product(AMINO_ACIDS, repeat=SEQUENCE_LENGTH))


def hamming(left: str, right: str) -> int:
    left, right = validate_sequence(left), validate_sequence(right)
    return sum(a != b for a, b in zip(left, right))


def hamming_neighbors(sequence: str, radius: int = 1) -> list[str]:
    sequence = validate_sequence(sequence)
    if radius != 1:
        raise ProtocolError("the primary protocol permits only Hamming-distance-1 local search")
    result: list[str] = []
    for position, original in enumerate(sequence):
        for residue in AMINO_ACIDS:
            if residue != original:
                result.append(sequence[:position] + residue + sequence[position + 1 :])
    return result


def seeded_tie_key(sequence: str, seed: int) -> str:
    return hashlib.sha256(f"{seed}:{sequence}".encode("ascii")).hexdigest()


def assert_unique_unmeasured(sequences: Sequence[str], measured: Iterable[str]) -> None:
    normalized = [validate_sequence(item) for item in sequences]
    if len(normalized) != len(set(normalized)):
        raise ProtocolError("candidate batch contains duplicate sequences")
    overlap = set(normalized).intersection(validate_sequence(item) for item in measured)
    if overlap:
        raise ProtocolError(f"candidate batch repeats measured sequences: {sorted(overlap)[:5]}")

