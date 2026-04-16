# AI Agent 智能体模块

AI热点追踪平台的核心智能化组件，提供AI驱动的内容处理、分类、推荐等功能，大幅提升平台运营效率和用户体验。

![Version](https://img.shields.io/badge/version-1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Go](https://img.shields.io/badge/go-1.21+-00ADD8)
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

- ✅ 微服务架构设计
- ✅ 支持多AI模型接入（OpenAI、Anthropic）
- ✅ Redis缓存层优化性能
- ✅ Docker容器化部署
- ✅ RESTful API + gRPC双协议支持
- ✅ 完善的监控和日志系统

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
│                       API网关层 (Gateway Layer)                       │
│                     Nginx / Go Zero Gateway                          │
├─────────────────────────────────────────────────────────────────────┤
│                        服务层 (Service Layer)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐         │
│  │ Content      │  │ AI Agent     │  │  Tool Library    │         │
│  │ Service      │  │ Service      │  │  Service         │         │
│  └──────────────┘  └──────────────┘  └──────────────────┘         │
├─────────────────────────────────────────────────────────────────────┤
│                      AI引擎层 (AI Engine Layer)                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │   AI Service    │  │ AI 模型管理器   │  │  Prompt 管理器  │     │
│  │   (LLM 服务)    │  │                 │  │                 │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
├─────────────────────────────────────────────────────────────────────┤
│                       数据层 (Data Layer)                             │
│  MySQL | Redis | MongoDB | Kafka                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 技术栈

- **后端**: Go 1.21+
- **AI服务**: OpenAI GPT-4 / Anthropic Claude
- **数据库**: MySQL, Redis
- **消息队列**: Kafka
- **容器化**: Docker, Docker Compose
- **API网关**: Nginx, Go Zero
- **监控**: Prometheus, Grafana

## 🚀 快速开始

### 前置要求

- Go 1.21 或更高版本
- Docker 和 Docker Compose
- OpenAI API Key（或其他AI服务）

### 本地开发

```bash
# 克隆项目
git clone https://github.com/your-org/hot-ai-agent.git
cd hot-ai-agent

# 启动依赖服务
docker-compose up -d mysql redis

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 AI_API_KEY 等配置

# 安装依赖
go mod download

# 启动服务
go run apps/services/ai-agent-svc/main.go
```

### 生产部署

```bash
# 构建镜像
docker build -t ai-hot-ai-agent-svc:latest -f deploy/docker/Dockerfile.ai-agent .

# 使用 Docker Compose 部署
docker-compose -f docker-compose.production.yml up -d

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
├── apps/
│   └── services/
│       └── ai-agent-svc/          # AI Agent服务
│           ├── main.go            # 入口文件
│           ├── config/            # 配置管理
│           ├── handler/           # HTTP处理
│           ├── logic/             # 业务逻辑
│           ├── service/           # 服务层
│           ├── model/             # 数据模型
│           └── internal/          # 内部逻辑
├── deploy/
│   └── docker/                    # Docker配置
├── docs/
│   ├── api/                       # API文档
│   ├── 需求文档/                  # PRD文档
│   ├── 技术文档/                  # 技术架构
│   └── 用户文档/                  # 用户指南
├── tests/                         # 测试文件
├── scripts/                       # 脚本工具
├── go.mod                         # Go依赖管理
├── go.sum                         # Go依赖锁定
├── docker-compose.yml             # Docker编排
└── README.md                      # 项目说明
```

## 🧪 测试

### 运行测试

```bash
# 单元测试
go test ./...

# 集成测试
go test ./tests/integration -v
```

### 测试覆盖

- ✅ 单元测试：核心业务逻辑
- ✅ 集成测试：服务间通信
- ✅ 性能测试：并发和响应时间
- ✅ 安全测试：认证和授权

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 必填 |
|--------|------|------|
| `AI_MODEL_PROVIDER` | AI模型提供商 (openai/anthropic) | 是 |
| `AI_API_KEY` | AI服务API密钥 | 是 |
| `AI_MODEL` | 使用的模型名称 | 是 |
| `AI_MAX_TOKENS` | 最大token数 | 否 |
| `AI_TEMPERATURE` | 模型温度参数 | 否 |
| `REDIS_ADDR` | Redis地址 | 否 |
| `MYSQL_ADDR` | MySQL地址 | 否 |

### 配置文件

服务配置文件位于 `apps/services/ai-agent-svc/config/ai-agent.yaml`

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

- 遵循 [Go官方代码规范](https://golang.org/doc/effective_go)
- 使用 `gofmt` 格式化代码
- 编写单元测试并确保覆盖
- 更新相关文档

### 开发环境

```bash
# 安装开发工具
go install github.com/go-delve/delve/cmd/dlv@latest
go install github.com/cosmtrek/air@latest

# 使用 air 热重载开发
air
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

- [Go](https://golang.org/) - 编程语言
- [OpenAI](https://openai.com/) - AI服务
- [Docker](https://www.docker.com/) - 容器化
- [Prometheus](https://prometheus.io/) - 监控系统

---

**Made with ❤️ by AI Hot Team**
