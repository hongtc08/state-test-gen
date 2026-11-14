"""[N4] Sinh mutant từ máy trạng thái (4 toán tử đột biến) và tính Mutation Score."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

try:
    from src.sut import SUT, load_model
except ImportError:
    from sut import SUT, load_model


def _make_mutant(
    model: dict[str, Any],
    operator: str,
    desc: str,
    transitions: list[dict[str, str]],
) -> dict[str, Any]:
    """Tạo bản sao mô hình FSM với danh sách transitions đã bị đột biến."""
    mutant = copy.deepcopy(model)
    mutant["transitions"] = transitions
    mutant["mutant_operator"] = operator
    mutant["mutant_desc"] = desc
    return mutant


def mutate_change_target(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Toán tử 1: Đổi trạng thái đích `to` của từng transition sang các trạng thái khác."""
    mutants: list[dict[str, Any]] = []
    states: list[str] = model["states"]
    orig_trans = model["transitions"]

    for i, t in enumerate(orig_trans):
        for new_to in states:
            if new_to == t["to"]:
                continue
            new_trans = copy.deepcopy(orig_trans)
            new_trans[i]["to"] = new_to
            desc = f"({t['from']}, {t['event']}): {t['to']} -> {new_to}"
            mutants.append(_make_mutant(model, "change_target", desc, new_trans))
    return mutants


def mutate_delete_transition(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Toán tử 2: Xóa từng transition khỏi mô hình."""
    mutants: list[dict[str, Any]] = []
    orig_trans = model["transitions"]

    for i, t in enumerate(orig_trans):
        new_trans = [copy.deepcopy(x) for j, x in enumerate(orig_trans) if j != i]
        desc = f"delete ({t['from']}, {t['event']} -> {t['to']})"
        mutants.append(_make_mutant(model, "delete_transition", desc, new_trans))
    return mutants


def mutate_change_event(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Toán tử 3: Đổi sự kiện kích hoạt sang sự kiện khác chưa dùng tại trạng thái nguồn."""
    mutants: list[dict[str, Any]] = []
    orig_trans = model["transitions"]
    all_events = sorted({t["event"] for t in orig_trans})
    defined_pairs = {(t["from"], t["event"]) for t in orig_trans}

    for i, t in enumerate(orig_trans):
        for new_event in all_events:
            if new_event == t["event"] or (t["from"], new_event) in defined_pairs:
                continue
            new_trans = copy.deepcopy(orig_trans)
            new_trans[i]["event"] = new_event
            desc = f"({t['from']}, {t['event']} -> {new_event}) -> {t['to']}"
            mutants.append(_make_mutant(model, "change_event", desc, new_trans))
    return mutants


def mutate_add_transition(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Toán tử 4: Thêm transition không hợp lệ dẫn về `initial` tại các cặp chưa có cạnh."""
    mutants: list[dict[str, Any]] = []
    orig_trans = model["transitions"]
    all_events = sorted({t["event"] for t in orig_trans})
    defined_pairs = {(t["from"], t["event"]) for t in orig_trans}
    target = model["initial"]

    for state in model["states"]:
        for event in all_events:
            if (state, event) in defined_pairs:
                continue
            new_trans = copy.deepcopy(orig_trans)
            new_trans.append({"from": state, "event": event, "to": target})
            desc = f"add ({state}, {event} -> {target})"
            mutants.append(_make_mutant(model, "add_transition", desc, new_trans))
    return mutants


def generate_all_mutants(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Sinh toàn bộ danh sách mutant từ cả 4 toán tử đột biến."""
    return (
        mutate_change_target(model)
        + mutate_delete_transition(model)
        + mutate_change_event(model)
        + mutate_add_transition(model)
    )


def is_killed(
    original_model: dict[str, Any],
    mutant_model: dict[str, Any],
    test_suite: list[list[str]],
) -> bool:
    """Trả về True nếu ít nhất 1 test case cho trace khác nhau giữa bản gốc và mutant."""
    orig_sut = SUT(original_model)
    mut_sut = SUT(mutant_model)
    return any(orig_sut.execute(tc) != mut_sut.execute(tc) for tc in test_suite)


def mutation_score(
    original_model: dict[str, Any],
    mutants: list[dict[str, Any]],
    test_suite: list[list[str]],
    as_percentage: bool = True,
) -> float:
    """Tính tỷ lệ mutant bị giết bởi test_suite (mặc định thang 0.0 - 100.0)."""
    if not mutants:
        return 0.0
    killed = sum(1 for m in mutants if is_killed(original_model, m, test_suite))
    ratio = killed / len(mutants)
    return ratio * 100.0 if as_percentage else ratio


def main() -> None:
    """Chạy demo nhanh trên models/login_mini.json để minh họa cách Mutation Score tăng."""
    root = Path(__file__).resolve().parent.parent
    model = load_model(root / "models" / "login_mini.json")
    mutants = generate_all_mutants(model)

    counts: dict[str, int] = {}
    for m in mutants:
        op = m["mutant_operator"]
        counts[op] = counts.get(op, 0) + 1

    suite_empty: list[list[str]] = []
    suite_happy_only = [["input_user", "pass_ok", "logout"]]
    suite_positive_full = [
        ["input_user", "pass_ok", "logout"],
        ["input_user", "pass_bad", "pass_ok", "logout"],
        ["input_user", "pass_bad", "pass_bad", "pass_ok"],
        ["input_user", "pass_bad", "pass_bad", "pass_bad"],
    ]

    print(f"Mo hinh: {model['name']} ({len(model['states'])} states, {len(model['transitions'])} transitions)")
    print(f"Tong so mutant sinh ra: {len(mutants)} -> {counts}")

    for label, suite in [
        ("1. Suite rong (0 test)", suite_empty),
        ("2. Happy path (1 test)", suite_happy_only),
        ("3. Du nhanh hop le (4 tests)", suite_positive_full),
    ]:
        score = mutation_score(model, mutants, suite)
        killed = sum(1 for m in mutants if is_killed(model, m, suite))
        print(f"  {label:<30} | Killed: {killed:>2}/{len(mutants)} | Mutation Score: {score:6.2f}%")


if __name__ == "__main__":
    main()
