# -------------------------------------------------
#  基础镜像：Rocker 官方 r-base (Debian-based) + R 4.3.1
# -------------------------------------------------
FROM rocker/r-base:4.3.1

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# ---------- 1️⃣ 修复 Debian GPG 公钥并安装系统依赖 ----------
RUN apt-get update --allow-insecure-repositories || true && \
    apt-get install -y --no-install-recommends gnupg ca-certificates && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys \
        6ED0E7B82643E131 78DBA3BC47EF2265 BDE6D2B9216EC7A8 8E9F831205B4BA95 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-dev \
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
    && rm -rf /var/lib/apt/lists/*

# ---------- 4️⃣ 复制项目文件 ----------
COPY backend/requirements.txt /app/backend/
COPY install_r_packages.R /app/

# ---------- 5️⃣ 安装 R 包 ----------
RUN Rscript /app/install_r_packages.R

# ---------- 6️⃣ 安装 Python 依赖 ----------
RUN pip3 install --no-cache-dir -r /app/backend/requirements.txt

# ---------- 7️⃣ 复制源码 ----------
COPY . /app/

# ---------- 8️⃣ 环境变量 & 暴露端口 ----------
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend/app.py
EXPOSE 5000

# ---------- 9️⃣ 启动命令 ----------
CMD ["python3", "backend/app.py"]
