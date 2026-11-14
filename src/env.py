"""[N1] Môi trường máy trạng thái hữu hạn xác định (Environment).

File này thuộc phần việc của thành viên N1: cung cấp lớp Environment đọc mô hình
FSM từ file JSON, quản lý ngân sách bước chạy (budget), phần thưởng khám phá
nhánh mới, bộ theo dõi độ bao phủ (state, transition, transition-pair),
lịch sử hội tụ và thu thập bộ ca kiểm thử (test suite).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


Transition = tuple[str, str, str]
TransitionPair = tuple[Transition, Transition]


class Environment:
    """Môi trường mô phỏng máy trạng thái hữu hạn xác định (Deterministic FSM).

    Lớp này làm giao diện chuẩn cho các thuật toán sinh ca kiểm thử (Q-Learning,
    Genetic Algorithm, Random Walk) tương tác theo từng bước (step) hoặc từng
    lượt chạy (episode) trong phạm vi ngân sách bước chạy cho trước.
    """

    def __init__(
        self,
        json_path: str,
        budget: int,
        max_steps_per_ep: int = 20,
        log_interval: int = 50,
    ) -> None:
        """Khởi tạo môi trường từ tệp mô hình FSM dạng JSON.

        Args:
            json_path: Đường dẫn đến tệp JSON mô tả máy trạng thái.
            budget: Tổng số lần gọi step() tối đa trong cả phiên chạy (> 0).
            max_steps_per_ep: Số bước tối đa trong một lượt chạy (episode).
            log_interval: Chu kỳ số bước để ghi nhận lịch sử hội tụ.

        Raises:
            FileNotFoundError: Nếu không tìm thấy tệp JSON.
            ValueError: Nếu cấu trúc JSON hoặc tham số khởi tạo không hợp lệ.
        """
        if budget <= 0:
            raise ValueError("Tham số budget phải là số nguyên dương (> 0).")
        if max_steps_per_ep <= 0:
            raise ValueError("Tham số max_steps_per_ep phải là số nguyên dương (> 0).")
        if log_interval <= 0:
            raise ValueError("Tham số log_interval phải là số nguyên dương (> 0).")

        path = Path(json_path)
        if not path.is_file():
            raise FileNotFoundError(f"Không tìm thấy tệp mô hình JSON: {json_path}")

        with path.open("r", encoding="utf-8") as file_handle:
            data: Any = json.load(file_handle)

        if not isinstance(data, dict):
            raise ValueError("Nội dung JSON phải là một object ở cấp cao nhất.")

        required_keys = {"name", "initial", "states", "transitions"}
        missing_keys = required_keys - set(data.keys())
        if missing_keys:
            raise ValueError(f"Tệp JSON thiếu các khóa bắt buộc: {sorted(missing_keys)}")

        name = data["name"]
        initial = data["initial"]
        states = data["states"]
        transitions = data["transitions"]

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Trường 'name' phải là chuỗi khác rỗng.")
        if not isinstance(initial, str) or not initial.strip():
            raise ValueError("Trường 'initial' phải là chuỗi khác rỗng.")
        if not isinstance(states, list) or not states or not all(isinstance(s, str) for s in states):
            raise ValueError("Trường 'states' phải là danh sách chuỗi khác rỗng.")
        if initial not in states:
            raise ValueError(f"Trạng thái khởi tạo '{initial}' không nằm trong danh sách 'states'.")
        if not isinstance(transitions, list):
            raise ValueError("Trường 'transitions' phải là danh sách các object chuyển tiếp.")

        self.name: str = name
        self.initial: str = initial
        self.states: list[str] = list(dict.fromkeys(states))
        self.budget: int = budget
        self.max_steps_per_ep: int = max_steps_per_ep
        self.log_interval: int = log_interval

        state_set = set(self.states)
        self.transition_map: dict[tuple[str, str], str] = {}
        self.valid_actions_map: dict[str, list[str]] = {state: [] for state in self.states}
        self.all_transitions: set[Transition] = set()

        for index, item in enumerate(transitions):
            if not isinstance(item, dict):
                raise ValueError(f"Phần tử transition tại vị trí {index} phải là object.")
            if not {"from", "event", "to"}.issubset(item.keys()):
                raise ValueError(
                    f"Transition tại vị trí {index} phải có đủ 3 khóa 'from', 'event', 'to'."
                )
            src = item["from"]
            event = item["event"]
            dst = item["to"]
            if not (isinstance(src, str) and isinstance(event, str) and isinstance(dst, str)):
                raise ValueError(
                    f"Các khóa 'from', 'event', 'to' tại vị trí {index} phải là chuỗi."
                )
            if src not in state_set or dst not in state_set:
                raise ValueError(
                    f"Transition ({src}, {event}, {dst}) chứa trạng thái không có trong 'states'."
                )
            key = (src, event)
            if key in self.transition_map:
                raise ValueError(
                    f"Mô hình không xác định: cặp (from={src!r}, event={event!r}) bị trùng lặp."
                )

            self.transition_map[key] = dst
            self.valid_actions_map[src].append(event)
            self.all_transitions.add((src, event, dst))

        self.all_transition_pairs: set[TransitionPair] = {
            (t1, t2)
            for t1 in self.all_transitions
            for t2 in self.all_transitions
            if t1[2] == t2[0]
        }

        # Biến thống kê toàn phiên chạy (không bị xóa khi gọi reset)
        self.total_steps: int = 0
        self.visited_states: set[str] = {self.initial}
        self.visited_transitions: set[Transition] = set()
        self.visited_pairs: set[TransitionPair] = set()
        self.test_suite: list[list[str]] = []
        self.steps_to_max_cov: int = 0
        self.convergence_history: list[dict[str, float | int]] = []

        # Khởi tạo biến lượt chạy hiện tại trước khi gọi reset()
        self.current_state: str = self.initial
        self.steps_in_ep: int = 0
        self.current_episode_actions: list[str] = []
        self.last_transition: Transition | None = None
        self.episode_contributed: bool = False
        self._ep_saved: bool = False

        self.reset()

    def _finalize_episode(self) -> None:
        """Lưu chuỗi hành động của lượt chạy hiện tại vào test_suite nếu có đóng góp mới."""
        if (
            self.episode_contributed
            and len(self.current_episode_actions) > 0
            and not self._ep_saved
        ):
            episode_copy = list(self.current_episode_actions)
            if episode_copy not in self.test_suite:
                self.test_suite.append(episode_copy)
            self._ep_saved = True

    def reset(self) -> str:
        """Đưa môi trường về trạng thái khởi tạo để bắt đầu lượt chạy mới.

        Lưu ý: Hàm này lưu lại lượt chạy trước (nếu có đóng góp mới) và
        tuyệt đối không làm tăng `self.total_steps`.

        Returns:
            Tên trạng thái khởi tạo (`self.initial`).
        """
        self._finalize_episode()

        self.current_state = self.initial
        self.visited_states.add(self.initial)
        self.steps_in_ep = 0
        self.current_episode_actions = []
        self.last_transition = None
        self.episode_contributed = False
        self._ep_saved = False

        return self.current_state

    def get_valid_actions(self, state: str | None = None) -> list[str]:
        """Trả về danh sách sự kiện hợp lệ đi ra từ một trạng thái.

        Args:
            state: Tên trạng thái cần truy vấn. Nếu là None thì dùng trạng thái hiện tại.

        Returns:
            Danh sách các tên sự kiện hợp lệ theo thứ tự ổn định, hoặc [] nếu là sink state.

        Raises:
            ValueError: Nếu trạng thái truyền vào không tồn tại trong mô hình.
        """
        target_state = self.current_state if state is None else state
        if target_state not in self.valid_actions_map:
            raise ValueError(f"Trạng thái không tồn tại trong mô hình: {target_state!r}")
        return list(self.valid_actions_map[target_state])

    def step(self, action: str) -> tuple[str, float, bool, dict[str, bool | int]]:
        """Thực thi một hành động trên trạng thái hiện tại của máy trạng thái.

        Args:
            action: Tên sự kiện đầu vào cần thực thi.

        Returns:
            Bộ 4 giá trị `(next_state, reward, done, info)` trong đó:
            - `next_state`: Trạng thái kế tiếp sau khi thực thi `action`.
            - `reward`: Điểm thưởng (+1.0 cho transition mới, +0.5 cho pair mới, -0.05 cho lặp/lỗi).
            - `done`: Cờ báo hiệu lượt chạy hiện tại đã kết thúc hay chưa.
            - `info`: Từ điển chứa 5 khóa `"is_new_transition"`, `"is_new_pair"`,
              `"invalid"`, `"total_steps"`, `"budget_exhausted"`.
        """
        if self.total_steps >= self.budget:
            self._finalize_episode()
            return (
                self.current_state,
                0.0,
                True,
                {
                    "is_new_transition": False,
                    "is_new_pair": False,
                    "invalid": False,
                    "total_steps": self.total_steps,
                    "budget_exhausted": True,
                },
            )

        self.total_steps += 1
        self.steps_in_ep += 1
        self.current_episode_actions.append(action)

        key = (self.current_state, action)
        if key not in self.transition_map:
            reward = -0.05
            is_new_transition = False
            is_new_pair = False
            invalid = True
            self.last_transition = None
        else:
            invalid = False
            next_state = self.transition_map[key]
            transition: Transition = (self.current_state, action, next_state)
            self.visited_states.add(next_state)

            is_new_transition = transition not in self.visited_transitions
            if is_new_transition:
                self.visited_transitions.add(transition)

            is_new_pair = False
            if self.last_transition is not None:
                pair: TransitionPair = (self.last_transition, transition)
                if pair in self.all_transition_pairs and pair not in self.visited_pairs:
                    is_new_pair = True
                    self.visited_pairs.add(pair)

            self.last_transition = transition
            self.current_state = next_state

            if is_new_transition:
                reward = 1.0
            elif is_new_pair:
                reward = 0.5
            else:
                reward = -0.05

            if is_new_transition or is_new_pair:
                self.episode_contributed = True
                self.steps_to_max_cov = self.total_steps

        if (self.total_steps % self.log_interval == 0) or (self.total_steps == self.budget):
            self.convergence_history.append(
                {
                    "step": self.total_steps,
                    **self.coverage(),
                }
            )

        budget_exhausted = self.total_steps >= self.budget
        is_terminal = len(self.get_valid_actions(self.current_state)) == 0
        reach_max_ep = self.steps_in_ep >= self.max_steps_per_ep
        done = budget_exhausted or is_terminal or reach_max_ep

        if done:
            self._finalize_episode()

        info: dict[str, bool | int] = {
            "is_new_transition": is_new_transition,
            "is_new_pair": is_new_pair,
            "invalid": invalid,
            "total_steps": self.total_steps,
            "budget_exhausted": budget_exhausted,
        }
        return self.current_state, reward, done, info

    def coverage(self) -> dict[str, float]:
        """Tính các chỉ số độ bao phủ hiện tại theo tỷ lệ phần trăm (0.0 - 100.0).

        Returns:
            Từ điển gồm 3 khóa `"state_coverage"`, `"transition_coverage"`,
            `"transition_pair_coverage"`, làm tròn đến 2 chữ số thập phân.
        """
        state_cov = (
            round(len(self.visited_states) / len(self.states) * 100.0, 2)
            if self.states
            else 0.0
        )
        transition_cov = (
            round(len(self.visited_transitions) / len(self.all_transitions) * 100.0, 2)
            if self.all_transitions
            else 0.0
        )
        pair_cov = (
            round(len(self.visited_pairs) / len(self.all_transition_pairs) * 100.0, 2)
            if self.all_transition_pairs
            else 0.0
        )
        return {
            "state_coverage": state_cov,
            "transition_coverage": transition_cov,
            "transition_pair_coverage": pair_cov,
        }

    def get_test_suite(self) -> list[list[str]]:
        """Thu thập và trả về toàn bộ bộ ca kiểm thử đã đóng góp độ phủ mới.

        Hàm tự động hoàn tất lượt chạy đang dở dang (nếu đã có đóng góp nhánh mới)
        trước khi trả về bản sao danh sách các chuỗi sự kiện.

        Returns:
            Danh sách các ca kiểm thử, mỗi ca là một danh sách tên sự kiện.
        """
        self._finalize_episode()
        return [list(episode) for episode in self.test_suite]

    def get_convergence_history(self) -> list[dict[str, float | int]]:
        """Trả về lịch sử hội tụ độ bao phủ theo các mốc bước chạy đã ghi nhận.

        Returns:
            Danh sách các bản ghi dạng `{"step": int, "state_coverage": float,
            "transition_coverage": float, "transition_pair_coverage": float}`.
        """
        return [dict(entry) for entry in self.convergence_history]
