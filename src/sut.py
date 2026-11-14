"""[N4] Hệ thống thử nghiệm (System Under Test - SUT).

Đọc mô hình Deterministic FSM từ dict hoặc file JSON và thực thi chuỗi sự kiện
(test case) để trả về chuỗi trạng thái quan sát được (trace).

Quy ước chung đã chốt (14/11):
- Nếu gặp sự kiện không hợp lệ tại trạng thái hiện tại, SUT giữ nguyên trạng thái
  và ghi nhận chuỗi "INVALID" vào vị trí tương ứng trong trace (không ném exception).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

INVALID_MARKER = "INVALID"


def load_model(model_or_path: dict[str, Any] | str | Path) -> dict[str, Any]:
    """Nạp mô hình FSM từ dict có sẵn hoặc đường dẫn file JSON."""
    if isinstance(model_or_path, dict):
        return model_or_path
    path = Path(model_or_path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


class SUT:
    """Thực thi ca kiểm thử trên một mô hình FSM (bản gốc hoặc bản đột biến)."""

    def __init__(self, model_or_path: dict[str, Any] | str | Path) -> None:
        data = load_model(model_or_path)
        self.name: str = data["name"]
        self.initial: str = data["initial"]
        self.states: list[str] = list(data["states"])
        self.trans: dict[tuple[str, str], str] = {
            (t["from"], t["event"]): t["to"] for t in data["transitions"]
        }

    def execute(self, events: list[str]) -> list[str]:
        """Chạy chuỗi sự kiện từ trạng thái khởi tạo và trả về trace đầu ra."""
        cur = self.initial
        trace = [cur]
        for event in events:
            next_state = self.trans.get((cur, event))
            if next_state is not None:
                cur = next_state
                trace.append(cur)
            else:
                trace.append(INVALID_MARKER)
        return trace
