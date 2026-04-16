#!/bin/bash

echo "🛑 停止AI Agent服务"

# 查找并停止Python进程
pids=$(ps aux | grep "python main.py" | grep -v grep | awk '{print $2}')

if [ -z "$pids" ]; then
    echo "ℹ️  没有运行中的服务"
    exit 0
fi

echo "🛑 停止以下进程: $pids"
for pid in $pids; do
    kill $pid
    echo "✅ 已停止进程 $pid"
done

echo "✅ AI Agent服务已停止"
