from __future__ import annotations

import importlib.util
import inspect
import unittest
from pathlib import Path


class OmnigentToolSurfaceTests(unittest.TestCase):
    def test_only_gated_public_functions_are_discoverable(self):
        path = Path(__file__).parents[1] / "tools/python/omnievo_tools.py"
        spec = importlib.util.spec_from_file_location("omnievo_tool_test", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        public_functions = {
            name
            for name, value in vars(module).items()
            if not name.startswith("_") and inspect.isfunction(value)
        }
        self.assertEqual(public_functions, set(module.__all__))
        self.assertNotIn("execute_source_preserving_allocation", public_functions)
        self.assertNotIn("fit_and_score", public_functions)


if __name__ == "__main__":
    unittest.main()
