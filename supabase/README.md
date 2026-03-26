# Supabase 数据库使用与迁移指南

此目录专门用于存放与 Supabase（以及未来阿里云全托管 PostgreSQL）数据库相关的文档、测试脚本和手动迁移工具。

由于后端已完全升级为 `Flask-SQLAlchemy`，**你的应用代码不需要修改任何逻辑** 即可无缝切换数据库引擎。以下是配置 Supabase 作为云端数据库的具体步骤：

---

## 🚀 1. 注册并创建 Supabase 项目

1. 前往 [Supabase 官网](https://supabase.com/) 注册账号。
2. 在控制台中点击 **"New Project"**。
3. 输入你的项目名称（如 `huiyanshiai`）并设置一个强密码。
   > **关键提示**：请妥善保存此密码，连接字符串需要用到它！
4. **Region (区域)**：选择离你（或你的部署服务器 Render）最近的节点，比如 `Singapore (新加坡)` 或 `Tokyo (东京)`。
5. 点击 **"Create new project"**，等待约 2 分钟完成数据库初始化。

---

## 🔗 2. 获取数据库连接字符串

1. 进入你新建的 Supabase 项目面板。
2. 在左侧导航栏的最下方，点击 **⚙️ Settings (设置)** -> **Database (数据库)**。
3. 往下找到 **Connection string (连接字符串)** 卡片。
4. 切换到 **URI** 选项卡。
5. 复制提供的链接，它应该长这样：
   ```text
   postgresql://postgres.[你的项目ID]:[YOUR-PASSWORD]@aws-0-[节点].pooler.supabase.com:6543/postgres
   ```
6. 将链接中的 `[YOUR-PASSWORD]` 替换为你在第一步设置的真实密码。

---

## ⚙️ 3. 配置到项目环境中

你的 Flask 后端通过读取 `DATABASE_URL` 环境变量来建立连接。

### A. 本地电脑测试 (开发环境)
打开项目根目录的 `.env` 文件，修改（或覆盖掉原有的 sqlite 路径）如下：
```env
# 将原先的 sqlite 直连替换为：
DATABASE_URL=postgresql://postgres.xxxxx:你的密码@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```
*测试方法*：修改完 `.env` 后，在根目录运行 `python api/app.py`。如果控制台打印了 "App loaded successfully" 且没有报错，说明连接成功。

### B. Render 线上部署 (生产环境)
如果你把项目部署到了 Render，你需要：
1. 登录 Render 控制台。
2. 找到你的 Web Service 项目 -> 左侧点击 **Environment (环境变量)**。
3. 添加一条新的变量：
   - **Key**: `DATABASE_URL`
   - **Value**: `postgresql://postgres.xxxxx:你的密码@aws-...`

---

## 🛠️ 4. 数据库表初始化 (自动完成)

**不用手动去建表！** 👍

得益于我们在 `api/app.py` 中编写的初始化逻辑，当你（在本地或服务器）**第一次启动后端项目时**，Flask 发现 Supabase 中没有 `users` 和 `patients` 表，它会自动为你执行相应的建表语句：

```python
with app.app_context():
    init_db()  # <-- 这个方法会自动连接到指定数据库并在空库中创建所有 ORM 模型对应的表
```

建议你：
1. 在 `.env` 填好 Supabase 链接。
2. 运行 `python api/app.py` 启动一次服务。
3. 回到 Supabase 控制台的 **Table Editor**，你会惊喜地发现 `users` 和 `patients` 表已经创建好，并且字段类型（如 VARCHAR、INTEGER、TIMESTAMP 等）均已完美适配。

---

## 📦 5. 本地 SQLite 数据如何迁移？(可选)

如果你有重要的旧测试账号/数据保存在本地的 `data/patients.db` 中，想移动到 Supabase，你可以：

1. **重新注册**：最简单。在连接到 Supabase 后，此时库是空的，直接在前端页面注册新账号演示即可。
2. 如果真需要迁移历史数据，可以在本目录下写一个简单的同步脚本（读取 sqlite -> 插入 sqlalchemy）。如需要，随时唤醒 AI 给你写这个脚本。
