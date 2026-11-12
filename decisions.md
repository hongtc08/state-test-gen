# Nhật ký quyết định (Decisions Log)

Mọi quyết định quan trọng về công cụ, thiết kế hệ thống, tham số thực nghiệm và quy trình làm việc của nhóm được ghi lại tại đây theo thứ tự thời gian.

## 1. Bảng nhật ký quyết định

| Ngày | Quyết định | Lý do | Ai đề xuất |
|------|-----------|-------|-----------|
| 12/11 | Dùng Python 3.11+, thư viện `numpy`, `pandas`, `scipy`, `matplotlib`, `pytest` (dự phòng `Gymnasium`, `DEAP`/`PyGAD` nếu tự cài đặt bị kẹt quá 3 ngày) | Quen thuộc với cả nhóm, đủ dùng cho RL, GA, kiểm định thống kê và vẽ biểu đồ chuẩn bài báo | N4 |
| 12/11 | Quy tắc nhánh Git: nhánh `main` luôn chạy được, không push thẳng; mỗi người làm nhánh riêng (`n1-env`, `n2-qlearn`, `n3-ga`, `n4-sut`) và tạo Pull Request có 1 người duyệt trước khi gộp | Tránh xung đột code khi 4 người cùng làm, giữ nhánh `main` luôn ổn định | N4 |
| 12/11 | Nhịp làm việc: họp ngắn 15 phút 2 lần/tuần (cố định giờ); báo tiến độ vào nhóm chat mỗi ngày 1–2 dòng | Theo dõi sát tiến độ ngắn hạn, phát hiện sớm chỗ bị kẹt để hỗ trợ nhau | N4 |
| 12/11 | Định nghĩa "Xong" (Definition of Done): code đã merge vào `main`, có test hoặc ví dụ chạy được, có ghi nhận trong `README.md` hoặc `decisions.md` | Đảm bảo sản phẩm bàn giao dùng được ngay cho thành viên phụ thuộc | N4 |

---

## 2. Bảng thống nhất Sprint 1 (Dùng cho buổi họp 14/11)

| Vấn đề | Ai đề xuất | Đề xuất / Nội dung chốt | Trạng thái |
|--------|-----------|-------------------------|------------|
| **RQ và độ đo** | N2, N3 | - **RQ1**: Q-Learning có đạt *transition coverage* cao hơn Random Walk và GA với cùng ngân sách bước chạy không?<br>- **RQ2**: Bộ kiểm thử sinh bởi Q-Learning có đạt *mutation score* cao hơn không?<br>- **Độ đo chính**: Transition coverage. **Độ đo phụ**: Mutation score, số bước, thời gian chạy. | Chờ chốt 14/11 |
| **Phạm vi mô hình** | N1 | Chỉ xét máy trạng thái hữu hạn xác định (Deterministic FSM), không có điều kiện chắn (guard); kích thước 10–20 trạng thái trên 3 hệ thống mẫu (`login`, `cart`, `atm`). | Chờ chốt 14/11 |
| **Hợp đồng code** | N1 (N4 góp ý) | Định dạng JSON chung (`name`, `initial`, `states`, `transitions`) và giao diện `Environment`. SUT của N4 đọc trực tiếp file JSON của N1. | Chờ chốt 14/11 |
| **Đơn vị ngân sách** | N3 | Tổng số lần gọi hàm `step()` (con số cụ thể cho từng hệ thống sẽ chốt đầu Sprint 2). | Chờ chốt 14/11 |
| **Công cụ** | N4 | Python 3.11+; `numpy`, `pandas`, `scipy`, `matplotlib`, `pytest`; quản lý mã nguồn trên GitHub theo quy tắc nhánh riêng + PR; quản lý tài liệu bằng Google Docs chung và `paper/references.bib`. | Đã soạn đề xuất |
| **Nhịp làm việc** | N4 | Họp 15 phút × 2 buổi/tuần cố định giờ; báo cáo hàng ngày 1–2 dòng trên kênh chat; áp dụng định nghĩa "Xong" (merge vào `main` + có test/demo + cập nhật tài liệu). | Đã soạn đề xuất |
