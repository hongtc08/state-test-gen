# AI-Based State Transition Test Generation (`state-test-gen`)

Repository phục vụ thực nghiệm và bài báo nghiên cứu: **So sánh các phương pháp sinh ca kiểm thử dựa trên máy trạng thái (`Random Walk`, `Genetic Algorithm`, `Q-Learning`) và thuật toán lai ghép đề xuất `Q-GA` (*Q-Learning Guided Genetic Algorithm*)**.

---

## 1. Cấu trúc thư mục & Phân công

```text
state-test-gen/
├── README.md               # Tổng quan dự án & Hợp đồng code chính thức
├── decisions.md            # Nhật ký quyết định đã chốt của nhóm
├── requirements.txt        # Các thư viện Python cần thiết
├── src/
│   ├── env.py              # [N1] Môi trường máy trạng thái (Environment)
│   ├── algos/
│   │   ├── qlearn.py       # [N2] Thuật toán Q-Learning
│   │   ├── ga.py           # [N3] Thuật toán di truyền (Genetic Algorithm)
│   │   ├── random_walk.py  # [N3] Thuật toán cơ sở (Random Walk baseline)
│   │   └── q_ga.py         # [N2, N3] Thuật toán lai ghép Q-GA & Ablation Study (RQ3)
│   ├── sut.py              # [N4] Hệ thống thử nghiệm (SUT) chạy máy trạng thái & mutant
│   ├── mutation.py         # [N4] Sinh mutant (4 toán tử) và tính mutation score
│   └── run.py              # [N4] Runner chạy thực nghiệm 30 seeds, xuất CSV
├── models/                 # [N1] Các mô hình máy trạng thái JSON (login_mini.json, login.json, cart.json, atm.json)
├── results/                # File CSV kết quả thực nghiệm (convergence.csv, summary.csv)
├── analysis/               # [N4] Script phân tích thống kê (Mann-Whitney U) và vẽ biểu đồ
│   └── stats_demo.py       # [N4] Minh họa kiểm định thống kê 30 seeds & Mann-Whitney U
├── paper/                  # Bản thảo bài báo, bảng thuật ngữ (glossary.md), trích dẫn (references.bib)
└── tests/                  # Kiểm thử tự động với pytest / unittest
```

---

## 2. Cài đặt & Chạy thử

Yêu cầu: **Python 3.11+**

```bash
# Cài đặt thư viện
pip install -r requirements.txt

# Chạy demo SUT & Mutation Testing của N4
python src/mutation.py

# Chạy demo thống kê 30 seeds & Mann-Whitney U
python analysis/stats_demo.py

# Chạy kiểm thử tự động
pytest
# Hoặc nếu chưa cài pytest:
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 3. Quy tắc làm việc với Git

1. **Nhánh `main` luôn chạy được**: Không ai push trực tiếp lên `main`.
2. **Nhánh làm việc cá nhân**: Mỗi thành viên tạo nhánh riêng theo tên việc/vai trò:
   - `n1-env` (N1: Mô hình & Môi trường)
   - `n2-qlearn` (N2: Q-Learning & hỗ trợ `Q-GA`)
   - `n3-ga` (N3: GA, Random Walk & `Q-GA`)
   - `n4-sut` (N4: SUT, Mutation, Runner & Đánh giá thống kê)
3. **Pull Request (PR)**: Khi hoàn thành một phần việc, tạo PR vào `main` và nhờ ít nhất 1 thành viên khác xem qua trước khi merge.
4. **Đặt tên commit rõ ràng**: Ví dụ `add random walk baseline`, `implement login state machine json`, `add mutation operators`.
5. **Định nghĩa "Xong" (Definition of Done)**: Code đã merge vào `main`, có test hoặc ví dụ chạy được, và đã ghi nhận vào `README.md` hoặc `decisions.md`.

---

## 4. Hợp đồng Code chung (Chính thức — Đã chốt 14/11)

### 4.1. Định dạng file JSON mô hình (`models/*.json`)
```json
{
  "name": "login_mini",
  "initial": "Start",
  "states": ["Start", "EnterPass", "LoggedIn", "Fail1", "Fail2", "Locked"],
  "transitions": [
    {"from": "Start", "event": "input_user", "to": "EnterPass"},
    {"from": "EnterPass", "event": "pass_ok", "to": "LoggedIn"},
    {"from": "EnterPass", "event": "pass_bad", "to": "Fail1"}
  ]
}
```
- **Quy ước bắt buộc giữa N1 và N4:**
  1. Trường `"states"` phải liệt kê đầy đủ **100%** tập trạng thái của mô hình (để N4 dùng trực tiếp khi sinh mutant bằng toán tử *đổi đích transition*).
  2. Máy trạng thái xác định (*Deterministic FSM*), không điều kiện phụ (*guard*): mỗi cặp `(from, event)` chỉ có tối đa 1 trạng thái đích `to`.

### 4.2. Giao diện lớp `Environment` (`src/env.py`)
```python
class Environment:
    def __init__(self, json_path: str, budget: int = 3000, max_steps_per_ep: int = 20): ...
    def reset(self) -> str: ...
    def get_valid_actions(self, state: str | None = None) -> list[str]: ...
    def step(self, action: str) -> tuple[str, float, bool, dict]: ...
    def coverage(self) -> dict[str, float]: ...
    def get_test_suite(self) -> list[list[str]]: ...
```
- **`reset() -> str`**: Đưa máy về `initial`, bắt đầu một lượt chạy (*episode*) mới, trả về tên trạng thái đầu. **Không tiêu tốn ngân sách `step()`**.
- **`get_valid_actions(state: str | None = None) -> list[str]`**: Trả về danh sách `event` hợp lệ đi ra từ `state` (mặc định trạng thái hiện tại). Nếu là trạng thái kết thúc, trả về `[]`.
- **`step(action: str) -> tuple[str, float, bool, dict]`**: Tăng `total_steps += 1`, trả về `(next_state, reward, done, info)`:
  - *Reward*: `+1.0` nếu đi qua một `transition` mới chưa từng thăm; `+0.5` nếu `transition` cũ nhưng tạo thành `transition-pair` mới; `-0.05` nếu lặp lại hoàn toàn đường đã đi.
  - *Done*: `True` khi đạt `max_steps_per_ep` ($K = 20$), rơi vào trạng thái kết thúc (`get_valid_actions() == []`), hoặc đạt ngân sách `budget` ($B = 3.000$).
  - *Info*: `{"is_new_transition": bool, "is_new_pair": bool, "invalid": bool, "total_steps": int, "budget_exhausted": bool}`.
  - *Thu nạp Test Suite*: Bất kỳ episode nào từ `reset()` đến `done=True` mà đóng góp ít nhất 1 transition mới hoặc 1 transition-pair mới đều được `Environment` tự động lưu vào `test_suite`.
- **`coverage() -> dict[str, float]`**: Trả về `{"state_coverage": float, "transition_coverage": float, "transition_pair_coverage": float}` theo thang `0.0`–`100.0`.
- **`get_test_suite() -> list[list[str]]`**: Trả về danh sách các test case đã thu thập.
- **`get_convergence_history() -> list[dict[str, float | int]]`**: Trả về lịch sử hội tụ độ bao phủ được ghi nhận mỗi `log_interval` bước (mặc định `50`) và tại bước chạm `budget`.

### 4.3. Giao diện `SUT` (`src/sut.py`) & Quy ước `"INVALID"`
- `SUT(model_or_path).execute(events: list[str]) -> list[str]`:
  - Khởi tạo từ `initial` (`trace = [initial]`).
  - Với mỗi `event` trong `events`: nếu `(current_state, event)` hợp lệ thì chuyển sang `next_state` và ghi `next_state` vào `trace`; nếu **không hợp lệ** (ví dụ trên mutant bị xóa cạnh hoặc đổi sự kiện), **giữ nguyên `current_state` và ghi `"INVALID"` vào vị trí tương ứng trong `trace`** (không ném exception).

### 4.4. Định dạng 2 file CSV kết quả (`results/`)
1. **`results/convergence.csv`** *(ghi mỗi 50 bước để vẽ đường cong hội tụ)*:
   ```csv
   system,algo,seed,step,state_coverage,transition_coverage,transition_pair_coverage
   ```
2. **`results/summary.csv`** *(ghi 1 dòng tổng hợp sau mỗi seed để tính thống kê & Mann-Whitney U)*:
   ```csv
   system,algo,seed,budget,final_state_cov,final_trans_cov,final_pair_cov,steps_to_max_cov,suite_size,mutation_score,runtime_sec
   ```

### 4.5. Mô hình & Công cụ đã hoàn thành của N1
- **`models/login.json`**: Mô hình Deterministic FSM hệ thống Đăng nhập nâng cao gồm 11 trạng thái và 27 transitions (nhánh sâu 6–7 bước, nhánh bẫy khóa `Locked`, nhánh bẫy reset `cancel`/`timeout`/`SessionExpired`).
- **`scripts/dot_to_json.py`**: Công cụ CLI chuyển đổi file `.dot` (Mealy Machine / DFA từ Automata Wiki) sang JSON chuẩn:
  ```bash
  # Chuyển đổi 1 file cụ thể
  python scripts/dot_to_json.py --input raw_dot/example.dot --output models/example.json --name example

  # Chuyển đổi hàng loạt toàn bộ raw_dot/*.dot -> models/*.json và in bảng thống kê
  python scripts/dot_to_json.py
  ```
- **`tests/test_env.py`**: Bộ kiểm thử `pytest` gồm 5 kịch bản kiểm tra `coverage()`, cơ chế trả thưởng, giới hạn `budget`, thu thập `get_test_suite()` và tích hợp Random Walk 200 bước trên `models/login.json`.
