# AI-Based State Transition Test Generation (`state-test-gen`)

Repository phục vụ thực nghiệm và bài báo nghiên cứu: **So sánh các phương pháp sinh ca kiểm thử dựa trên máy trạng thái (Random Walk, Genetic Algorithm, Q-Learning)**.

---

## 1. Cấu trúc thư mục & Phân công

```text
state-test-gen/
├── README.md              # Tổng quan dự án & Hợp đồng code chung (N1 cập nhật)
├── decisions.md           # Nhật ký quyết định của nhóm
├── requirements.txt       # Các thư viện Python cần thiết
├── src/
│   ├── env.py             # [N1] Môi trường máy trạng thái (Environment)
│   ├── algos/
│   │   ├── qlearn.py      # [N2] Thuật toán Q-Learning
│   │   ├── ga.py          # [N3] Thuật toán di truyền (Genetic Algorithm)
│   │   └── random_walk.py # [N3] Thuật toán cơ sở (Random Walk baseline)
│   ├── sut.py             # [N4] Hệ thống thử nghiệm (SUT) chạy máy trạng thái & mutant
│   ├── mutation.py        # [N4] Sinh mutant và tính mutation score
│   └── run.py             # [N4] Runner chạy thực nghiệm nhiều seed, xuất CSV
├── models/                # [N1] Các mô hình máy trạng thái JSON (login.json, cart.json, atm.json)
├── results/               # File CSV kết quả thực nghiệm
├── analysis/              # [N4] Script phân tích thống kê (Mann-Whitney U) và vẽ biểu đồ
├── paper/                 # Bản thảo bài báo, bảng thuật ngữ (glossary.md), trích dẫn (references.bib)
└── tests/                 # Kiểm thử tự động với pytest
```

---

## 2. Cài đặt & Chạy thử

Yêu cầu: **Python 3.11+**

```bash
# Cài đặt thư viện
pip install -r requirements.txt

# Chạy kiểm thử tự động
pytest
```

---

## 3. Quy tắc làm việc với Git

1. **Nhánh `main` luôn chạy được**: Không ai push trực tiếp lên `main`.
2. **Nhánh làm việc cá nhân**: Mỗi thành viên tạo nhánh riêng theo tên việc/vai trò:
   - `n1-env` (N1: Mô hình & Môi trường)
   - `n2-qlearn` (N2: Q-Learning)
   - `n3-ga` (N3: GA & Random Walk)
   - `n4-sut` (N4: SUT, Mutation & Đánh giá)
3. **Pull Request (PR)**: Khi hoàn thành một phần việc, tạo PR vào `main` và nhờ ít nhất 1 thành viên khác xem qua trước khi merge.
4. **Đặt tên commit rõ ràng**: Ví dụ `add random walk baseline`, `implement login state machine json`, `add mutation operators`.
5. **Định nghĩa "Xong" (Definition of Done)**: Code đã merge vào `main`, có test hoặc ví dụ chạy được, và đã ghi nhận vào `README.md` hoặc `decisions.md`.

---

## 4. Hợp đồng Code chung (Code Contract) — *[Phần của N1]*

> **Ghi chú cho N1**: N1 cập nhật chi tiết định dạng JSON và giao diện lớp `Environment` tại đây.

### 4.1. Định dạng file JSON mô hình (`models/*.json`) *(Dự kiến)*
```json
{
  "name": "login_mini",
  "initial": "Start",
  "states": ["Start", "EnterPass", "LoggedIn", "Fail1"],
  "transitions": [
    {"from": "Start", "event": "enter_user", "to": "EnterPass"},
    {"from": "EnterPass", "event": "pass_ok", "to": "LoggedIn"},
    {"from": "EnterPass", "event": "pass_bad", "to": "Fail1"},
    {"from": "Fail1", "event": "retry", "to": "EnterPass"},
    {"from": "LoggedIn", "event": "logout", "to": "Start"}
  ]
}
```

> **Điểm N4 cần thống nhất với N1 trước khi chốt hợp đồng code:**
> 1. Trường `"states"` trong JSON có liệt kê đầy đủ toàn bộ tập trạng thái của hệ thống không (để N4 dùng trực tiếp khi sinh mutant bằng toán tử *đổi đích transition*)?
> 2. Khi gặp một sự kiện không hợp lệ ở trạng thái hiện tại, hàm `step(action)` hoặc SUT sẽ xử lý thế nào (giữ nguyên trạng thái hiện tại và ghi nhận `"INVALID"` vào chuỗi đầu ra, hay báo lỗi)?

### 4.2. Giao diện `Environment` (`src/env.py`) *(Dự kiến)*
- `reset() -> str`: Đưa máy về trạng thái khởi tạo (`initial`), trả về tên trạng thái đầu.
- `get_valid_actions(state: str) -> list[str]`: Trả về danh sách các sự kiện hợp lệ tại `state`.
- `step(action: str) -> tuple`: Thực hiện hành động `action`, trả về trạng thái mới và thông tin chuyển trạng thái.
- `coverage() -> dict`: Trả về các độ đo bao phủ (`state_coverage`, `transition_coverage`, `transition_pair_coverage`).
