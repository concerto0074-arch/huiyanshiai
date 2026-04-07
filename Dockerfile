# -------------------------------------------------
#  基础镜像：Python 3.11 官方 slim (Debian bookworm)
#  R 算法目前使用 Mock 数据，无需安装 R 环境
# -------------------------------------------------
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# ---------- 1️⃣ 安装最小系统依赖（仅 Python 运行所需）----------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq-dev \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# ---------- 2️⃣ 安装 Python 依赖 ----------
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# ---------- 3️⃣ 复制源码 ----------
COPY . /app/

# ---------- 4️⃣ 环境变量 & 暴露端口 ----------
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend/app.py
EXPOSE 5000

# ---------- 5️⃣ 启动命令 ----------
CMD ["python", "backend/app.py"]
