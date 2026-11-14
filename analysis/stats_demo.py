"""[N4] Demo phân tích thống kê 30 seeds & kiểm định Mann-Whitney U (Việc 5).

Minh họa quy trình so sánh kết quả hai thuật toán (ví dụ Q-GA vs GA) qua 30 lần chạy
độc lập (30 seeds):
1. Tính trung bình và độ lệch chuẩn mẫu (ddof=1).
2. Chạy kiểm định phi tham số Mann-Whitney U hai phía (alpha = 0.05).

Ưu tiên dùng numpy + scipy nếu đã cài; tự động fallback sang thư viện chuẩn Python
nếu môi trường chưa cài gói ngoài.
"""

from __future__ import annotations

import math
import random
import statistics


def _generate_sample(mean: float, std: float, n: int, seed: int) -> list[float]:
    rng = random.Random(seed)
    return [rng.gauss(mean, std) for _ in range(n)]


def _mannwhitney_u_pure(x: list[float], y: list[float]) -> tuple[float, float]:
    """Kiểm định Mann-Whitney U hai phía xấp xỉ chuẩn có hiệu chỉnh đồng hạng & liên tục."""
    n1, n2 = len(x), len(y)
    combined = [(val, 0) for val in x] + [(val, 1) for val in y]
    combined.sort(key=lambda pair: pair[0])

    ranks_x = 0.0
    tie_correction = 0.0
    i = 0
    total_n = n1 + n2
    while i < total_n:
        j = i + 1
        while j < total_n and combined[j][0] == combined[i][0]:
            j += 1
        tie_size = j - i
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            if combined[k][1] == 0:
                ranks_x += avg_rank
        if tie_size > 1:
            tie_correction += tie_size**3 - tie_size
        i = j

    u1 = ranks_x - n1 * (n1 + 1) / 2.0
    mean_u = n1 * n2 / 2.0
    sd_u = math.sqrt(
        (n1 * n2 / 12.0) * ((total_n + 1) - tie_correction / (total_n * (total_n - 1)))
    )
    if sd_u == 0:
        return u1, 1.0
    z = max(0.0, abs(u1 - mean_u) - 0.5) / sd_u
    p_value = math.erfc(z / math.sqrt(2.0))
    return u1, p_value


def run_demo() -> None:
    """Chạy mô phỏng 30 seeds: Q-GA ~ N(0.80, 0.05) vs GA ~ N(0.75, 0.05)."""
    try:
        import numpy as np
        from scipy.stats import mannwhitneyu

        rng_a = np.random.default_rng(42)
        rng_b = np.random.default_rng(99)
        q_ga_scores = rng_a.normal(0.80, 0.05, 30)
        ga_scores = rng_b.normal(0.75, 0.05, 30)

        mean_a, std_a = float(np.mean(q_ga_scores)), float(np.std(q_ga_scores, ddof=1))
        mean_b, std_b = float(np.mean(ga_scores)), float(np.std(ga_scores, ddof=1))
        stat = mannwhitneyu(q_ga_scores, ga_scores, alternative="two-sided")
        u_stat, p_val = float(stat.statistic), float(stat.pvalue)
        backend = "numpy + scipy"
    except ImportError:
        q_ga_scores = _generate_sample(0.80, 0.05, 30, seed=42)
        ga_scores = _generate_sample(0.75, 0.05, 30, seed=99)

        mean_a, std_a = statistics.mean(q_ga_scores), statistics.stdev(q_ga_scores)
        mean_b, std_b = statistics.mean(ga_scores), statistics.stdev(ga_scores)
        u_stat, p_val = _mannwhitney_u_pure(q_ga_scores, ga_scores)
        backend = "Python stdlib fallback"

    print(f"Backend: {backend} (n = 30 seeds/thuat toan)")
    print(f"Q-GA : mean +/- std = {mean_a:.4f} +/- {std_a:.4f}")
    print(f"GA   : mean +/- std = {mean_b:.4f} +/- {std_b:.4f}")
    print(f"Mann-Whitney U = {u_stat:.1f}, two-sided p-value = {p_val:.6f}")

    if p_val < 0.05:
        print("Ket luan (alpha = 0.05): Khac biet CO Y NGHIA THONG KE (p < 0.05).")
    else:
        print("Ket luan (alpha = 0.05): Chua du bang chung ket luan khac biet (p >= 0.05).")


if __name__ == "__main__":
    run_demo()
