# AI Agent 智能体 API 文档

## 概述

AI Agent 智能体 API 是一个基于 FastAPI 构建的异步服务，提供智能问答、内容分类、职业分析、文本摘要、翻译等功能。

**基础 URL：** `http://localhost:8000`

**API 文档：** `http://localhost:8000/docs`

**OpenAPI 规范：** `http://localhost:8000/openapi.yaml`

---

## 认证

当前版本无需认证。

---

## 通用响应格式

### 成功响应

```json
{
  "success": true,
  "data": { ... }
}
```

### 错误响应

```json
{
  "detail": "错误描述"
}
```

---

## 接口列表

### 健康检查

**GET** `/health`

检查服务是否正常运行。

**响应示例：**

```json
{
  "status": "healthy"
}
```

---

### 根路径

**GET** `/`

返回服务基本信息。

**响应示例：**

```json
{
  "message": "AI 智能体 API 服务",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

### 文本翻译

**POST** `/api/translate`

将文本翻译为目标语言。语言方向：中文(cn)->英文(en)，非中文->中文(cn)

**请求体：**

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| content | string | 是 | - | 待翻译的文本 |
| source_language | string | 否 | auto | 源语言，auto表示自动检测 |
| target_language | string | 否 | "" | 目标语言，空表示自动判断 |
| model | string | 否 | 默认模型 | 模型标识符：glm, deepseek, qwen, custom |

**请求示例：**

```json
{
  "content": "Hello, world!"
}
```

**响应示例：**

```json
{
  "success": true,
  "translated_text": "你好，世界！",
  "source_language": "en",
  "target_language": "cn",
  "model": "GLM-4-Flash-250414"
}
```

**说明：**
- source_language/target_language 使用 `en`(英文) 或 `cn`(中文)
- 中文文本 -> 翻译为英文
- 英文或其他文本 -> 翻译为中文
- model 参数指定使用的模型，默认为 config.yml 中的 default 模型

---

## Chain 接口（直接调用）

以下 Chain 可以通过代码直接调用：

### ClassifyChain - 智能分类

```python
from src.chains.classify_chain import ClassifyChain, ClassifyRequest

chain = ClassifyChain()
request = ClassifyRequest(
    content="文章内容...",
    categories=["news", "tech", "business"]
)
response = chain.classify(request)
```

**ClassifyRequest：**

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| content | string | 是 | - | 待分类内容 |
| categories | List[str] | 是 | - | 可选类别列表 |
| max_length | int | 否 | 500 | 内容最大长度 |

**ClassifyResponse：**

| 字段 | 类型 | 描述 |
|------|------|------|
| category | string | 分类结果 |
| confidence | float | 置信度 (0-1) |
| reason | string | 分类理由 |
| model | string | 使用的模型 |

---

### SummaryChain - 文本摘要

```python
from src.chains.summary_chain import SummaryChain, SummaryRequest

chain = SummaryChain()
request = SummaryRequest(
    content="长文本内容...",
    max_length=200,
    include_keywords=True,
    language="中文"
)
response = chain.generate(request)
```

**SummaryRequest：**

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| content | string | 是 | - | 待摘要文本 |
| max_length | int | 否 | 200 | 摘要最大长度 |
| include_keywords | bool | 否 | True | 是否提取关键词 |
| language | string | 否 | 中文 | 摘要语言 |

**SummaryResponse：**

| 字段 | 类型 | 描述 |
|------|------|------|
| summary | string | 生成的摘要 |
| keywords | List[str] | 关键词列表 |
| length | int | 摘要长度 |
| model | string | 使用的模型 |
| request_id | string | 请求ID |

---

### RecommendChain - 学习推荐

```python
from src.chains.recommend_chain import RecommendChain, RecommendationRequest

chain = RecommendChain()
request = RecommendationRequest(
    user_profession="软件工程师",
    learning_goals=["提升AI能力", "掌握机器学习"],
    target_days=60
)
response = chain.recommend(request)
```

**RecommendationRequest：**

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| user_profession | string | 是 | - | 用户职业 |
| learning_goals | List[str] | 否 | None | 学习目标列表 |
| target_days | int | 否 | None | 目标天数 |

**RecommendationResponse：**

| 字段 | 类型 | 描述 |
|------|------|------|
| learning_paths | List[Dict] | 学习路径列表 |
| model | string | 使用的模型 |
| request_id | string | 请求ID |

---

### AnalysisChain - 职业分析

```python
from src.chains.analysis_chain import ProfessionAnalysisChain, ProfessionAnalysisRequest

chain = ProfessionAnalysisChain()
request = ProfessionAnalysisRequest(
    profession="会计",
    user_profile={"experience": "5年", "skills": ["财务分析"]},
    include_recommendations=True
)
response = chain.analyze(request)
```

**ProfessionAnalysisRequest：**

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| profession | string | 是 | - | 职业名称 |
| user_profile | Dict | 否 | None | 用户画像 |
| include_recommendations | bool | 否 | True | 是否包含建议 |

**ProfessionAnalysisResponse：**

| 字段 | 类型 | 描述 |
|------|------|------|
| risk_level | string | 风险等级（高/中/低） |
| automation_rate | float | 自动化率 (0-100) |
| analysis | string | 分析内容 |
| recommendations | List[str] | 建议列表 |
| model | string | 使用的模型 |
| request_id | string | 请求ID |

---

### TranslateChain - 文本翻译

```python
from src.chains.translate_chain import TranslateChain, TranslateRequest

# 使用默认模型
chain = TranslateChain()

# 使用指定模型
chain = TranslateChain(model_id="deepseek")

request = TranslateRequest(
    content="Hello, world!",
    source_language="auto",
    target_language=""
)
response = chain.translate(request)
```

**TranslateRequest：**

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| content | string | 是 | - | 待翻译文本 |
| source_language | string | 否 | auto | 源语言 |
| target_language | string | 否 | "" | 目标语言，空表示自动判断 |

**TranslateResponse：**

| 字段 | 类型 | 描述 |
|------|------|------|
| translated_text | string | 翻译结果 |
| source_text | string | 原文 |
| source_language | string | 源语言：cn/en |
| target_language | string | 目标语言：cn/en |
| model | string | 使用的模型 |

**语言方向规则：**
- 中文(cn) -> 英文(en)
- 英文或其他(en) -> 中文(cn)

---

## Agent 智能体

### Router Agent

根据请求类型自动分发到不同的 Chain。

```python
from src.agent.builder import create_agent

agent = create_agent()
result = agent.invoke({"input": "你的问题"})
```

---

## 错误码

| 状态码 | 描述 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 500 | 服务器内部错误 |

---

## 限流

暂无限流策略。

---

## 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| OPENAI_API_KEY | API 密钥 | - |
| OPENAI_BASE_URL | API 地址 | - |
| REDIS_HOST | Redis 主机 | localhost |
| REDIS_PORT | Redis 端口 | 6379 |
| APP_HOST | 应用监听地址 | 0.0.0.0 |
| APP_PORT | 应用监听端口 | 8000 |

---

## 多模型配置

### 配置模型

在 `src/conf/config.yml` 中配置多模型：

```yaml
llm:
  default: "glm"  # 默认模型

  models:
    glm:
      modelName: 'GLM-4-Flash-250414'
      apiKey: "your-api-key"
      apiBase: "https://open.bigmodel.cn/api/paas/v4"
      maxTokens: 1024
      type: "openai"

    deepseek:
      modelName: 'deepseek-chat'
      apiKey: "your-api-key"
      apiBase: "https://api.deepseek.com/v1"
      maxTokens: 1024
      type: "openai"

    qwen:
      modelName: 'qwen-plus'
      apiKey: "your-api-key"
      apiBase: "https://dashscope.aliyuncs.com/compatible-mode/v1"
      maxTokens: 1024
      type: "openai"

    custom:
      modelName: 'your-model-name'
      apiKey: "your-api-key"
      apiBase: "https://your-custom-endpoint.com/v1"
      maxTokens: 1024
      type: "openai"
```

### 可用模型

| 模型标识符 | 描述 |
|-----------|------|
| glm | 智谱 GLM 模型（默认） |
| deepseek | DeepSeek 模型 |
| qwen | 阿里 Qwen 模型 |
| custom | 自定义模型（可配置任意 OpenAI 兼容接口） |
