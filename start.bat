@echo off
chcp 65001 >nul
echo ========================================
echo   AI Agent 服务启动脚本
echo ========================================
echo.

cd /d %~dp0

echo [1/4] 检查Python版本...
python --version
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装 Python 3.10+
    pause
    exit /b 1
)
echo.

echo [2/4] 安装依赖...
pip install -r requirements.txt --timeout 120
if errorlevel 1 (
    echo [警告] 依赖安装可能失败，尝试继续启动...
)
echo.

echo [3/4] 创建日志目录...
if not exist logs mkdir logs
echo.

echo [4/4] 启动服务...
echo.
echo 提示：按 Ctrl+C 停止服务
echo.

set PYTHONPATH=%~dp0
python src/main.py

pause
