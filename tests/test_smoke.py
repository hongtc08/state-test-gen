"""Kiểm thử cơ bản (smoke test) cho cấu trúc repo, SUT và Mutation Testing."""

import unittest
from pathlib import Path

from src.mutation import (
    generate_all_mutants,
    mutation_score,
    mutate_add_transition,
    mutate_change_event,
    mutate_change_target,
    mutate_delete_transition,
)
from src.sut import SUT, load_model


class TestRepoAndMutation(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parent.parent
        self.model = load_model(self.root / "models" / "login_mini.json")

    def test_repo_structure_exists(self) -> None:
        expected_paths = [
            self.root / "README.md",
            self.root / "decisions.md",
            self.root / "requirements.txt",
            self.root / "src" / "env.py",
            self.root / "src" / "sut.py",
            self.root / "src" / "mutation.py",
            self.root / "src" / "run.py",
            self.root / "src" / "algos" / "qlearn.py",
            self.root / "src" / "algos" / "ga.py",
            self.root / "src" / "algos" / "random_walk.py",
            self.root / "src" / "algos" / "q_ga.py",
            self.root / "models" / "login_mini.json",
            self.root / "results",
            self.root / "analysis" / "stats_demo.py",
            self.root / "paper" / "references.bib",
            self.root / "paper" / "glossary.md",
        ]
        for path in expected_paths:
            self.assertTrue(path.exists(), f"Thiếu đường dẫn bắt buộc trong repo: {path}")

    def test_sut_execute_valid_and_invalid(self) -> None:
        sut = SUT(self.model)
        trace = sut.execute(["input_user", "pass_bad", "unknown_evt", "pass_ok"])
        self.assertEqual(trace, ["Start", "EnterPass", "Fail1", "INVALID", "LoggedIn"])

    def test_mutation_operators_and_score(self) -> None:
        self.assertGreater(len(mutate_change_target(self.model)), 0)
        self.assertEqual(len(mutate_delete_transition(self.model)), len(self.model["transitions"]))
        self.assertGreater(len(mutate_change_event(self.model)), 0)
        self.assertGreater(len(mutate_add_transition(self.model)), 0)

        all_mutants = generate_all_mutants(self.model)
        self.assertEqual(mutation_score(self.model, all_mutants, []), 0.0)

        # Bộ test phủ toàn bộ transition hợp lệ + mọi sự kiện không hợp lệ tại mọi trạng thái
        all_events = sorted({t["event"] for t in self.model["transitions"]})
        prefixes = {
            "Start": [],
            "EnterPass": ["input_user"],
            "LoggedIn": ["input_user", "pass_ok"],
            "Fail1": ["input_user", "pass_bad"],
            "Fail2": ["input_user", "pass_bad", "pass_bad"],
            "Locked": ["input_user", "pass_bad", "pass_bad", "pass_bad"],
        }
        exhaustive_suite = [prefix + [evt] for prefix in prefixes.values() for evt in all_events]
        self.assertEqual(mutation_score(self.model, all_mutants, exhaustive_suite), 100.0)


if __name__ == "__main__":
    unittest.main()
