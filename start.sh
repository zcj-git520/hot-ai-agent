#!/bin/bash

echo "🚀 AI Agent服务启动脚本"

cd "$(dirname "$0")"

# 检查Python版本
echo "📊 检查Python版本..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✅ Python版本: $python_version"

# 安装依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 创建日志目录
echo "📁 创建日志目录..."
mkdir -p logs

# 启动服务
echo "🚀 启动AI Agent服务..."
export PYTHONPATH="$(dirname "$0")"
python src/main.py

echo "💡 提示：按Ctrl+C停止服务"
