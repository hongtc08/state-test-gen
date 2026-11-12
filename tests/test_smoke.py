"""Kiểm thử cơ bản (smoke test) để đảm bảo cấu trúc hạ tầng repo hoạt động tốt."""

from pathlib import Path


def test_repo_structure_exists():
    root = Path(__file__).resolve().parent.parent
    expected_paths = [
        root / "README.md",
        root / "decisions.md",
        root / "requirements.txt",
        root / "src" / "env.py",
        root / "src" / "sut.py",
        root / "src" / "mutation.py",
        root / "src" / "run.py",
        root / "src" / "algos" / "qlearn.py",
        root / "src" / "algos" / "ga.py",
        root / "src" / "algos" / "random_walk.py",
        root / "models",
        root / "results",
        root / "analysis",
        root / "paper" / "references.bib",
        root / "paper" / "glossary.md",
    ]
    for p in expected_paths:
        assert p.exists(), f"Thiếu đường dẫn bắt buộc trong repo: {p}"
