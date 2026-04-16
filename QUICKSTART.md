# AI Agent 服务快速开始指南

## 📋 目录

- [系统要求](#系统要求)
- [快速安装](#快速安装)
- [配置说明](#配置说明)
- [运行服务](#运行服务)
- [测试API](#测试api)
- [常见问题](#常见问题)

## 🔧 系统要求

- Python 3.11+
- Docker & Docker Compose（可选，用于容器化部署）
- OpenAI API Key

## 🚀 快速安装

### 方法1：直接运行（开发环境）

```bash
# 1. 克隆项目
git clone https://github.com/your-org/hot-ai-agent.git
cd hot-ai-agent

# 2. 配置环境变量
cp .env.example .env
# 编辑.env文件，设置OPENAI_API_KEY

# 3. 安装依赖
pip install -r ai_agent_service/requirements.txt

# 4. 启动服务
cd ai_agent_service
python main.py
```

### 方法2：Docker部署（推荐）

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑.env文件，设置OPENAI_API_KEY

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f ai-agent-service
```

## ⚙️ 配置说明

### 主要配置项

```bash
# AI模型配置
AI_PROVIDER=openai           # AI提供商 (openai/anthropic)
AI_MODEL=gpt-4               # 使用的模型
AI_MAX_TOKENS=2000           # 最大token数
AI_TEMPERATURE=0.7           # 温度参数（0-1）

# 服务端口
PORT=8889                    # 服务监听端口
DEBUG=True                   # 调试模式

# 缓存配置
CACHE_TTL=3600               # 缓存过期时间（秒）
```

### 环境变量清单

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| OPENAI_API_KEY | ✅ | - | OpenAI API密钥 |
| REDIS_HOST | ❌ | localhost | Redis地址 |
| REDIS_PORT | ❌ | 6379 | Redis端口 |
| CACHE_TTL | ❌ | 3600 | 缓存TTL（秒） |
| PORT | ❌ | 8889 | 服务端口 |

## 🎯 运行服务

### 开发环境

```bash
# 在项目根目录执行
bash start.sh

# 或直接运行
cd ai_agent_service
python main.py
```

### 生产环境

```bash
# 使用Docker Compose
docker-compose up -d

# 查看服务状态
docker-compose ps

# 重启服务
docker-compose restart ai-agent-service
```

### 验证服务启动

```bash
# 健康检查
curl http://localhost:8889/health

# 查看API状态
curl http://localhost:8889/api/ai/status
```

预期响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "services": {
      "summarize": true,
      "classify": true,
      "analyze": true,
      "recommend": true
    },
    "models": {
      "provider": "openai",
      "model": "gpt-4"
    }
  }
}
```

## 🧪 测试API

### 1. AI摘要生成

```bash
curl -X POST http://localhost:8889/api/ai/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "content": "GPT-4是OpenAI开发的最新大型语言模型，具有强大的自然语言处理能力...",
    "max_length": 200,
    "include_keywords": true
  }'
```

### 2. 智能分类

```bash
curl -X POST http://localhost:8889/api/ai/classify \
  -H "Content-Type: application/json" \
  -d '{
    "content": "本文讨论了AI技术对设计师职业的影响，以及设计师如何适应新的技术趋势。",
    "categories": ["news", "impact", "learn", "tool"]
  }'
```

### 3. 职业分析

```bash
curl -X POST http://localhost:8889/api/ai/profession/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "profession": "设计师",
    "user_profile": {
      "experience": "3年",
      "skills": ["平面设计", "UI设计"],
      "interests": ["AI设计工具", "用户体验"]
    }
  }'
```

### 4. 学习路径推荐

```bash
curl -X POST http://localhost:8889/api/ai/learning-path/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_profession": "设计师",
    "learning_goals": ["学习AI设计工具", "提升用户体验设计"],
    "target_days": 60
  }'
```

## 📊 API接口列表

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 健康检查 | GET | /health | 服务健康状态 |
| API状态 | GET | /api/ai/status | 各服务状态 |
| 摘要生成 | POST | /api/ai/summarize | AI摘要生成 |
| 智能分类 | POST | /api/ai/classify | 文章分类 |
| 职业分析 | POST | /api/ai/profession/analyze | 职业影响分析 |
| 学习推荐 | POST | /api/ai/learning-path/recommend | 学习路径推荐 |

## ❓ 常见问题

### 1. 启动时提示"Redis连接失败"

**解决方案**：
- 启动Redis服务：`docker-compose up -d redis`
- 或修改.env中的REDIS_HOST为实际Redis地址

### 2. OpenAI API调用失败

**解决方案**：
- 检查.env中的OPENAI_API_KEY是否正确
- 确保网络可以访问OpenAI API
- 检查API Key是否有足够额度

### 3. 端口被占用

**解决方案**：
- 修改.env中的PORT为其他端口
- 或停止占用8889端口的进程

### 4. 依赖安装失败

**解决方案**：
```bash
# 使用国内镜像源
pip install -r ai_agent_service/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 5. 查看详细日志

```bash
# 实时查看日志
tail -f ai_agent_service/logs/ai_agent_service.log

# 查看错误日志
tail -f ai_agent_service/logs/ai_agent_error.log
```

## 🛠️ 常用命令

```bash
# 启动服务
bash start.sh

# 停止服务
bash stop.sh

# Docker相关
docker-compose up -d           # 启动所有服务
docker-compose down            # 停止所有服务
docker-compose logs -f         # 查看日志
docker-compose restart         # 重启服务

# 查看Redis状态
redis-cli ping

# 清理Docker资源
docker system prune -a
```

## 📚 下一步

- [查看API文档](docs/api/index.html)
- [技术架构文档](docs/技术文档/AI-Agent-智能体模块-技术架构.md)
- [贡献指南](CONTRIBUTING.md)

## 💬 技术支持

如有问题，请联系：
- 邮箱：support@ai-hot.com
- GitHub Issues：[提交问题](https://github.com/your-org/hot-ai-agent/issues)
