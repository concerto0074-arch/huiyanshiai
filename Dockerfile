# 使用 rocker 官方更稳定的 4.3.1 镜像 (基于 Ubuntu，避免 Debian Sid 的编译器 Bug)
FROM rocker/r-base:4.3.1

# 设置非交互环境变量
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# 1. 直接安装预编译好的 R 系统包 (r-cran-*)，避开 C 源代码编译过程
# 2. 同时安装 Python 和 数据库依赖
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

# 复制配置文件
COPY backend/requirements.txt /app/backend/
COPY install_r_packages.R /app/

# 安装剩余的 R 包（大部分已经通过 apt 预装好了，这里只会快速检测补充）
RUN Rscript /app/install_r_packages.R

# 安装后端 Python 库
RUN pip3 install --no-cache-dir -r /app/backend/requirements.txt

# 复制项目代码
COPY . /app/

# 环境变量设置
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=api/app.py
EXPOSE 5000

# 启动命令
CMD ["python3", "api/app.py"]
