"""[N2, N3] Thuật toán lai ghép Q-GA (Q-Learning Guided Genetic Algorithm).

Cơ chế 2 pha dưới cùng ngân sách step B (mặc định B = 3000):
- Pha 1 (Q-Seeding, 0.2 * B bước): chạy Q-Learning để thu bảng Q(s, a) và tập episode tốt
  làm quần thể khởi tạo cho GA (khi use_q_seeding=True).
- Pha 2 (GA + Q-Guided Mutation, 0.8 * B bước): tiến hóa quần thể GA; khi đột biến tại
  trạng thái s, tra bảng Q(s, a) để ưu tiên hành động triển vọng (khi use_q_mutation=True).

Điều khiển Ablation Study (RQ3) bằng 2 cờ:
- Q-GA (đầy đủ):      use_q_seeding=True,  use_q_mutation=True
- Q-GA-Seed:          use_q_seeding=True,  use_q_mutation=False
- Q-GA-Mut:           use_q_seeding=False, use_q_mutation=True
"""

from __future__ import annotations


def run_q_ga(
    env,
    budget: int = 3000,
    seed: int = 1,
    use_q_seeding: bool = True,
    use_q_mutation: bool = True,
):
    """Khung hàm chuẩn để N2 và N3 phối hợp cài đặt ở Sprint 2."""
    raise NotImplementedError("N2 và N3 phối hợp triển khai run_q_ga() ở Sprint 2.")
