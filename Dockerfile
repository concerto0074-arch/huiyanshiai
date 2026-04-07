# -------------------------------------------------
#  基础镜像：Python 3.11 官方 slim (Debian bookworm，稳定可靠)
#  R 通过 CRAN 官方 Debian 仓库安装
# -------------------------------------------------
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# ---------- 1️⃣ 安装系统依赖 + R ----------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gnupg \
        ca-certificates \
        curl \
        libpq-dev \
        libcurl4-openssl-dev \
        libxml2-dev \
        libssl-dev \
        libfontconfig1-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libfreetype6-dev \
        libpng-dev \
        libtiff5-dev \
        libjpeg-dev \
        build-essential \
        r-base \
    && rm -rf /var/lib/apt/lists/*

# ---------- 4️⃣ 复制项目文件 ----------
COPY backend/requirements.txt /app/backend/
COPY install_r_packages.R /app/

# ---------- 5️⃣ 安装 R 包 ----------
RUN Rscript /app/install_r_packages.R

# ---------- 6️⃣ 安装 Python 依赖 ----------
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# ---------- 7️⃣ 复制源码 ----------
COPY . /app/

# ---------- 8️⃣ 环境变量 & 暴露端口 ----------
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend/app.py
EXPOSE 5000

# ---------- 9️⃣ 启动命令 ----------
CMD ["python", "backend/app.py"]
