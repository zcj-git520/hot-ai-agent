# AI Agent 智能体模块

AI热点追踪平台的核心智能化组件，提供AI驱动的内容处理、分类、推荐等功能，大幅提升平台运营效率和用户体验。

![Version](https://img.shields.io/badge/version-1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![OpenAI](https://img.shields.io/badge/ai-openai-orange)

## 📋 目录

- [项目简介](#项目简介)
- [核心功能](#核心功能)
- [技术架构](#技术架构)
- [快速开始](#快速开始)
- [API 文档](#api-文档)
- [部署指南](#部署指南)
- [使用指南](#使用指南)
- [项目结构](#项目结构)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 📖 项目简介

AI Agent智能体模块是AI热点追踪平台的核心智能化组件，旨在通过先进的AI技术实现：

- 🎯 **自动化内容处理** - 智能摘要、分类、标签生成
- 🤖 **个性化推荐** - 基于用户画像的内容和学习路径推荐
- 📊 **职业影响分析** - 深度分析各职业受AI影响的程度
- 🛠️ **智能工具建议** - 根据场景推荐合适的AI工具和使用方法

### 技术特点

- ✅ 模块化架构设计
- ✅ 支持多LLM模型接入（OpenAI、通义千问、DeepSeek）
- ✅ Redis缓存层优化性能
- ✅ Docker容器化部署
- ✅ RESTful API接口
- ✅ 完善的日志系统

## 🎯 核心功能

### 1. AI 内容摘要生成
自动为文章生成精准的摘要，支持多种长度输出，提取关键信息和关键词。

**接口**: `POST /api/ai/summarize`

```json
{
  "content": "完整文章内容",
  "max_length": 150,
  "include_keywords": true
}
```

### 2. 智能文章分类
根据文章内容自动识别分类，推荐相关标签和关键词。

**接口**: `POST /api/ai/classify`

```json
{
  "content": "完整文章内容",
  "categories": ["news", "impact", "learn", "tool"]
}
```

### 3. 职业影响分析
分析特定职业受AI影响的程度和趋势，提供转型建议。

**接口**: `POST /api/ai/profession/analyze`

```json
{
  "profession": "设计师",
  "user_profile": {
    "experience": "3年",
    "skills": ["平面设计", "UI设计"]
  }
}
```

### 4. 学习路径推荐
根据用户职业背景推荐个性化学习路径。

**接口**: `POST /api/ai/learning-path/recommend`

### 5. 工具使用建议
根据使用场景推荐合适的AI工具和使用方法。

**接口**: `POST /api/ai/tool/suggest`

## 🏗️ 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                           用户层 (User Layer)                         │
│                     Web UI / Mobile App                              │
├─────────────────────────────────────────────────────────────────────┤
│                       API层 (API Layer)                               │
│                     FastAPI + Uvicorn                                │
├─────────────────────────────────────────────────────────────────────┤
│                        服务层 (Service Layer)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐         │
│   │ Summary      │  │ Classify     │  │ Analysis         │         │
│   │ Chain        │  │ Chain        │  │ Chain            │         │
│   └──────────────┘  └──────────────┘  └──────────────────┘         │
├─────────────────────────────────────────────────────────────────────┤
│                      AI引擎层 (AI Engine Layer)                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│   │ LLM Factory     │  │ Agent Builder   │  │ Prompt Manager  │     │
│   │ (LLM 客户端)    │  │                 │  │                 │     │
│   └─────────────────┘  └─────────────────┘  └─────────────────┘     │
├─────────────────────────────────────────────────────────────────────┤
│                       数据层 (Data Layer)                             │
│  Redis (缓存) | ChromaDB (向量数据库) | MySQL (可选)                  │
└─────────────────────────────────────────────────────────────────────┘
```

### 技术栈

- **后端**: Python 3.11+
- **Web框架**: FastAPI + Uvicorn
- **AI框架**: LangChain + LangGraph
- **LLM服务**: OpenAI GPT-4 / 通义千问 / DeepSeek
- **向量数据库**: ChromaDB
- **缓存**: Redis
- **数据库**: MySQL（可选）
- **容器化**: Docker, Docker Compose
- **配置管理**: YAML

## 🚀 快速开始

### 前置要求

- Python 3.11 或更高版本
- Docker 和 Docker Compose（可选，用于容器化部署）
- OpenAI API Key 或其他 LLM API密钥

### 本地开发

```bash
# 克隆项目
git clone https://github.com/your-org/hot-ai-agent.git
cd hot-ai-agent

# 启动依赖服务（Redis）
docker-compose up -d redis

# 配置应用
# 编辑 src/conf/config.yml 文件，填入 LLM API密钥等配置

# 安装依赖
pip install -r requirements.txt

# 启动服务
python src/main.py
```

### 生产部署

```bash
# 构建镜像
docker build -t ai-hot-ai-agent:latest .

# 使用 Docker Compose 部署
docker-compose up -d

# 查看服务状态
curl http://localhost:8889/health
```

## 📚 API 文档

完整的API接口文档请查看：
- **[交互式文档](docs/api/index.html)** - 推荐使用，支持在线测试
- **[OpenAPI规范](docs/api/openapi.yaml)** - 标准规范文件
- **[Markdown文档](docs/api/user-api.md)** - 文本格式文档

### 主要接口列表

| 功能 | 接口路径 | 方法 | 说明 |
|------|----------|------|------|
| AI摘要生成 | `/api/ai/summarize` | POST | 生成文章摘要 |
| 智能分类 | `/api/ai/classify` | POST | 文章分类和标签推荐 |
| 职业分析 | `/api/ai/profession/analyze` | POST | 职业影响分析 |
| 学习路径推荐 | `/api/ai/learning-path/recommend` | POST | 个性化学习路径 |
| 工具建议 | `/api/ai/tool/suggest` | POST | AI工具推荐和使用建议 |
| 健康检查 | `/health` | GET | 服务健康状态 |

### 认证说明

大多数API接口需要JWT Token认证：

```
Authorization: Bearer <your_access_token>
```

Token通过用户登录接口获取，有效期为24小时。

## 📖 使用指南

### 文章摘要使用

在文章详情页面，用户可以看到AI生成的摘要：

```
【AI摘要】
GPT-5的发布标志着AI技术的又一次重大突破，本文详细分析了这一技术革新对各行业的影响...
```

### 智能分类标签

文章页面会展示AI推荐的标签：

```
【推荐标签】
#AI技术 #GPT-5 #工具评测 #职业影响 #深度学习
```

### 个性化学习推荐

在职业影响页面，系统会根据用户的职业信息和学习需求，推荐相应的学习路径：

```
【为您推荐的学习路径】
1. 零基础入门AI（30天）
2. 设计师AI转型指南（60天）
3. 运营人员AI提效实战（45天）
```

### 工具使用建议

在工具详情页面，将提供使用建议：

```
【使用建议】
对于图像生成任务，推荐使用Midjourney，可参考以下提示词模板：
"a beautiful landscape painting in the style of Van Gogh..."
```

## 📁 项目结构

```
hot-ai-agent/
├── src/                          # 源代码目录
│   ├── agent/                    # Agent构建器
│   │   ├── builder.py            # Agent构建逻辑
│   │   └── prompts.py            # Agent提示词
│   ├── api/                      # API路由
│   │   └── routes.py             # FastAPI路由定义
│   ├── cache/                    # 缓存模块
│   │   └── redis_cache.py        # Redis缓存实现
│   ├── chains/                   # LangChain链
│   │   ├── analysis_chain.py     # 职业分析链
│   │   ├── classify_chain.py     # 分类链
│   │   ├── recommend_chain.py    # 推荐链
│   │   └── summary_chain.py      # 摘要链
│   ├── conf/                     # 配置文件
│   │   └── config.yml            # 主配置文件
│   ├── config/                   # 配置管理
│   │   ├── settings.py           # 设置类
│   │   └── config.py             # 配置加载器
│   ├── model/                    # LLM客户端
│   │   ├── base_client.py        # 基类客户端
│   │   ├── llm_factory.py        # LLM工厂
│   │   └── openai_client.py      # OpenAI客户端
│   ├── rag/                      # RAG模块
│   │   └── indexer.py            # 文档索引器
│   ├── tools/                    # 工具函数
│   │   ├── calculator.py         # 计算器工具
│   │   └── web_search.py         # 网络搜索工具
│   ├── utils/                    # 工具模块
│   │   └── logger.py             # 日志工具
│   ├── main.py                   # 应用入口
│   └── state.py                  # 全局状态管理
├── docs/                         # 文档目录
│   ├── api/                      # API文档
│   ├── 技术文档/                  # 技术架构文档
│   ├── 用户文档/                  # 用户指南
│   └── 需求文档/                  # PRD文档
├── logs/                         # 日志目录
├── tests/                        # 测试文件
├── docker-compose.yml            # Docker编排
├── Dockerfile                    # Docker镜像
├── requirements.txt              # Python依赖
├── start.sh                      # 启动脚本
└── README.md                     # 项目说明
```

## 🧪 测试

### 运行测试

```bash
# 单元测试
pytest tests/ -v

# 带覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

### 测试覆盖

- ✅ 单元测试：核心业务逻辑
- ✅ 集成测试：API端点测试
- ✅ 性能测试：并发和响应时间

## 🔧 配置说明

### 配置文件

项目使用 `src/conf/config.yml` 作为主要配置文件。编辑该文件以配置以下参数：

#### LLM 配置
```yaml
llm:
  deepseek_api_key: "your_deepseek_api_key"    # DeepSeek API密钥
  qwen_api_key: "your_qwen_api_key"            # 通义千问API密钥
  openai_api_key: "your_openai_api_key"        # OpenAI API密钥
  openai_base_url: "https://api.openai.com/v1" # OpenAI API地址
```

#### Redis 配置
```yaml
redis:
  host: "localhost"      # Redis主机地址
  port: 6379             # Redis端口
  password: ""           # Redis密码
  db: 0                  # Redis数据库编号
  cache_prefix: "ai_agent:"  # 缓存键前缀
  cache_ttl: 3600        # 缓存过期时间（秒）
```

#### 应用配置
```yaml
app:
  host: "0.0.0.0"  # 服务监听地址
  port: 8000       # 服务端口
  debug: true      # 调试模式
```

#### RAG 配置
```yaml
rag:
  chroma_persist_dir: "./chroma_db"           # ChromaDB持久化目录
  chroma_collection: "documents"              # 集合名称
  embedding_model: "text-embedding-3-small"   # 嵌入模型
```

### 环境变量（可选）

在 Docker 部署时，可以通过环境变量覆盖 `config.yml` 中的配置：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥 | - |
| `QWEN_API_KEY` | 通义千问API密钥 | - |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | - |
| `REDIS_HOST` | Redis主机地址 | localhost |
| `REDIS_PORT` | Redis端口 | 6379 |
| `REDIS_PASSWORD` | Redis密码 | - |
| `APP_PORT` | 服务端口 | 8000 |
| `DEBUG` | 调试模式 | false |
| `LOG_LEVEL` | 日志级别 | INFO |

## 📊 监控和日志

### 监控指标

- AI调用次数
- 平均处理时间
- 成功/失败率
- 模型响应时间
- 缓存命中率

### 日志级别

- `DEBUG` - 详细调试信息
- `INFO` - 一般信息
- `WARN` - 警告信息
- `ERROR` - 错误信息

### 健康检查

```bash
curl http://localhost:8889/health
```

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 贡献流程

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) Python 代码规范
- 使用 `black` 格式化代码
- 使用 `flake8` 进行代码检查
- 编写单元测试并确保覆盖
- 更新相关文档

### 开发环境

```bash
# 安装开发依赖
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# 代码格式化
black src/

# 代码检查
flake8 src/

# 运行测试
pytest tests/ -v
```

## 📈 更新日志

### v1.0.0 (2026-04-14)
- ✨ 初始版本发布
- 🎯 实现AI摘要生成功能
- 🏷️ 实现智能文章分类
- 📊 实现职业影响分析
- 🎓 实现学习路径推荐
- 🛠️ 实现工具使用建议
- 🐳 完成Docker容器化部署

## 📞 联系方式

- 📧 Email: support@ai-hot.com
- 💬 技术支持: tech@ai-hot.com
- 🌐 官网: https://ai-hot.com
- 📚 文档: https://docs.ai-hot.com

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

感谢以下开源项目和工具：

- [Python](https://www.python.org/) - 编程语言
- [FastAPI](https://fastapi.tiangolo.com/) - Web框架
- [LangChain](https://python.langchain.com/) - AI应用框架
- [OpenAI](https://openai.com/) - AI服务
- [Redis](https://redis.io/) - 缓存数据库
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [Docker](https://www.docker.com/) - 容器化

---

**Made with ❤️ by AI Hot Team**
