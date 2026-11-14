# Bảng thuật ngữ chung (Glossary)

Mỗi thuật ngữ được thống nhất cách gọi tiếng Anh, tiếng Việt và giải thích ngắn gọn để dùng nhất quán trong toàn bộ mã nguồn và bài báo.

## 1. Hệ thống, Kiểm thử & Độ bao phủ (N1)

| Thuật ngữ (Tiếng Anh) | Thuật ngữ (Tiếng Việt) | Giải thích ngắn gọn của nhóm | Người phụ trách |
|-----------------------|------------------------|------------------------------|-----------------|
| Finite State Machine (FSM) | Máy trạng thái hữu hạn | Mô hình gồm tập trạng thái (states) và các chuyển tiếp (transitions) kích hoạt bởi sự kiện (events). | N1 |
| Deterministic FSM | Máy trạng thái xác định | Tại mỗi cặp `(state, event)` hợp lệ chỉ dẫn đến tối đa 1 trạng thái đích `to` duy nhất, không kèm điều kiện phụ (guard). | N1 |
| State Coverage | Độ bao phủ trạng thái | Tỷ lệ phần trăm các trạng thái trong mô hình đã được ghé thăm ít nhất một lần. | N1 |
| Transition Coverage | Độ bao phủ chuyển trạng thái | Tỷ lệ phần trăm các chuyển tiếp (`from --event--> to`) trong mô hình đã được thực thi ít nhất một lần. | N1 |
| Transition-Pair Coverage | Độ bao phủ cặp chuyển tiếp | Tỷ lệ phần trăm các cặp 2 chuyển tiếp liên tiếp nhau đã được thực thi, dùng để đo khả năng đi theo chuỗi sâu. | N1 |
| Test Case / Test Suite | Ca kiểm thử / Bộ kiểm thử | Một test case là chuỗi các sự kiện tối đa $K = 20$ bước từ `initial`; test suite là tập hợp các test case do `Environment` thu thập. | N1, N4 |

## 2. Thuật toán tìm đường & Lai ghép Q-GA (N2, N3)

| Thuật ngữ (Tiếng Anh) | Thuật ngữ (Tiếng Việt) | Giải thích ngắn gọn của nhóm | Người phụ trách |
|-----------------------|------------------------|------------------------------|-----------------|
| Random Walk (Baseline) | Đi ngẫu nhiên (Mốc cơ sở) | Thuật toán chọn ngẫu nhiên một hành động hợp lệ ở mỗi bước; dùng làm ngưỡng tối thiểu để chứng minh thuật toán AI có giá trị. | N3 |
| Q-Learning | Học tăng cường Q-Learning | Thuật toán học bảng giá trị $Q(s, a)$ thông qua tương tác với `Environment` và tín hiệu thưởng/phạt (`+1.0`, `+0.5`, `-0.05`). | N2 |
| $\epsilon$-greedy | Chiến lược tham lam $\epsilon$ | Với xác suất $\epsilon$ tác tử chọn ngẫu nhiên để khám phá nhánh mới (*exploration*), còn lại chọn hành động có $Q$ cao nhất (*exploitation*). | N2 |
| Genetic Algorithm (GA) | Thuật toán di truyền | Thuật toán tiến hóa quần thể các chuỗi hành động qua chọn lọc (*Selection*), lai ghép (*Crossover*) và đột biến (*Mutation*). | N3 |
| Q-Guided Genetic Algorithm (`Q-GA`) | Thuật toán di truyền định hướng bởi Q-Learning | Thuật toán lai ghép 2 pha kết hợp bảng $Q(s, a)$ của Q-Learning vào việc khởi tạo quần thể và định hướng phép đột biến cho GA. | N2, N3 |
| Population Seeding (`Q-Seeding`) | Khởi tạo quần thể bằng Q-Learning | Pha 1 (20% ngân sách đầu): chạy Q-Learning để thu tập chuỗi tốt làm quần thể khởi tạo cho GA thay vì sinh ngẫu nhiên. | N2, N3 |
| Q-Guided Mutation | Đột biến có định hướng bảng Q | Pha 2 (80% ngân sách sau): khi đột biến gen trên chuỗi GA tại trạng thái $s$, tra bảng $Q(s, a)$ để ưu tiên chọn hành động triển vọng. | N2, N3 |
| Ablation Study | Nghiên cứu cắt bỏ thành phần | Thí nghiệm bật/tắt `Q-Seeding` và `Q-Guided Mutation` (`Q-GA`, `Q-GA-Seed`, `Q-GA-Mut`) nhằm đo đóng góp riêng của từng thành phần (RQ3). | N3, N4 |

## 3. Hệ thống thử nghiệm, Mutation Testing & Thống kê (N4)

| Thuật ngữ (Tiếng Anh) | Thuật ngữ (Tiếng Việt) | Giải thích ngắn gọn của nhóm | Người phụ trách |
|-----------------------|------------------------|------------------------------|-----------------|
| System Under Test (SUT) | Hệ thống được kiểm thử | Module thực thi mô hình FSM từ JSON trên từng test case để xuất chuỗi trạng thái đầu ra (`trace`), ghi `"INVALID"` nếu sự kiện không hợp lệ. | N4 |
| Mutant | Bản đột biến (nhân bản có lỗi) | Bản sao của mô hình FSM gốc đã bị cố ý cài một lỗi nhỏ thông qua một toán tử đột biến. | N4 |
| Mutation Operator | Toán tử đột biến | Quy tắc tạo mutant trên FSM: đổi đích (`change_target`), xóa transition (`delete_transition`), đổi sự kiện (`change_event`), thêm transition (`add_transition`). | N4 |
| Equivalent Mutant | Mutant tương đương | Mutant bị sửa cấu trúc nhưng hành vi đầu ra giống hệt máy gốc trên mọi chuỗi sự kiện hợp lệ (không test nào giết được), cần loại khỏi mẫu số. | N4 |
| Kill a Mutant | Giết mutant | Bộ kiểm thử giết được mutant nếu có ít nhất 1 test case cho `trace` trên mutant khác với `trace` trên máy gốc. | N4 |
| Mutation Score | Điểm đột biến | Tỷ lệ phần trăm số mutant bị giết trên tổng số mutant hợp lệ (đã loại equivalent mutant). | N4 |
| Step Budget (`B`) | Ngân sách bước chạy | Tổng số lần gọi `env.step()` tối đa cấp cho mỗi lần chạy (chốt $B = 3.000$ bước) để so sánh công bằng giữa các thuật toán. | N3, N4 |
| Random Seed | Hạt giống ngẫu nhiên | Số nguyên (`1` đến `30`) cố định bộ sinh ngẫu nhiên giúp lặp lại thí nghiệm 30 lần độc lập để phân tích thống kê. | N4 |
| Mann-Whitney U Test | Kiểm định Mann-Whitney U | Kiểm định phi tham số trên 30 seeds để xác định sự khác biệt giữa hai thuật toán có ý nghĩa thống kê ($p < 0.05$) hay do ngẫu nhiên. | N4 |
