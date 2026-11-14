"""[N1] Môi trường máy trạng thái (Environment) theo Hợp đồng Code đã chốt 14/11.

N1 triển khai đầy đủ lớp Environment tại file này dựa trên các chữ ký chuẩn bên dưới.
"""

from __future__ import annotations


class Environment:
    """Môi trường mô phỏng Deterministic FSM thống nhất cho Q-Learning, GA, Random Walk và Q-GA."""

    def __init__(self, json_path: str, budget: int = 3000, max_steps_per_ep: int = 20) -> None:
        raise NotImplementedError("N1 triển khai phần khởi tạo mô hình từ json_path.")

    def reset(self) -> str:
        """Đưa máy về initial state, bắt đầu episode mới (không trừ budget)."""
        raise NotImplementedError("N1 triển khai reset().")

    def get_valid_actions(self, state: str | None = None) -> list[str]:
        """Trả về danh sách event hợp lệ từ state (mặc định current state)."""
        raise NotImplementedError("N1 triển khai get_valid_actions().")

    def step(self, action: str) -> tuple[str, float, bool, dict]:
        """Thực thi 1 bước (tăng total_steps), trả về (next_state, reward, done, info)."""
        raise NotImplementedError("N1 triển khai step().")

    def coverage(self) -> dict[str, float]:
        """Trả về state_coverage, transition_coverage, transition_pair_coverage (0.0 - 100.0)."""
        raise NotImplementedError("N1 triển khai coverage().")

    def get_test_suite(self) -> list[list[str]]:
        """Trả về tập các test case đóng góp transition hoặc transition-pair mới."""
        raise NotImplementedError("N1 triển khai get_test_suite().")
