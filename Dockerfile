# -------------------------------------------------
#  基础镜像：Rocker 官方的 Ubuntu 22.04 + R 4.3.1
# -------------------------------------------------
FROM rocker/r-base:4.3.1

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# ---------- 1️⃣ 切换为 Ubuntu 官方源 ----------
#（如果您坚持使用 Debian 源，可删除下面两行并保留后面的公钥导入步骤）
RUN echo "deb http://archive.ubuntu.com/ubuntu jammy main restricted universe multiverse\ndeb http://archive.ubuntu.com/ubuntu jammy-updates main restricted universe multiverse\ndeb http://archive.ubuntu.com/ubuntu jammy-security main restricted universe multiverse" > /etc/apt/sources.list

# ---------- 2️⃣（可选）导入缺失的 Debian 公钥 ----------
# RUN apt-get update && apt-get install -y --no-install-recommends gnupg ca-certificates && \
#     apt-key adv --keyserver keyserver.ubuntu.com --recv-keys \
#         6ED0E7B82643E131 78DBA3BC47EF2265 BDE6D2B9216EC7A8 8E9F831205B4BA95 && \
#     rm -rf /var/lib/apt/lists/*

# ---------- 3️⃣ 安装系统依赖 ----------
RUN apt-get update && apt-get install -y --no-install-recommends \
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
    r-cran-devtools \
    r-cran-matrix \
    r-cran-survival \
    r-cran-foreach \
    r-cran-doparallel \
    r-cran-jsonlite \
    r-cran-stringi \
    r-cran-rcpp \
    r-cran-rcpparmadillo \
    r-cran-biocmanager \
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
