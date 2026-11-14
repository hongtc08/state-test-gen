"""[N1] Bộ kiểm thử tự động cho lớp Environment (src/env.py) và mô hình login.json."""

from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from src.env import Environment


def _write_mini_model(tmp_path: Path) -> Path:
    """Tạo một mô hình FSM giả lập 3 trạng thái S0 -> S1 -> S2 (và quay lại S0)."""
    model = {
        "name": "mini_3states",
        "initial": "S0",
        "states": ["S0", "S1", "S2"],
        "transitions": [
            {"from": "S0", "event": "go_1", "to": "S1"},
            {"from": "S1", "event": "go_2", "to": "S2"},
            {"from": "S2", "event": "go_0", "to": "S0"},
        ],
    }
    model_path = tmp_path / "mini.json"
    model_path.write_text(json.dumps(model), encoding="utf-8")
    return model_path


def _write_branching_model(tmp_path: Path) -> Path:
    """Tạo mô hình nhỏ cho phép tạo transition-pair mới khi đi lại transition cũ."""
    model = {
        "name": "pair_test",
        "initial": "A",
        "states": ["A", "B", "C"],
        "transitions": [
            {"from": "A", "event": "e1", "to": "B"},
            {"from": "A", "event": "e2", "to": "B"},
            {"from": "B", "event": "e3", "to": "C"},
            {"from": "C", "event": "e4", "to": "A"},
        ],
    }
    model_path = tmp_path / "branching.json"
    model_path.write_text(json.dumps(model), encoding="utf-8")
    return model_path


def test_coverage_matches_manual_calculation(tmp_path: Path) -> None:
    """Kịch bản 1: Kiểm tra coverage() khớp tuyệt đối với tính toán bằng tay trên mô hình 3 trạng thái."""
    model_path = _write_mini_model(tmp_path)
    env = Environment(str(model_path), budget=10, max_steps_per_ep=10, log_interval=5)

    # Ban đầu: mới thăm S0 (1/3 states = 33.33%), 0/3 transitions, 0/3 pairs
    initial_cov = env.coverage()
    assert initial_cov["state_coverage"] == pytest.approx(33.33)
    assert initial_cov["transition_coverage"] == pytest.approx(0.0)
    assert initial_cov["transition_pair_coverage"] == pytest.approx(0.0)

    # Bước 1: S0 -> S1 (visited states: 2/3 = 66.67%, transitions: 1/3 = 33.33%, pairs: 0/3 = 0.0%)
    state_1, _, _, _ = env.step("go_1")
    assert state_1 == "S1"
    cov_1 = env.coverage()
    assert cov_1["state_coverage"] == pytest.approx(66.67)
    assert cov_1["transition_coverage"] == pytest.approx(33.33)
    assert cov_1["transition_pair_coverage"] == pytest.approx(0.0)

    # Bước 2: S1 -> S2 (states: 3/3 = 100.0%, transitions: 2/3 = 66.67%, pairs: 1/3 = 33.33%)
    state_2, _, _, _ = env.step("go_2")
    assert state_2 == "S2"
    cov_2 = env.coverage()
    assert cov_2["state_coverage"] == pytest.approx(100.0)
    assert cov_2["transition_coverage"] == pytest.approx(66.67)
    assert cov_2["transition_pair_coverage"] == pytest.approx(33.33)

    # Bước 3: S2 -> S0 (states: 3/3 = 100.0%, transitions: 3/3 = 100.0%, pairs: 2/3 = 66.67%)
    state_3, _, _, _ = env.step("go_0")
    assert state_3 == "S0"
    cov_3 = env.coverage()
    assert cov_3["state_coverage"] == pytest.approx(100.0)
    assert cov_3["transition_coverage"] == pytest.approx(100.0)
    assert cov_3["transition_pair_coverage"] == pytest.approx(66.67)

    # Bước 4: S0 -> S1 (khép kín cặp (S2->S0, S0->S1), pairs: 3/3 = 100.0%)
    state_4, _, _, _ = env.step("go_1")
    assert state_4 == "S1"
    cov_4 = env.coverage()
    assert cov_4["state_coverage"] == pytest.approx(100.0)
    assert cov_4["transition_coverage"] == pytest.approx(100.0)
    assert cov_4["transition_pair_coverage"] == pytest.approx(100.0)


def test_reward_mechanism(tmp_path: Path) -> None:
    """Kịch bản 2: Kiểm tra trả thưởng +1.0, +0.5 và -0.05 (lặp lại hoặc invalid)."""
    model_path = _write_branching_model(tmp_path)
    env = Environment(str(model_path), budget=20, max_steps_per_ep=20, log_interval=5)

    # +1.0 cho các transition mới: A -e1-> B, B -e3-> C, C -e4-> A
    _, r1, _, info1 = env.step("e1")
    assert r1 == pytest.approx(1.0)
    assert info1["is_new_transition"] is True
    assert info1["invalid"] is False

    _, r2, _, info2 = env.step("e3")
    assert r2 == pytest.approx(1.0)
    assert info2["is_new_transition"] is True
    assert info2["is_new_pair"] is True

    _, r3, _, info3 = env.step("e4")
    assert r3 == pytest.approx(1.0)
    assert info3["is_new_transition"] is True
    assert info3["is_new_pair"] is True

    # +1.0 khi mở transition mới A -e2-> B (đồng thời tạo cặp mới (C-e4->A, A-e2->B))
    _, r4, _, info4 = env.step("e2")
    assert r4 == pytest.approx(1.0)
    assert info4["is_new_transition"] is True

    # +0.5 khi đi lại transition cũ (B -e3-> C) nhưng tạo cặp mới (A-e2->B, B-e3->C)
    _, r5, _, info5 = env.step("e3")
    assert r5 == pytest.approx(0.5)
    assert info5["is_new_transition"] is False
    assert info5["is_new_pair"] is True
    assert info5["invalid"] is False

    # -0.05 khi đi lặp lại hoàn toàn: C -e4-> A (pair (B-e3->C, C-e4->A) đã thăm)
    _, r6, _, info6 = env.step("e4")
    assert r6 == pytest.approx(-0.05)
    assert info6["is_new_transition"] is False
    assert info6["is_new_pair"] is False
    assert info6["invalid"] is False

    # -0.05 khi truyền hành động không hợp lệ ở trạng thái hiện tại (A không có e3)
    prev_state = env.current_state
    next_state, r_invalid, _, info_invalid = env.step("e3")
    assert next_state == prev_state
    assert r_invalid == pytest.approx(-0.05)
    assert info_invalid["invalid"] is True
    assert info_invalid["is_new_transition"] is False
    assert info_invalid["is_new_pair"] is False


def test_budget_enforcement_and_reset_does_not_consume_steps(tmp_path: Path) -> None:
    """Kịch bản 3: reset() không tăng total_steps; chạm budget trả về done=True và không vượt budget."""
    model_path = _write_mini_model(tmp_path)
    env = Environment(str(model_path), budget=3, max_steps_per_ep=10, log_interval=2)

    for _ in range(5):
        assert env.reset() == "S0"
    assert env.total_steps == 0

    _, _, done_1, info_1 = env.step("go_1")
    assert done_1 is False
    assert info_1["total_steps"] == 1
    assert info_1["budget_exhausted"] is False

    env.reset()
    assert env.total_steps == 1

    _, _, done_2, info_2 = env.step("go_1")
    assert done_2 is False
    assert info_2["total_steps"] == 2
    assert info_2["budget_exhausted"] is False

    _, _, done_3, info_3 = env.step("go_2")
    assert done_3 is True
    assert info_3["total_steps"] == 3
    assert info_3["budget_exhausted"] is True

    # Gọi thêm step() khi đã hết budget không làm tăng total_steps
    state_extra, reward_extra, done_extra, info_extra = env.step("go_0")
    assert state_extra == "S2"
    assert reward_extra == pytest.approx(0.0)
    assert done_extra is True
    assert info_extra["total_steps"] == 3
    assert info_extra["budget_exhausted"] is True
    assert env.total_steps == 3


def test_get_test_suite_collection_on_done_and_early_reset(tmp_path: Path) -> None:
    """Kịch bản 4: Lưu test case cả khi done=True lẫn khi reset() sớm giữa chừng."""
    model_path = _write_mini_model(tmp_path)
    env = Environment(str(model_path), budget=20, max_steps_per_ep=2, log_interval=5)

    # Lượt 1: Kết thúc tự nhiên do đạt max_steps_per_ep=2 và có đóng góp nhánh mới
    _, _, done_1, _ = env.step("go_1")
    assert done_1 is False
    _, _, done_2, _ = env.step("go_2")
    assert done_2 is True

    # Lượt 2: Reset và đi lại y hệt (không đóng góp nhánh/cặp mới) -> không lưu trùng
    env.reset()
    env.step("go_1")
    env.step("go_2")

    # Lượt 3: Reset, chạy hết ep mới với budget đủ để đi tới go_0 (đóng góp transition S2->S0)
    env_early = Environment(str(model_path), budget=20, max_steps_per_ep=10, log_interval=5)
    env_early.step("go_1")
    # Chủ động gọi reset() sớm trước khi done=True
    env_early.reset()
    env_early.step("go_1")
    env_early.step("go_2")
    # Gọi get_test_suite() khi lượt chạy vẫn đang mở (chưa done, chưa reset)
    suite_early = env_early.get_test_suite()

    suite_done = env.get_test_suite()
    assert suite_done == [["go_1", "go_2"]]
    assert suite_early == [["go_1"], ["go_1", "go_2"]]


def test_integration_login_model_random_walk_convergence() -> None:
    """Kịch bản 5: Tích hợp models/login.json, chạy Random Walk 200 bước và kiểm tra hội tụ."""
    login_path = Path(__file__).resolve().parent.parent / "models" / "login.json"
    assert login_path.is_file(), f"Không tìm thấy tệp mô hình thật: {login_path}"

    rng = random.Random(42)
    env = Environment(str(login_path), budget=200, max_steps_per_ep=20, log_interval=50)

    assert len(env.states) == 11
    assert 24 <= len(env.all_transitions) <= 28

    state = env.reset()
    while env.total_steps < env.budget:
        valid_actions = env.get_valid_actions(state)
        assert len(valid_actions) > 0
        action = rng.choice(valid_actions)
        next_state, _, done, _ = env.step(action)
        state = env.reset() if done else next_state

    assert env.total_steps == 200

    history = env.get_convergence_history()
    assert [entry["step"] for entry in history] == [50, 100, 150, 200]
    for entry in history:
        assert 0.0 <= float(entry["state_coverage"]) <= 100.0
        assert 0.0 <= float(entry["transition_coverage"]) <= 100.0
        assert 0.0 <= float(entry["transition_pair_coverage"]) <= 100.0

    # Độ bao phủ phải đơn điệu không giảm qua các mốc lịch sử
    for index in range(1, len(history)):
        assert history[index]["transition_coverage"] >= history[index - 1]["transition_coverage"]

    suite = env.get_test_suite()
    assert len(suite) > 0
