from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from omnievo.dataset import prepare_proteingym_gb1
from omnievo.lab.oracle import PrivateOracle


class DatasetPreparationTests(unittest.TestCase):
    def test_prepares_four_site_private_oracle(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "protein_gym.csv"
            destination = root / "oracle.csv"
            full = ["A"] * 448
            for position, residue in zip((265, 266, 267, 280), "ADGV"):
                full[position - 1] = residue
            with source.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["mutant", "mutated_sequence", "DMS_score", "DMS_score_bin"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "mutant": "V265A",
                        "mutated_sequence": "".join(full),
                        "DMS_score": "0.5",
                        "DMS_score_bin": "1",
                    }
                )
            with patch("omnievo.dataset.EXPECTED_PROTEINGYM_ROWS", 1):
                audit = prepare_proteingym_gb1(source, destination)
            oracle = PrivateOracle.from_csv(destination)
            self.assertEqual(oracle.lookup("ADGV"), 0.5)
            self.assertEqual(audit["measured_mutant_rows"], 1)
            self.assertFalse(audit["wild_type_in_oracle"])
            self.assertTrue(destination.with_suffix(".csv.audit.json").exists())


if __name__ == "__main__":
    unittest.main()
