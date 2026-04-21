# AI Agent 智能体模块开发指引

## 📚 项目概述

这是一个基于 Python + LangChain+langgraph + FastAPI 的 AI Agent 智能体平台，提供智能问答、内容分析、职业分析等功能。

**核心特性：**
- 🤖 多种 Agent 模式（Router Agent、RAG Chain、Chain 组合）
- 📊 完整的 Chain 实现（分类、分析、推荐、摘要）
- 🔧 可扩展的工具系统
- 💾 Redis 缓存支持
- 📝 结构化 Prompt 管理
- 🚀 FastAPI 异步服务
- 🐳 Docker 容器化部署

## 🏗️ 架构设计

### 5层架构

```
┌─────────────────────────────────────┐
│  用户层         │
├─────────────────────────────────────┤
│  网关层         │
├─────────────────────────────────────┤
│  服务层         │
├─────────────────────────────────────┤
│  AI引擎层        │
├─────────────────────────────────────┤
│  数据层        │
└─────────────────────────────────────┘
```

### 核心模块

- **agent/** - Agent 智能体构建器
- **chains/** - LangChain Chain 实现
- **tools/** - 可复用工具
- **rag/** - RAG 检索增强生成
- **prompt_manager/** - Prompt 模板管理
- **cache/** - Redis 缓存
- **api/** - FastAPI 路由

## 📂 项目结构

```
hot-ai-agent/
├── src/
│   ├── agent/                  # Agent 构建模块
│   │   ├── __init__.py         # Agent 模块入口
│   │   ├── builder.py          # Agent 构建器（Router + RAG）
│   │   └── prompts.py          # Agent Prompt 模板
│   │
│   ├── chains/                 # Chain 实现模块
│   │   ├── __init__.py
│   │   ├── classify_chain.py   # 智能分类
│   │   ├── analysis_chain.py   # 职业分析（Agent模式）
│   │   ├── recommend_chain.py  # 学习推荐
│   │   └── summary_chain.py    # 文本摘要
│   │
│   ├── tools/                  # 工具模块
│   │   ├── __init__.py
│   │   ├── calculator.py       # 计算工具
│   │   └── web_search.py       # 网页搜索工具
│   │
│   ├── rag/                    # RAG 模块
│   │   ├── __init__.py
│   │   └── indexer.py          # 文档索引器
│   │
│   ├── prompt_manager/         # Prompt 管理模块
│   │   ├── __init__.py
│   │   └── template_loader.py  # 模板加载器
│   │
│   ├── cache/                  # 缓存模块
│   │   ├── __init__.py
│   │   └── redis_cache.py      # Redis 缓存实现
│   │
│   ├── config/                 # 配置模块
│   │   ├── __init__.py
│   │   └── config.py           # 配置管理
│   │
│   ├── database/               # 数据库模块（规划中）
│   │   └── __init__.py
│   │
│   ├── api/                    # API 路由模块
│   │   ├── __init__.py
│   │   └── routes.py           # FastAPI 路由
│   │
│   ├── model/                  # LLM 客户端模块
│   │   ├── __init__.py
│   │   ├── base_client.py      # 基类
│   │   ├── openai_client.py    # OpenAI 实现
│   │   └── llm_factory.py      # LLM 工厂
│   │
│   ├── utils/                  # 工具类模块
│   │   ├── __init__.py
│   │   └── logger.py           # 日志工具
│   │
│   └── main.py                 # 应用入口
│
├── conf/                       # 配置文件
│   └── config.yml              # 环境配置
│
├── tests/                      # 测试模块（规划中）
│
├── docs/                       # 文档
│   ├── README.md               # 项目说明
│   ├── 用户文档/               # 用户指南
│   └── 技术文档/               # 技术架构
│
├── Dockerfile                  # Docker 配置
├── docker-compose.yml          # 编排配置
├── requirements.txt            # 依赖清单
└── .env                        # 环境变量
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Redis 6.0+
- Docker (可选)

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd hot-ai-agent

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

### 运行

```bash
# 直接运行
python src/main.py

# 或使用 Docker
docker-compose up -d
```

### API 访问

- 健康检查：`GET /health`
- API 文档：`GET /docs`
- 主页：`GET /`

## 📖 核心概念

### 1. Agent 智能体

Agent 是基于大模型构建的智能体，可以自主调用工具完成任务。

**Agent 模式：**
- **Router Agent** - 智能路由，根据请求类型分发到不同的 Chain
- **Tool-calling Agent** - 工具调用 Agent，支持多工具协作

**创建 Agent：**
```python
from src.agent.builder import create_agent

agent = create_agent()
result = agent.invoke({"input": "你的问题"})
```

### 2. Chain 链

Chain 是将多个 LLM 调用组合在一起的有序序列。

**Chain 类型：**
- **Simple Chain** - 简单的 LLM 调用链
- **Agent Chain** - Agent 模式的复杂推理链
- **RAG Chain** - 检索增强生成链

**示例 - 智能分类：**
```python
from src.chains.classify_chain import ClassifyChain, ClassifyRequest

chain = ClassifyChain()
request = ClassifyRequest(
    content="文章内容...",
    categories=["news", "impact", "learn", "tool"]
)
response = chain.classify(request)
```

### 3. Tool 工具

Tool 是 Agent 可以调用的外部功能。

**创建自定义工具：**
```python
from langchain.tools import tool

@tool
def my_tool(param: str) -> str:
    """
    工具描述（会被 LLM 读取）
    """
    # 工具实现
    return result

# 添加到 Agent
tools = [my_tool, calculator_tool, search_tool]
```

### 4. Prompt 管理

使用 Prompt 模板确保 AI 的输出格式一致。

**创建 Prompt 模板：**
```python
from langchain.prompts import ChatPromptTemplate

prompt_template = ChatPromptTemplate.from_template("""
你是一个专业的{role}。
任务：{task}
输入：{input}
输出格式：{format}
""")
```

### 5. 缓存机制

使用 Redis 缓存常见请求结果，减少重复 AI 调用。

**缓存使用：**
```python
from src.cache.redis_cache import cache

# 设置缓存
cache.set("key", "value", "prefix", ttl=3600)

# 获取缓存
value = cache.get("key", "prefix")
```

## 💡 开发指南

### 添加新的 Chain

1. 在 `src/chains/` 创建新文件
2. 实现 Chain 类
3. 定义请求/响应数据类
4. 注册到 API 路由

```python
# 示例：src/chains/custom_chain.py
from dataclasses import dataclass
from typing import Optional, Dict, Any
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

@dataclass
class CustomRequest:
    input: str
    param: Optional[str] = None

@dataclass
class CustomResponse:
    result: str
    metadata: Dict[str, Any]

class CustomChain:
    def __init__(self):
        self.llm = LLMFactory.create_client()
        self._init_prompt()

    def _init_prompt(self):
        self.prompt_template = ChatPromptTemplate.from_template("""
        你的角色：{role}
        任务：{task}
        输入：{input}
        参数：{param}
        """)

    def execute(self, request: CustomRequest) -> CustomResponse:
        chain = LLMChain(llm=self.llm.llm, prompt=self.prompt_template)
        result = chain.run(
            role="专家",
            task="你的任务",
            input=request.input,
            param=request.param or ""
        )
        return CustomResponse(result=result, metadata={})
```

### 添加新的 Tool

1. 在 `src/tools/` 创建文件
2. 使用 `@tool` 装饰器定义工具
3. 在 `src/agent/builder.py` 中注册工具

```python
# 示例：src/tools/custom_tool.py
from langchain.tools import tool

@tool
def custom_search(query: str, limit: int = 5) -> str:
    """
    自定义搜索工具
    搜索关键词并返回 top N 结果

    Args:
        query: 搜索关键词
        limit: 返回结果数量

    Returns:
        搜索结果字符串
    """
    # 实现搜索逻辑
    results = perform_search(query, limit)
    return "\n".join(results)
```

### 添加新的 API 端点

1. 在 `src/api/routes.py` 添加路由
2. 创建 Chain 实例
3. 处理请求和响应

```python
# 示例：添加新的端点
from fastapi import APIRouter, HTTPException
from src.chains.custom_chain import CustomChain, CustomRequest
from src.utils.logger import logger

router = APIRouter()
chain = CustomChain()

@router.post("/api/custom/execute")
async def execute_custom(request: CustomRequest):
    """执行自定义 Chain"""
    try:
        response = chain.execute(request)
        return {
            "code": 200,
            "message": "success",
            "data": response
        }
    except Exception as e:
        logger.error(f"执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 使用 RAG 模式

```python
from src.agent.builder import create_rag_chain

# 创建 RAG Chain
rag_chain = create_rag_chain()

# 查询
result = rag_chain.invoke({
    "input": "用户问题",
    "context": "检索到的文档"
})
```

## 🔧 配置说明

### 配置文件 (config.yml)

```yaml
model:
  modelName: deepseek-chat
  apiKey: ${DEEPSEEK_API_KEY}
  baseURL: https://api.deepseek.com

chroma:
  persistDirectory: ./chroma_db
  collectionName: documents
```

## 🎯 常见任务

### 调试 Agent 调用

```python
from src.agent.builder import create_agent

agent = create_agent()
result = agent.invoke({"input": "测试问题"}, return_only_outputs=False)
```

### 检查缓存命中率

```python
from src.cache.redis_cache import cache

# 查看缓存统计
stats = cache.get_stats()
print(f"命中次数: {stats['hits']}")
print(f"未命中次数: {stats['misses']}")
```

### 重新加载配置

```python
from src.config.config import Config
from enums.model_enums import ModelType

config = Config("conf/config.yml")
model_config = config.model_config(ModelType.DEEPSEEK)
```

## 📝 最佳实践

### 1. Prompt 设计
- 保持 Prompt 简洁明确
- 定义明确的输出格式
- 使用占位符 `{}` 动态注入数据
- 提供示例（few-shot prompt）

### 2. 错误处理
```python
try:
    result = chain.execute(request)
except Exception as e:
    logger.error(f"执行失败: {str(e)}")
    # 降级处理或返回默认值
    return default_response
```

### 3. 缓存策略
- 对耗时操作使用缓存
- 设置合理的 TTL
- 缓存键要具有唯一性
- 定期清理过期缓存

### 4. 日志记录
```python
from loguru import logger

logger.info("开始处理请求")
logger.debug(f"请求参数: {request}")
logger.error(f"处理失败: {str(e)}", exc_info=True)
```

### 5. 测试
- 为每个 Chain 编写单元测试
- 测试边界情况和错误场景
- 验证缓存机制
- 性能测试

## 🐛 故障排除

### 问题：Agent 不调用工具
**解决：** 确保 Prompt 中明确提到工具，且工具描述清晰。

### 问题：缓存不生效
**解决：** 检查 Redis 连接，确认缓存键设置正确。

### 问题：API 500 错误
**解决：** 查看日志文件 `logs/app.log`，检查异常堆栈。

### 问题：RAG 检索不准确
**解决：** 调整向量检索的 `score_threshold` 和 `k` 参数。

## 📚 相关资源

- [LangChain 文档](https://python.langchain.com/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [OpenAI API 文档](https://platform.openai.com/docs)

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

---

**最后更新：** 2026年4月20日
