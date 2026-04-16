# AI Agent 智能体模块 - 技术架构文档

## 版本信息
- **版本**: v1.0
- **创建日期**: 2026-04-14
- **负责人**: AI Agent技术团队
- **适用范围**: AI热点追踪平台AI Agent模块

## 1. 概述

### 1.1 项目背景
为配合AI热点追踪平台的智能化发展需求，建设专门的AI Agent服务模块，用于提供智能化的内容处理、分类、推荐等服务，提高平台内容处理效率和用户体验。

### 1.2 技术目标
- 构建高可用的AI服务架构
- 实现与现有微服务的无缝集成
- 支持多种AI模型接入和切换
- 提供灵活可扩展的API接口

## 2. 系统架构设计

### 2.1 总体架构图
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           用户层 (User Layer)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                               Web/UI (用户可见)                             │
│                    ┌─────────────┐  ┌─────────────┐                           │
│                    │   Web UI    │  │ Mobile App  │                           │
│                    └─────────────┘  └─────────────┘                           │
│                               │     │                                       │
│                               ▼     ▼                                       │
│         ┌─────────────────────────────────────────────────────────────┐     │
│         │                        API网关层 (Gateway Layer)               │     │
│         │                   ┌─────────┐   ┌─────────┐                  │     │
│         │                   │  Nginx  │   │  Go Zero Gateway  │              │
│         │                   └─────────┘   └─────────┘                  │     │
│         └─────────────────────────────────────────────────────────────┘     │
│                               │     │                                       │
│                               ▼     ▼                                       │
│         ┌─────────────────────────────────────────────────────────────┐     │
│         │                         服务层 (Service Layer)                │     │
│         │  ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐   │     │
│         │  │   Content    │   │   AI Agent   │   │    Tool Library  │   │
│         │  │   Service    │   │   Service    │   │    Service       │   │
│         │  └──────────────┘   └──────────────┘   └──────────────────┘   │     │
│         │         │              │              │                        │     │
│         │         ▼              ▼              ▼                        │     │
│         │  ┌─────────────────────────────────────────────────────────┐   │     │
│         │  │                   数据层 (Data Layer)                     │   │     │
│         │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │   │     │
│         │  │  │  MySQL  │  │  Redis  │  │ MongoDB │  │  Kafka  │       │   │     │
│         │  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │   │     │
│         │  └─────────────────────────────────────────────────────────┘   │     │
│         └─────────────────────────────────────────────────────────────┘     │
│                               │     │                                       │
│                               ▼     ▼                                       │
│       ┌─────────────────────────────────────────────────────────────┐     │
│       │                       AI引擎层 (AI Engine Layer)                │     │
│       │                    ┌─────────────────┐                        │     │
│       │                    │   AI Service    │                        │     │
│       │                    │   (LLM 服务)    │                        │     │
│       │                    └─────────────────┘                        │     │
│       │                    ┌─────────────────┐                        │     │
│       │                    │ AI 模型管理器   │                        │     │
│       │                    └─────────────────┘                        │     │
│       │                    ┌─────────────────┐                        │     │
│       │                    │  Prompt 管理器  │                        │     │
│       │                    └─────────────────┘                        │     │
│       └─────────────────────────────────────────────────────────────┘     │
│                               │                                             │
│                               ▼                                             │
│                          ┌─────────────────────┐                            │
│                          │ 外部AI服务商API     │                            │
│                          │ (OpenAI/Claude等)  │                            │
│                          └─────────────────────┘                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3. 模块设计

### 3.1 AI Agent服务模块

#### 3.1.1 服务组件架构
```
AI Agent Service
├── main.go (入口文件)
├── config (配置管理)
│   └── config.go
├── handler (HTTP处理)
│   ├── ai_handler.go
│   └── health_handler.go
├── logic (业务逻辑)
│   ├── summarize_logic.go
│   ├── classify_logic.go
│   ├── profession_analysis_logic.go
│   ├── learning_path_logic.go
│   └── tool_suggestions_logic.go
├── service (服务层)
│   ├── ai_service.go
│   └── model_service.go
├── model (数据模型)
│   ├── ai_request.go
│   └── ai_response.go
└── internal (内部逻辑)
    ├── ai_client.go
    ├── prompt_manager.go
    └── cache_manager.go
```

#### 3.1.2 数据模型定义

**AI 请求模型:**
```go
type SummarizeRequest struct {
    Content      string `json:"content"`
    MaxLength    int    `json:"max_length,omitempty"`
    IncludeKeywords bool  `json:"include_keywords,omitempty"`
}

type ClassifyRequest struct {
    Content      string `json:"content"`
    Categories   []string `json:"categories,omitempty"`
}
```

**AI 响应模型:**
```go
type SummarizeResponse struct {
    Text      string   `json:"text"`
    Keywords  []string `json:"keywords,omitempty"`
    Length    int      `json:"length"`
}

type ClassifyResponse struct {
    Category     string   `json:"category"`
    Confidence   float64  `json:"confidence"`
    Tags         []string `json:"tags"`
    Explanation  string   `json:"explanation,omitempty"`
}
```

### 3.2 AI引擎层设计

#### 3.2.1 模型管理器
- 支持多模型接入（OpenAI、Anthropic、本地模型）
- 模型版本控制和切换
- 模型性能监控和评估
- 配置管理

#### 3.2.2 Prompt 管理器
- Prompt模板管理系统
- 系统Prompt和用户Prompt的结合
- Prompt版本控制
- Prompt使用统计和分析

#### 3.2.3 缓存层
- AI处理结果缓存（Redis）
- 模型调用频率限制
- 缓存失效策略
- 性能优化

## 4. 接口设计

### 4.1 REST API设计

**AI摘要生成接口**
```
POST /api/ai/summarize
Content-Type: application/json

{
  "content": "完整的文章内容",
  "max_length": 150,
  "include_keywords": true
}

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "text": "生成的摘要文本",
    "keywords": ["关键词1", "关键词2"],
    "length": 120
  }
}
```

**智能分类接口**
```
POST /api/ai/classify
Content-Type: application/json

{
  "content": "完整文章内容",
  "categories": ["news", "impact", "learn", "tool"]
}

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "category": "impact",
    "confidence": 0.95,
    "tags": ["职业影响", "设计师"],
    "explanation": "基于内容分析，主要讨论职业影响"
  }
}
```

### 4.2 gRPC接口设计

- `Summarize`：摘要生成服务
- `Classify`：内容分类服务  
- `AnalyzeProfession`：职业影响分析服务
- `RecommendLearningPath`：学习路径推荐服务
- `SuggestTool`：工具使用建议服务

## 5. 部署架构

### 5.1 部署结构
```
AI Agent Service 部署
├── Docker Container (1容器)
│   ├── 启动脚本
│   ├── 配置文件
│   ├── 服务主程序
│   └── 依赖库
├── 服务配置文件
│   ├── ai-agent.yaml
│   └── prometheus.yml
├── 服务监控
│   └── 运行状态监控
└── 部署脚本
    ├── docker-compose.yml
    └── deploy.sh
```

### 5.2 部署配置文件示例

#### ai-agent.yaml
```yaml
name: ai-agent-svc
host: 0.0.0.0
port: 8889
mode: debug

ai:
  model_provider: openai
  model: gpt-4
  api_key: "${AI_API_KEY}"
  max_tokens: 1000
  temperature: 0.7

redis:
  addr: redis:6379
  password: ""
  db: 0

mysql:
  addr: mysql:3306
  user: root
  password: root
  database: hot_ai

consul:
  addr: consul:8500
  service_name: ai-agent-svc
```

## 6. 集成方案

### 6.1 与现有服务集成

#### 6.1.1 与内容服务集成
```go
// 内容服务在文章采集完成后的调用示例
func (s *ContentService) ProcessArticle(article *Article) error {
    // 调用AI摘要服务
    summary, err := s.aiAgentService.Summarize(article.Content)
    if err != nil {
        return err
    }
    
    // 更新文章摘要
    article.Summary = summary.Text
    article.Keywords = summary.Keywords
    
    return s.articleRepo.Create(article)
}
```

#### 6.1.2 与工具服务集成
```go
// 工具服务调用建议接口
func (s *ToolService) GetToolSuggestion(tool *Tool, usageContext string) (*ToolSuggestion, error) {
    suggestion, err := s.aiAgentService.SuggestToolUsage(tool, usageContext)
    if err != nil {
        return nil, err
    }
    
    return suggestion, nil
}
```

### 6.2 监控和日志

#### 6.2.1 监控指标
- AI调用次数
- 平均处理时间
- 成功/失败率
- 模型响应时间
- 缓存命中率

#### 6.2.2 日志管理
- 请求日志
- 错误日志
- 性能日志
- 详细的AI处理分析日志

## 7. 安全设计

### 7.1 访问控制
- API Key认证机制
- 请求频率限制
- IP白名单控制
- 异常访问检测

### 7.2 数据安全
- 敏感数据脱敏
- API请求参数验证
- 返回数据内容过滤
- HTTPS传输加密

### 7.3 模型安全
- 输入内容安全检查
- 防止恶意Prompt注入
- 模型输出值过滤
- 审核机制预留

## 8. 性能优化

### 8.1 缓存策略
- AI处理结果缓存（Redis）
- 频繁调用数据缓存
- 预热机制
- 缓存过期策略

### 8.2 异步处理
- 批量任务处理
- 异步通知机制
- 消息队列（Kafka）
- 异步任务监控

### 8.3 负载均衡
- 多实例部署
- 负载均衡策略
- 健康检查
- 服务发现

## 9. 部署脚本示例

### 9.1 Docker Compose文件
```yaml
version: '3.8'
services:
  ai-agent-svc:
    build: 
      context: . 
      dockerfile: Dockerfile.ai-agent
    ports:
      - "8889:8889"
    environment:
      - AI_MODEL_PROVIDER=openai
      - AI_API_KEY=${AI_API_KEY}
    depends_on:
      - mysql
      - redis
    networks:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8889/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

networks:
  backend:
    external: true
```

### 9.2 部署脚本
```bash
#!/bin/bash
# deploy-ai-agent.sh

# 构建镜像
docker build -t ai-hot-ai-agent-svc:latest -f deploy/docker/Dockerfile.ai-agent .

# 启动服务
docker-compose up -d ai-agent-svc

# 等待服务启动
sleep 10
echo "AI Agent服务已启动"

# 健康检查
curl http://localhost:8889/health
if [ $? -eq 0 ]; then
    echo "部署成功！"
else
    echo "部署失败！"
fi
```

## 10. 测试方案

### 10.1 单元测试
- API接口测试
- 数据模型测试
- 业务逻辑测试
- 错误处理测试

### 10.2 集成测试
- 与现有服务集成测试
- 数据流转测试
- 性能测试
- 安全测试

### 10.3 回归测试
- 各功能模块回归测试
- 基础服务稳定性测试
- 集成接口压力测试

## 11. 部署说明

### 11.1 本地开发环境
```bash
# 启动环境依赖
docker-compose up -d mysql redis

# 启动AI Agent服务
go run apps/services/ai-agent-svc/main.go

# 环境变量配置
export AI_MODEL_PROVIDER=openai
export AI_API_KEY=your_openai_key
```

### 11.2 生产环境部署
```bash
# 构建镜像
docker build -t ai-hot-ai-agent-svc:production -f deploy/docker/Dockerfile.ai-agent .

# 启动服务
docker-compose -f docker-compose.production.yml up -d
```

## 12. 维护说明

### 12.1 日常维护
- 定期检查服务健康状态
- 监控AI调用性能
- 分析调用日志
- 及时更新模型配置

### 12.2 故障处理
- 健康检查异常告警
- 性能下降阈值监控
- 日志分析定位问题
- 快速回滚机制