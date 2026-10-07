# Báo cáo Lab Day 21 - CI/CD cho AI Systems

| Thông tin | Nội dung |
|---|---|
| Họ và tên | Nguyễn Quang Huy |
| MSSV | 2A202602820 |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/hshdhu/K4-L3-DAY21-NguyenQuangHuy-2A202602820-CI-CD-for-AI-Systems |
| Ngày nộp | Chờ hoàn tất triển khai |

## 1. Bộ siêu tham số đã chọn và lý do

Ba thí nghiệm thực tế dùng 22.361 mẫu huấn luyện, cùng holdout 500 mẫu và random_state=42.

| Lần | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 100 | 0.1 | 3 | 0.710900 | 0.878000 |
| 2 | 50 | 0.05 | 2 | 0.605128 | 0.846000 |
| 3 | 200 | 0.1 | 5 | 0.714932 | 0.874000 |

**Bộ đã chọn:** n_estimators=200, learning_rate=0.1, max_depth=5. Cấu hình này đạt F1 cao nhất, 0,714932, vượt ngưỡng 0,65. Cấu hình mặc định đạt accuracy cao nhất nhưng F1 thấp hơn, cho thấy hai tiêu chí có thể dẫn tới lựa chọn khác nhau. Cấu hình 50 cây, tốc độ học 0,05 và độ sâu 2 có F1 thấp nhất; mô hình có thể chưa học đủ quan hệ trong dữ liệu. Giảm learning_rate thường cần tăng số cây để bù lại.

## 2. Vì sao Quality Gate đặt trên F1 thay vì Accuracy

Dữ liệu chỉ có khoảng 24,8% lớp thu nhập cao và 75,2% lớp thu nhập thấp. Mô hình luôn dự đoán thu nhập thấp vẫn đạt accuracy khoảng 75,2%, nhưng bỏ sót toàn bộ lớp dương và có F1 bằng 0. F1 lớp dương kết hợp precision và recall, đánh giá khả năng nhận diện người có thu nhập trên 50.000 USD. Hàm f1_score dùng mặc định binary với nhãn dương 1. Không dùng weighted vì lớp đa số ảnh hưởng mạnh tới điểm tổng hợp; macro đánh giá trung bình cả hai lớp, không đúng tiêu chí riêng của lab. Quality Gate chỉ cho phép Release khi F1 hữu hạn và đạt ít nhất 0,65. Mô hình chỉ được upload vào đường dẫn phục vụ sau khi qua gate.

## 3. Khó khăn gặp phải và cách giải quyết

| Khó khăn thực tế | Nguyên nhân | Cách giải quyết |
|---|---|---|
| MLflow không import được pkg_resources | Setuptools 84 trong môi trường thiếu module MLflow cũ sử dụng | Cố định setuptools=69.5.1 trong requirements. |
| SQLite tracking không khởi tạo được | SQLAlchemy 2.1.3 thiếu thành phần MLflow 2.13 import | Cố định sqlalchemy=2.0.30 và chạy lại ba thí nghiệm. |

## 4. So sánh Bước 2 và Bước 3

| Chỉ số | Bước 2: 22.361 mẫu | Bước 3: 44.722 mẫu |
|---|---|---|
| f1_score | Chờ report GitHub Actions | Chờ report GitHub Actions |
| accuracy | Chờ report GitHub Actions | Chờ report GitHub Actions |

**Nhận xét:** Chưa có kết quả từ hai lần chạy trên cloud nên chưa kết luận mức thay đổi. Sau khi pipeline hoàn tất, đối chiếu report trên cùng holdout và xác nhận commit dữ liệu tự động kích hoạt đủ bốn jobs.
