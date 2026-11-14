"""[N1] Công cụ chuyển đổi mô hình Graphviz (.dot) sang JSON chuẩn của dự án.

Hỗ trợ các file .dot tải từ Automata Wiki (cả dạng Mealy Machine có nhãn
`EVENT / OUTPUT` và dạng DFA chỉ có `EVENT`), tự động lọc bỏ các cạnh trùng
cặp `(from, event)` để đảm bảo tính xác định (Deterministic FSM) và xuất
bảng thống kê kích thước mô hình.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


START_EDGE_PATTERN = re.compile(
    r'^\s*__start0\s*->\s*(?:"([^"]+)"|([A-Za-z0-9_.\-]+))\s*(?:\[[^\]]*\])?\s*;?\s*$'
)
TRANSITION_EDGE_PATTERN = re.compile(
    r'^\s*(?:"([^"]+)"|([A-Za-z0-9_.\-]+))\s*->\s*(?:"([^"]+)"|([A-Za-z0-9_.\-]+))\s*\[(.*)\]\s*;?\s*$'
)
LABEL_QUOTED_PATTERN = re.compile(r'label\s*=\s*"((?:\\.|[^"\\])*)"')
LABEL_HTML_PATTERN = re.compile(r'label\s*=\s*<(.+)>\s*(?:,|\s|$)')
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")


def _natural_sort_key(text: str) -> list[int | str]:
    """Tạo khóa sắp xếp tự nhiên để s0, s1, s2, ..., s10 đúng thứ tự số học."""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", text)]


def _unquote(quoted: str | None, plain: str | None) -> str:
    """Lấy tên nút đã bỏ ngoặc kép từ kết quả khớp regex."""
    value = quoted if quoted is not None else (plain or "")
    return value.strip()


def _extract_event(raw_label: str) -> str:
    """Tách tên sự kiện đứng trước dấu '/' (nếu có) và loại bỏ khoảng trắng thừa."""
    unescaped = raw_label.replace('\\"', '"').strip()
    if "/" in unescaped:
        event_part = unescaped.split("/", 1)[0]
    else:
        event_part = unescaped
    return event_part.strip()


def parse_dot_file(dot_path: Path, model_name: str | None = None) -> tuple[dict[str, Any], int]:
    """Đọc và phân tích một file .dot thành cấu trúc từ điển JSON chuẩn.

    Args:
        dot_path: Đường dẫn đến file .dot nguồn.
        model_name: Tên mô hình dùng cho trường `"name"`. Nếu là None, lấy tên file gốc.

    Returns:
        Bộ đôi `(model_dict, duplicate_count)` gồm cấu trúc JSON chuẩn và số lượng
        cạnh bị lọc bỏ do trùng lặp cặp `(from, event)`.

    Raises:
        FileNotFoundError: Nếu không tìm thấy file .dot.
        ValueError: Nếu file .dot không chứa trạng thái hoặc cạnh hợp lệ nào.
    """
    if not dot_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy tệp .dot: {dot_path}")

    content = dot_path.read_text(encoding="utf-8")
    initial_state: str | None = None
    raw_transitions: list[tuple[str, str, str]] = []

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("//") or stripped.startswith("#"):
            continue

        start_match = START_EDGE_PATTERN.match(stripped)
        if start_match:
            initial_state = _unquote(start_match.group(1), start_match.group(2))
            continue

        edge_match = TRANSITION_EDGE_PATTERN.match(stripped)
        if edge_match:
            src = _unquote(edge_match.group(1), edge_match.group(2))
            dst = _unquote(edge_match.group(3), edge_match.group(4))
            attrs = edge_match.group(5)

            if src == "__start0" or dst == "__start0":
                if src == "__start0" and initial_state is None:
                    initial_state = dst
                continue

            label_match = LABEL_QUOTED_PATTERN.search(attrs)
            if label_match:
                raw_label = label_match.group(1)
            else:
                html_match = LABEL_HTML_PATTERN.search(attrs)
                if not html_match:
                    continue
                raw_label = HTML_TAG_PATTERN.sub("", html_match.group(1))

            event = _extract_event(raw_label)
            if not event:
                continue

            raw_transitions.append((src, event, dst))

    seen_pairs: set[tuple[str, str]] = set()
    deterministic_transitions: list[dict[str, str]] = []
    duplicate_count = 0
    discovered_states: set[str] = set()

    if initial_state is not None:
        discovered_states.add(initial_state)

    for src, event, dst in raw_transitions:
        discovered_states.add(src)
        discovered_states.add(dst)

        key = (src, event)
        if key in seen_pairs:
            duplicate_count += 1
            continue

        seen_pairs.add(key)
        deterministic_transitions.append(
            {
                "from": src,
                "event": event,
                "to": dst,
            }
        )

    if not discovered_states:
        raise ValueError(f"Không tìm thấy trạng thái hoặc chuyển tiếp hợp lệ trong tệp: {dot_path}")

    sorted_states = sorted(discovered_states, key=_natural_sort_key)
    if initial_state is None:
        initial_state = sorted_states[0]

    resolved_name = model_name.strip() if model_name and model_name.strip() else dot_path.stem
    model_dict: dict[str, Any] = {
        "name": resolved_name,
        "initial": initial_state,
        "states": sorted_states,
        "transitions": deterministic_transitions,
    }
    return model_dict, duplicate_count


def count_transition_pairs(transitions: list[dict[str, str]]) -> int:
    """Đếm tổng số cặp chuyển tiếp liên tiếp hợp lệ (t1, t2) với t1.to == t2.from."""
    outgoing_counts: dict[str, int] = {}
    for item in transitions:
        src = item["from"]
        outgoing_counts[src] = outgoing_counts.get(src, 0) + 1

    total_pairs = 0
    for item in transitions:
        dst = item["to"]
        total_pairs += outgoing_counts.get(dst, 0)
    return total_pairs


def convert_single_file(
    input_path: Path,
    output_path: Path,
    model_name: str | None = None,
) -> tuple[dict[str, Any], int]:
    """Chuyển đổi một file .dot sang .json và ghi xuống ổ đĩa."""
    model_dict, duplicate_count = parse_dot_file(input_path, model_name=model_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file_handle:
        json.dump(model_dict, file_handle, indent=2, ensure_ascii=False)
        file_handle.write("\n")

    if duplicate_count > 0:
        print(
            f"[Thông báo] {input_path.name}: Đã lọc bỏ {duplicate_count} cạnh trùng cặp (from, event)."
        )
    return model_dict, duplicate_count


def convert_batch(raw_dir: Path, models_dir: Path) -> None:
    """Quét toàn bộ tệp *.dot trong raw_dir, chuyển đổi sang models_dir và in bảng thống kê."""
    if not raw_dir.is_dir():
        print(f"Thư mục nguồn '{raw_dir}' chưa tồn tại. Không có tệp .dot nào để chuyển đổi.")
        return

    dot_files = sorted(raw_dir.glob("*.dot"))
    if not dot_files:
        print(f"Không tìm thấy tệp *.dot nào trong thư mục '{raw_dir}'.")
        return

    rows: list[tuple[str, int, int, int, int]] = []
    for dot_file in dot_files:
        output_file = models_dir / f"{dot_file.stem}.json"
        model_dict, dup_count = convert_single_file(dot_file, output_file, model_name=dot_file.stem)
        num_states = len(model_dict["states"])
        num_transitions = len(model_dict["transitions"])
        num_pairs = count_transition_pairs(model_dict["transitions"])
        rows.append((model_dict["name"], num_states, num_transitions, num_pairs, dup_count))

    print("\nBảng thống kê các mô hình đã chuyển đổi:")
    print(f"{'Model':<24} | {'States':>6} | {'Transitions':>11} | {'Pairs':>7} | {'Filtered':>8}")
    print("-" * 68)
    for name, num_states, num_transitions, num_pairs, dup_count in rows:
        print(
            f"{name:<24} | {num_states:>6} | {num_transitions:>11} | {num_pairs:>7} | {dup_count:>8}"
        )


def build_arg_parser() -> argparse.ArgumentParser:
    """Tạo bộ phân tích tham số dòng lệnh cho công cụ dot_to_json."""
    parser = argparse.ArgumentParser(
        description="Chuyển đổi mô hình Graphviz (.dot) sang định dạng JSON chuẩn của state-test-gen."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Đường dẫn tới một file .dot cụ thể cần chuyển đổi.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Đường dẫn file .json đầu ra (mặc định: models/<tên_file>.json khi dùng --input).",
    )
    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Tên mô hình ghi vào trường 'name' trong JSON (mặc định lấy theo tên file).",
    )
    return parser


def main() -> None:
    """Điểm khởi chạy CLI cho công cụ chuyển đổi .dot sang .json."""
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.input is not None:
        output_path = args.output if args.output is not None else Path("models") / f"{args.input.stem}.json"
        model_dict, _ = convert_single_file(args.input, output_path, model_name=args.name)
        num_states = len(model_dict["states"])
        num_transitions = len(model_dict["transitions"])
        num_pairs = count_transition_pairs(model_dict["transitions"])
        print(
            f"Đã xuất '{output_path}' | States: {num_states}, "
            f"Transitions: {num_transitions}, Transition-Pairs: {num_pairs}"
        )
    else:
        if args.output is not None or args.name is not None:
            parser.error("Các tham số --output và --name chỉ dùng kèm với --input.")
        convert_batch(raw_dir=Path("raw_dot"), models_dir=Path("models"))


if __name__ == "__main__":
    main()
