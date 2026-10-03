from __future__ import annotations

import csv
import tempfile
import threading
import unittest
from pathlib import Path

from omnievo.lab.client import LabClient
from omnievo.lab.oracle import PrivateOracle
from omnievo.lab.server import create_server
from omnievo.lab.state import LabState
from omnievo.space import theoretical_sequences


class VirtualLabIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        oracle_path = root / "private.csv"
        self.valid = list(theoretical_sequences()[:120])
        with oracle_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["sequence", "fitness"])
            writer.writeheader()
            for index, sequence in enumerate(self.valid):
                writer.writerow({"sequence": sequence, "fitness": index / 10.0})
        oracle = PrivateOracle.from_csv(oracle_path)
        self.state = LabState(root / "state.sqlite3", root / "private-ledger.jsonl")
        self.server = create_server("127.0.0.1", 0, oracle, self.state, "test-token")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.client = LabClient(f"http://127.0.0.1:{self.server.server_port}", "test-token")

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temporary.cleanup()

    @staticmethod
    def proposals(sequences, action="RANDOM_SAMPLE"):
        return [
            {"sequence": sequence, "source_action": action, "proposal_agent": "test"}
            for sequence in sequences
        ]

    def test_unavailable_and_duplicate_do_not_consume_budget(self):
        self.client.create_run("run-a", "random", 1)
        requested = ["YYYY", self.valid[0], self.valid[0], *self.valid[1:25]]
        result = self.client.measure_batch("run-a", 1, self.proposals(requested), "batch-1")
        self.assertEqual(len(result["measurements"]), 24)
        self.assertEqual(result["status"]["successful_assays"], 24)
        self.assertEqual(
            {item["status"] for item in result["rejections"]},
            {"UNAVAILABLE", "DUPLICATE_IN_REQUEST"},
        )

    def test_round_order_and_total_budget_survive_reopen(self):
        self.client.create_run("run-b", "fixed_mixture", 2)
        with self.assertRaises(Exception):
            self.client.measure_batch("run-b", 2, self.proposals(self.valid[:24]), "too-early")
        for round_number in range(1, 5):
            start = (round_number - 1) * 24
            result = self.client.measure_batch(
                "run-b",
                round_number,
                self.proposals(self.valid[start : start + 24]),
                f"batch-{round_number}",
            )
            self.assertEqual(len(result["measurements"]), 24)
        self.assertEqual(self.client.status("run-b")["successful_assays"], 96)
        self.assertEqual(self.client.status("run-b")["status"], "COMPLETE")
        reopened = LabState(self.state.database_path, self.state.ledger_path)
        self.assertEqual(reopened.status("run-b")["remaining_budget"], 0)
        with self.assertRaises(Exception):
            self.client.measure_batch("run-b", 4, self.proposals([self.valid[119]]), "overflow")

    def test_runs_are_isolated(self):
        self.client.create_run("run-c", "random", 3)
        self.client.create_run("run-d", "random", 3)
        self.client.measure_batch("run-c", 1, self.proposals(self.valid[:24]), "c1")
        self.client.measure_batch("run-d", 1, self.proposals(self.valid[:24]), "d1")
        self.assertEqual(len(self.client.observations("run-c")), 24)
        self.assertEqual(len(self.client.observations("run-d")), 24)


if __name__ == "__main__":
    unittest.main()

