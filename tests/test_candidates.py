from __future__ import annotations

import unittest

from omnievo.artifacts import validate_planner_decision
from omnievo.candidates import generate_local_pool, generate_random_pool, select_from_allocations
from omnievo.errors import ProtocolError


class CandidateTests(unittest.TestCase):
    def test_random_pool_is_seed_reproducible(self):
        first = generate_random_pool(["AAAA"], 30, 7)
        second = generate_random_pool(["AAAA"], 30, 7)
        self.assertEqual(first, second)
        self.assertNotIn("AAAA", {item["sequence"] for item in first})
        self.assertNotIn("VDGV", {item["sequence"] for item in first})

    def test_local_pool_uses_observed_parent_only(self):
        observations = [{"sequence": "AAAA", "fitness": 1.0}, {"sequence": "CCCC", "fitness": 0.2}]
        pool = generate_local_pool(observations, 20, 4)
        self.assertTrue(all(item["hamming_distance"] == 1 for item in pool))
        self.assertTrue(all(item["parent"] in {"AAAA", "CCCC"} for item in pool))

    def test_allocation_deduplicates_overlap(self):
        random_pool = generate_random_pool([], 80, 8)
        pools = {
            "RANDOM_SAMPLE": random_pool,
            "LOCAL_MUTATE": [
                {**item, "source_action": "LOCAL_MUTATE"} for item in random_pool[:40]
            ],
        }
        selected, _ = select_from_allocations(
            pools, {"RANDOM_SAMPLE": 12, "LOCAL_MUTATE": 12}, []
        )
        self.assertEqual(len({item["sequence"] for item in selected}), 24)

    def test_planner_requires_exact_budget(self):
        with self.assertRaises(ProtocolError):
            validate_planner_decision(
                {"budget": 24, "allocation": {"RANDOM_SAMPLE": 23}, "selected_sequences": []},
                [],
            )


if __name__ == "__main__":
    unittest.main()
