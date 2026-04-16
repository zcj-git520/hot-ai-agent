#!/bin/bash

echo "🚀 AI Agent服务启动脚本"

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env文件不存在，从.env.example复制..."
    cp .env.example .env
    echo "⚠️  请编辑.env文件，填入您的OpenAI API Key"
    echo "   OPENAI_API_KEY=your_api_key_here"
fi

# 检查OpenAI API Key
if grep -q "your_openai_api_key_here" .env; then
    echo "❌ 错误：请在.env文件中设置有效的OpenAI API Key"
    exit 1
fi

# 检查Python版本
echo "📊 检查Python版本..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✅ Python版本: $python_version"

# 安装依赖
echo "📦 安装Python依赖..."
pip install -r ai_agent_service/requirements.txt

# 创建日志目录
echo "📁 创建日志目录..."
mkdir -p logs

# 启动服务
echo "🚀 启动AI Agent服务..."
cd ai_agent_service
python main.py

echo "💡 提示：按Ctrl+C停止服务"
