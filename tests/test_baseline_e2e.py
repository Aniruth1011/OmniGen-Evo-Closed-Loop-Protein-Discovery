from __future__ import annotations

import csv
import tempfile
import threading
import unittest
from pathlib import Path

from omnievo.baselines import run_baseline
from omnievo.constants import AMINO_ACIDS
from omnievo.lab.client import LabClient
from omnievo.lab.oracle import PrivateOracle
from omnievo.lab.server import create_server
from omnievo.lab.state import LabState
from omnievo.space import theoretical_sequences


class BaselineEndToEndTest(unittest.TestCase):
    def test_fixed_mixture_completes_four_rounds_on_temporary_fixture(self):
        """Engineering fixture only: these values are not GB1 scientific evidence."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            oracle_path = root / "synthetic-engineering-fixture.csv"
            index = {residue: value for value, residue in enumerate(AMINO_ACIDS)}
            with oracle_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["sequence", "fitness"])
                writer.writeheader()
                for sequence in theoretical_sequences():
                    additive = sum(index[residue] for residue in sequence) / 20.0
                    interaction = 1.5 if sequence[0] == sequence[3] else 0.0
                    writer.writerow({"sequence": sequence, "fitness": additive + interaction})
            oracle = PrivateOracle.from_csv(oracle_path)
            state = LabState(root / "lab.sqlite3", root / "private-ledger.jsonl")
            server = create_server("127.0.0.1", 0, oracle, state, "fixture-token")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                client = LabClient(f"http://127.0.0.1:{server.server_port}", "fixture-token")
                result = run_baseline(
                    client,
                    "fixed_mixture",
                    5,
                    root / "runs",
                    candidate_pool_size=64,
                    surrogate_n_estimators=8,
                )
                self.assertEqual(result["status"]["successful_assays"], 96)
                self.assertEqual(result["status"]["status"], "COMPLETE")
                self.assertEqual(len(client.observations(result["run_id"])), 96)
                self.assertTrue((root / "runs/fixed_mixture/seed_005/round_04/critic_report.yaml").exists() is False)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
