# Nhật ký quyết định (Decisions Log)

Mọi quyết định quan trọng về công cụ, thiết kế hệ thống, tham số thực nghiệm và quy trình làm việc của nhóm được ghi lại tại đây theo thứ tự thời gian.

## 1. Bảng nhật ký quyết định

| Ngày | Quyết định | Lý do | Ai đề xuất |
|------|-----------|-------|-----------|
| 12/11 | Dùng Python 3.11+, thư viện `numpy`, `pandas`, `scipy`, `matplotlib`, `pytest` (dự phòng `Gymnasium`, `DEAP`/`PyGAD` nếu tự cài đặt bị kẹt quá 3 ngày) | Quen thuộc với cả nhóm, đủ dùng cho RL, GA, kiểm định thống kê và vẽ biểu đồ chuẩn bài báo | N4 |
| 12/11 | Quy tắc nhánh Git: nhánh `main` luôn chạy được, không push thẳng; mỗi người làm nhánh riêng (`n1-env`, `n2-qlearn`, `n3-ga`, `n4-sut`) và tạo Pull Request có 1 người duyệt trước khi gộp | Tránh xung đột code khi 4 người cùng làm, giữ nhánh `main` luôn ổn định | N4 |
| 12/11 | Nhịp làm việc: họp ngắn 15 phút 2 lần/tuần (cố định giờ); báo tiến độ vào nhóm chat mỗi ngày 1–2 dòng | Theo dõi sát tiến độ ngắn hạn, phát hiện sớm chỗ bị kẹt để hỗ trợ nhau | N4 |
| 12/11 | Định nghĩa "Xong" (Definition of Done): code đã merge vào `main`, có test hoặc ví dụ chạy được, có ghi nhận trong `README.md` hoặc `decisions.md` | Đảm bảo sản phẩm bàn giao dùng được ngay cho thành viên phụ thuộc | N4 |
| 14/11 | Chốt định hướng **Hướng B (`Q-GA` – Q-Learning Guided Genetic Algorithm)** với 3 câu hỏi nghiên cứu: **RQ1** (Khả năng khám phá: `transition_coverage`, `transition_pair_coverage`, `steps_to_max_cov`), **RQ2** (Hiệu quả diệt lỗi: `mutation_score`, `suite_size`), **RQ3** (Ablation Study: `Q-GA` đầy đủ vs `Q-GA-Seed` vs `Q-GA-Mut`) | Khắc phục điểm yếu lặp cục bộ của Q-Learning thuần và đột biến mù quáng của GA thuần; có yếu tố lai ghép mới (*novelty*) và thí nghiệm chứng minh (*Ablation Study*) | Nhóm (chốt 14/11) |
| 14/11 | Chốt **Hợp đồng Code**: định dạng `models/*.json` (Deterministic FSM, đủ 100% `states`, không guard), 5 phương thức chuẩn của `Environment` (`src/env.py`) kèm hàm thưởng (`+1.0` transition mới, `+0.5` transition-pair mới, `-0.05` lặp), và quy ước giữ nguyên trạng thái + ghi `"INVALID"` vào trace trên `SUT` (`src/sut.py`) | Đảm bảo 4 thành viên tích hợp code mượt mà; quy ước `"INVALID"` giúp phát hiện mọi mutant thiếu/sai sự kiện mà không làm sập chương trình | N1, N4 (chốt 14/11) |
| 14/11 | Chốt tham số chạy thử & log CSV: độ dài tối đa 1 test case $K = 20$ bước, `Environment` tự động thu nạp Test Suite khi episode mở được transition/pair mới; ngân sách chung **$B = 3.000$ bước `step()`** (với `Q-GA`: 20% `Q-Seeding` + 80% `GA`); chuẩn hóa 2 file log `results/convergence.csv` và `results/summary.csv` | Đảm bảo so sánh công bằng tuyệt đối dưới cùng ngân sách tương tác `step()` trên cả 4 thuật toán (`Random Walk`, `GA`, `Q-Learning`, `Q-GA`) và 2 biến thể ablation | N2, N3, N4 (chốt 14/11) |

---

## 2. Bảng thống nhất Sprint 1–2 (Đã chốt tại buổi họp 14/11)

| Vấn đề | Ai đề xuất | Nội dung đã chốt | Trạng thái |
|--------|-----------|------------------|------------|
| **Định hướng & RQ** | Cả nhóm | Chọn **Hướng B (`Q-GA`)**:<br>- **RQ1 (Khám phá)**: `Q-GA` có vượt `Q-Learning`, `GA`, `Random Walk` về `transition_coverage`, `transition_pair_coverage` và `steps_to_max_cov` không?<br>- **RQ2 (Diệt lỗi)**: `Q-GA` có đạt `mutation_score` cao hơn và ổn định hơn (độ lệch chuẩn thấp hơn qua 30 seeds) và `suite_size` hợp lý không?<br>- **RQ3 (Ablation Study)**: So sánh `Q-GA` (`Seeding + Guided Mutation`), `Q-GA-Seed` (`chỉ Seeding`), `Q-GA-Mut` (`chỉ Guided Mutation`) xem thành phần nào đóng góp nhiều hơn. | Đã chốt (14/11) |
| **Phạm vi mô hình** | N1 | Máy trạng thái hữu hạn xác định (Deterministic FSM), không guard; 3 hệ thống mẫu (`login`, `cart`, `atm`) quy mô 10–20 trạng thái, có nhánh sâu 4–6 bước và nhánh bẫy reset. | Đã chốt (14/11) |
| **Hợp đồng code** | N1 & N4 | - JSON liệt kê đủ 100% `"states"`.<br>- `Environment` (`src/env.py`): `__init__`, `reset()`, `get_valid_actions()`, `step()`, `coverage()`, `get_test_suite()`.<br>- `SUT` (`src/sut.py`): gặp sự kiện không hợp lệ thì giữ nguyên trạng thái và ghi `"INVALID"` vào trace đầu ra. | Đã chốt (14/11) |
| **Test Case, Suite & Ngân sách** | N2, N3, N4 | - Độ dài tối đa 1 test case: **$K = 20$**.<br>- `Environment` tự động lưu episode đóng góp transition mới hoặc pair mới vào `test_suite`.<br>- Ngân sách: **$B = 3.000$ bước `step()`** (`Q-GA`: 600 bước Pha 1 `Q-Seeding` + 2.400 bước Pha 2 `GA` + `Q-Guided Mutation`). | Đã chốt (14/11) |
| **Công cụ & Log CSV** | N4 | - Python 3.11+ (`numpy`, `pandas`, `scipy`, `matplotlib`, `pytest`).<br>- Bổ sung `src/algos/q_ga.py`.<br>- Xuất 2 file log: `results/convergence.csv` (mỗi 50 bước) và `results/summary.csv` (tổng hợp cuối mỗi seed). | Đã chốt (14/11) |
| **Nhịp làm việc & Git** | N4 | Họp 15 phút × 2 buổi/tuần; báo cáo ngắn mỗi ngày; nhánh riêng + PR vào `main`; Definition of Done (merge + test/demo + docs). | Đã chốt (14/11) |
