# Dockerfile

# Sử dụng Python base image
FROM python:3.12-slim

# Cài đặt các gói cần thiết để biên dịch mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config

# Đặt thư mục làm việc
WORKDIR /app

# Sao chép file yêu cầu vào container và cài đặt thư viện
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn dự án vào container
COPY . /app/

# Thiết lập biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Migrate và thu thập các static files
RUN python manage.py migrate

# Chạy server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
