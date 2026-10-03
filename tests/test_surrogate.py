from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from omnievo.space import theoretical_sequences
from omnievo.surrogate import fit_and_score, load_score_records


class SurrogateTests(unittest.TestCase):
    def test_scores_theoretical_space_without_oracle_labels(self):
        observations = [
            {"sequence": sequence, "fitness": float(index % 7)}
            for index, sequence in enumerate(theoretical_sequences()[:24])
        ]
        with tempfile.TemporaryDirectory() as directory:
            report = fit_and_score(
                observations,
                Path(directory),
                "fixture",
                2,
                17,
                n_estimators=8,
            )
            records = load_score_records(report["artifacts"]["candidate_scores"])
        self.assertEqual(report["train_n"], 24)
        self.assertEqual(len(records), 160_000)
        self.assertEqual(set(records[0]), {"sequence", "predicted_fitness", "uncertainty"})


if __name__ == "__main__":
    unittest.main()
