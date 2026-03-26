# 基础镜像：官方 R 环境结合 Python，或者选用 Ubuntu 安装两者
FROM r-base:4.3.1

# 设置非交互环境变量以防 tzdata 等卡住
ENV DEBIAN_FRONTEND=noninteractive

# 设置工作目录
WORKDIR /app

# 安装系统依赖（给 Python 和一些 R 编译包）
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    libpq-dev \
    libcurl4-openssl-dev \
    libxml2-dev \
    libssl-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 先复制环境配置文件以利用 Docker 缓存机制
COPY backend/requirements.txt /app/backend/
COPY install_r_packages.R /app/

# ================= R 环境初始化 =================
# 执行 R 脚本，安装 WGCNA, msgl 等关键生信包
RUN Rscript /app/install_r_packages.R

# ================= Python 环境初始化 =================
# 安装后端所需的所有 Python 库
RUN pip3 install --no-cache-dir -r /app/backend/requirements.txt

# 复制整个项目文件进入此工作目录
COPY . /app/

# 设置启动环境变量与端口
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=api/app.py
EXPOSE 5000

# 指定启动命令 (最终生产环境建议使用 gunicorn -w 4 -b 0.0.0.0:5000 api.app:app)
CMD ["python3", "api/app.py"]
