# 基于官方 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 启动 FastAPI 应用（假设你的入口为 main.py，app 对象为 "app"）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]