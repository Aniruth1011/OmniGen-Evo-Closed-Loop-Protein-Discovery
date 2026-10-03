from __future__ import annotations

import unittest

from omnievo.evaluation import paired_contrast, summarize_observations


def observations(offset=0.0):
    return [
        {
            "assay_index_global": index,
            "round": (index - 1) // 24 + 1,
            "fitness": offset + index / 100.0,
            "source_action": "RANDOM_SAMPLE",
        }
        for index in range(1, 97)
    ]


class EvaluationTests(unittest.TestCase):
    def test_summary_has_round_endpoints(self):
        summary = summarize_observations(observations(), "adaptive", 100, "a")
        self.assertEqual(summary["best_24"], 0.24)
        self.assertEqual(summary["best_96"], 0.96)

    def test_paired_contrast_uses_shared_seeds(self):
        summaries = []
        for seed in (100, 101, 102):
            adaptive = summarize_observations(observations(1.0), "adaptive", seed, f"a{seed}")
            fixed = summarize_observations(observations(), "fixed_mixture", seed, f"f{seed}")
            summaries.extend([adaptive, fixed])
        result = paired_contrast(summaries)
        self.assertEqual(result["n_pairs"], 3)
        self.assertAlmostEqual(result["mean_difference"], 1.0)


if __name__ == "__main__":
    unittest.main()
