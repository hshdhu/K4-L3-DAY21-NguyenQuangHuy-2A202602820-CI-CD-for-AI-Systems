# Các bước còn lại trên AWS — us-east-1

## 1. Cài AWS CLI

Tải và chạy bộ cài chính thức: https://awscli.amazonaws.com/AWSCLIV2.msi
Đóng rồi mở lại IDE/PowerShell sau khi cài. Kiểm tra `aws --version`.
Hướng dẫn chính thức: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

## 2. Xác thực và tạo bucket

Cấu hình theo loại tài khoản của bạn: IAM Identity Center dùng `aws configure sso`; IAM user có access key dùng `aws configure`. Region là `us-east-1`, output là `json`. Nhập khóa trực tiếp trên máy, không gửi vào chat.

```powershell
aws sts get-caller-identity
$env:AWS_DEFAULT_REGION = 'us-east-1'
$env:ARTIFACT_BUCKET = 'TEN_BUCKET_DUY_NHAT'
aws s3 mb "s3://$env:ARTIFACT_BUCKET" --region us-east-1
```

Bucket giữ private. IAM identity dành cho lab cần ListBucket trên bucket và GetObject/PutObject/DeleteObject trong tiền tố dvc/, cùng PutObject trong artifacts/. EC2 dùng IAM role có GetObject trên artifacts/current/model.joblib.

## 3. DVC

```powershell
python -m pip install -r requirements.txt
dvc init
dvc remote add -d labstore "s3://$env:ARTIFACT_BUCKET/dvc"
dvc remote modify labstore region us-east-1
dvc add data/train_batch1.csv data/holdout.csv data/train_batch2.csv
dvc push
```

Không ghi access key vào `.dvc/config`. DVC dùng credentials AWS đã cấu hình trên máy. Nếu repo đã khởi tạo DVC, bỏ qua `dvc init`.

## 4. EC2 và API

Tạo EC2 Ubuntu trong us-east-1, gắn IAM role đọc mô hình S3. SSH user mặc định của Ubuntu là ubuntu. Cấu hình Security Group cho SSH và TCP 8080 theo nguồn truy cập cần dùng; GitHub runner cần kết nối được SSH khi deploy.

Trên VM:

```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv ~/income-venv
~/income-venv/bin/pip install fastapi==0.111.0 uvicorn==0.29.0 scikit-learn==1.4.2 joblib==1.4.2 pandas==2.2.2 'boto3==1.34.162'
mkdir -p ~/src ~/models
```

Chuyển src/serve.py lên ~/src/serve.py bằng scp. Tạo systemd service /etc/systemd/system/income-api.service:

```ini
[Unit]
Description=Income Model Inference Server
After=network-online.target
Wants=network-online.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu
Environment="ARTIFACT_BUCKET=TEN_BUCKET_THAT"
Environment="AWS_DEFAULT_REGION=us-east-1"
ExecStart=/home/ubuntu/income-venv/bin/python /home/ubuntu/src/serve.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Thay tên bucket, sau đó chạy sudo systemctl daemon-reload và sudo systemctl enable income-api. Pipeline sẽ start/restart sau khi upload mô hình đầu tiên.

## 5. GitHub Secrets — vẫn dùng 5 tên

STORAGE_CREDENTIALS chứa JSON theo cấu trúc dưới đây (điền key của IAM identity dành cho lab):

```json
{"AWS_ACCESS_KEY_ID":"YOUR_ACCESS_KEY","AWS_SECRET_ACCESS_KEY":"YOUR_SECRET_KEY"}
```

Nếu dùng credentials tạm thời, thêm AWS_SESSION_TOKEN; credentials này có thời hạn. Các secrets còn lại: ARTIFACT_BUCKET (tên bucket), SERVER_HOST (public IP EC2), SERVER_USER (ubuntu), SERVER_SSH_KEY (private key tương ứng public key được cho phép SSH vào EC2).

## 6. Chạy pipeline và bằng chứng

Sau khi dvc push thành công, VM và secrets đã sẵn sàng, commit code, .dvc/config và các con trỏ data/*.dvc, rồi push main. Chụp Actions Bước 2, curl API và S3 Console thấy dvc/ cùng artifacts/current/model.joblib. Gửi report GitHub Actions để cập nhật báo cáo.

Chỉ khi Bước 2 thành công: chạy python append_batch.py một lần, xác nhận 44.722 mẫu, dvc add data/train_batch1.csv, dvc push, rồi commit con trỏ và git push. Chụp Actions Bước 3 và lấy report mới để hoàn thiện so sánh.

