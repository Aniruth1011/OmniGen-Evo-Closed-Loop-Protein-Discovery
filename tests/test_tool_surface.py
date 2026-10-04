from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path


class OmnigentToolSurfaceTests(unittest.TestCase):
    def test_each_registered_tool_has_a_matching_file_and_function(self):
        client = types.ModuleType("omnigent_client")
        client.tool = lambda function=None, **_kwargs: function or (lambda target: target)
        sys.modules.setdefault("omnigent_client", client)
        root = Path(__file__).parents[1] / "tools/python"
        expected = {
            "lab_status", "initialize_adaptive_run", "fit_observed_surrogate",
            "generate_all_candidate_pools", "prepare_critic_input",
            "save_hypothesis_report", "save_critic_report",
            "save_planner_decision", "record_critic_to_planner_handoff",
            "execute_planner_round",
        }
        self.assertEqual({path.stem for path in root.glob("*.py")}, expected)
        for name in expected:
            path = root / f"{name}.py"
            spec = importlib.util.spec_from_file_location(f"omnievo_tool_{name}", path)
            module = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(module)
            self.assertTrue(callable(getattr(module, name)))
            self.assertNotIn("execute_source_preserving_allocation", vars(module))
            self.assertNotIn("fit_and_score", vars(module))


if __name__ == "__main__":
    unittest.main()
