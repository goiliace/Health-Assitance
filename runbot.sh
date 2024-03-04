#!/bin/bash

# Kiểm tra xem môi trường ảo đã tồn tại hay chưa
if [ ! -d ".venv" ]; then
    echo "Môi trường ảo không tồn tại. Đang tạo môi trường ảo..."
    python -m venv .venv || { echo "Không thể tạo môi trường ảo"; exit 1; }
    pip install -r requirements.txt || { echo "Không thể cài đặt các yêu cầu"; exit 1; }
fi

# Kích hoạt môi trường ảo
source .venv/bin/activate || { echo "Không thể kích hoạt môi trường ảo"; exit 1; }

# Khởi chạy ứng dụng Python sử dụng Gunicorn
uvicorn main:app --host 0.0.0.0 --port 8055  || { echo "Không thể chạy ứng dụng Python"; exit 1; }
