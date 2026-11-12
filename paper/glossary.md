# Bảng thuật ngữ chung (Glossary)

Mỗi thuật ngữ giải thích ngắn gọn bằng lời của nhóm để thống nhất cách gọi trong toàn bộ bài báo.

| Thuật ngữ (Tiếng Anh) | Thuật ngữ (Tiếng Việt) | Giải thích ngắn gọn của nhóm | Người phụ trách |
|-----------------------|------------------------|------------------------------|-----------------|
| Finite State Machine (FSM) | Máy trạng thái hữu hạn | Mô hình gồm tập các trạng thái (states) và các chuyển tiếp (transitions) kích hoạt bởi sự kiện (events). | N1 |
| State Coverage | Độ bao phủ trạng thái | Tỷ lệ phần trăm các trạng thái trong mô hình đã được đi qua ít nhất một lần. | N1 |
| Transition Coverage | Độ bao phủ chuyển trạng thái | Tỷ lệ phần trăm các chuyển tiếp (`from --event--> to`) trong mô hình đã được thực thi ít nhất một lần. | N1 |
| System Under Test (SUT) | Hệ thống được kiểm thử | Hệ thống đích dùng để chạy bộ kiểm thử (trong bài này là module thực thi máy trạng thái từ file JSON). | N4 |
| Mutant | Bản đột biến (nhân bản có lỗi) | Bản sao của mô hình máy trạng thái gốc đã bị cố ý chèn một lỗi nhỏ thông qua một toán tử đột biến. | N4 |
| Mutation Operator | Toán tử đột biến | Quy tắc biến đổi mô hình gốc để tạo mutant (đổi đích, xóa transition, thêm transition sai, đổi sự kiện kích hoạt). | N4 |
| Equivalent Mutant | Mutant tương đương | Mutant có câu trúc bị sửa đổi nhưng hành vi đầu ra luôn giống hệt bản gốc trên mọi chuỗi sự kiện hợp lệ (không test nào giết được). | N4 |
| Kill a Mutant | Giết mutant | Một ca kiểm thử (test case) giết được một mutant khi chuỗi trạng thái đầu ra trên mutant khác với chuỗi đầu ra trên máy gốc. | N4 |
| Mutation Score | Điểm đột biến | Tỷ lệ giữa số lượng mutant bị bộ kiểm thử giết trên tổng số mutant (sau khi đã loại bỏ các mutant tương đương). | N4 |
| Mann-Whitney U Test | Kiểm định Mann-Whitney U | Kiểm định phi tham số dùng để đánh giá xem sự khác biệt kết quả giữa hai thuật toán (trên 30 seed) có ý nghĩa thống kê ($p < 0.05$) hay chỉ do ngẫu nhiên. | N4 |
