"""
AI文章分类与审核Chain
专门用于AI相关内容的【动态、学习、工具、职业】四分类，并提取关键信息
"""
from typing import Optional, List
from dataclasses import dataclass
from langchain_core.prompts import ChatPromptTemplate

from src.model.llm_factory import LLMFactory
from src.cache.redis_cache import cache
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


# AI内容分类枚举
AI_CONTENT_CATEGORIES = ["动态", "学习", "工具", "职业"]


@dataclass
class AIArticleRequest:
    """AI文章分析请求"""
    title: str
    content: str
    max_length: int = 2000


@dataclass
class AIArticleResponse:
    """AI文章分析响应"""
    category: str                      # 分类：动态/学习/工具/职业
    confidence: float                   # 置信度 0-1
    reason: str                         # 分类理由
    is_ai_related: bool                 # 是否AI相关内容
    key_points: List[str]              # 核心要点
    summary: str                        # 摘要
    keywords: List[str]                 # 关键词
    model: str                           # 使用的模型


class AIArticleChain:
    """AI文章分类与审核链"""

    CATEGORIES_DISPLAY = "、".join(AI_CONTENT_CATEGORIES)

    def __init__(self, model_id: Optional[str] = None):
        self._model_id = model_id
        self._llm = None
        self._init_prompt_template()

    @property
    def llm(self):
        if self._llm is None:
            self._llm = LLMFactory.create_client(self._model_id)
        return self._llm

    def _init_prompt_template(self):
        self.prompt_template = ChatPromptTemplate.from_template("""
你是一个专业的AI内容分类专家。请分析提供的文章，判断其是否属于AI相关范畴，并进行精确分类。

文章标题：{title}

文章内容：
{content}

分类说明：
- 动态：AI行业新闻、产品发布、市场动态、公司动态、技术突破
- 学习：AI教程、学习资源、课程推荐、知识点讲解、入门指南
- 工具：AI工具推荐、使用技巧、工具对比、效率提升、软件应用
- 职业：AI职业发展、岗位招聘、面试经验、技能要求、薪资趋势

重要说明：
1. 首先判断文章是否与AI相关（AI核心技术、产品、应用、行业等）
2. 如果是AI相关内容，从【动态、学习、工具、职业】中选择一个最合适的分类
3. 如果不是AI相关内容，请明确标注

请按照以下格式输出（每项占一行）：
是否AI相关：是/否
分类：动态/学习/工具/职业
置信度：[0-1的小数]
分类理由：[简要说明分类依据]
核心要点：[要点1]、[要点2]、[要点3]（用中文逗号分隔，至少3个）
摘要：[50字以内的文章摘要]
关键词：[关键词1]、[关键词2]、[关键词3]（用中文逗号分隔，至少3个）
""")
        self._chain = None

    @property
    def chain(self):
        if self._chain is None:
            self._chain = self.prompt_template | self.llm.llm
        return self._chain

    def analyze(self, request: AIArticleRequest) -> AIArticleResponse:
        """执行AI文章分析"""
        try:
            cache_key = f"ai_article:{request.title}:{request.content[:200]}"

            # 缓存检查
            cached = cache.get(cache_key, "ai_article")
            if cached:
                logger.info("从缓存获取分析结果")
                return self._parse_cached_response(cached)

            logger.info("开始AI文章分析")

            # 调用LLM
            response = self.chain.invoke({
                "title": request.title,
                "content": request.content[:request.max_length]
            })
            response_text = response.content if hasattr(response, 'content') else str(response)

            # 解析响应
            result = self._parse_response(response_text)
            result["model"] = self.llm.model

            # 缓存结果
            cache.set(cache_key, response_text, "ai_article", ttl=settings.cache_ttl)

            logger.info(f"分析完成 | AI相关: {result['is_ai_related']} | 分类: {result['category']}")
            return AIArticleResponse(**result)

        except Exception as e:
            logger.error(f"分析失败: {str(e)}")
            raise Exception(f"AI文章分析失败: {str(e)}") from e

    def _parse_response(self, response_text: str) -> dict:
        """解析LLM响应"""
        lines = response_text.strip().split('\n')

        result = {
            "category": "动态",
            "confidence": 0.0,
            "reason": "",
            "is_ai_related": True,
            "key_points": [],
            "summary": "",
            "keywords": []
        }

        for line in lines:
            line = line.strip()

            if "是否AI相关" in line:
                value = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                result["is_ai_related"] = value in ["是", "yes", "Yes", "YES", "true", "True"]

            elif "分类：" in line or "分类:" in line:
                value = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                if value in AI_CONTENT_CATEGORIES:
                    result["category"] = value

            elif "置信度：" in line or "置信度:" in line:
                value = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                try:
                    result["confidence"] = float(value)
                except ValueError:
                    result["confidence"] = 0.5

            elif "分类理由：" in line or "分类理由:" in line:
                result["reason"] = line.split("：", 1)[-1].split(":", 1)[-1].strip()

            elif "核心要点：" in line or "核心要点:" in line:
                value = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                result["key_points"] = [p.strip() for p in value.split("、") if p.strip()]

            elif "摘要：" in line or "摘要:" in line:
                result["summary"] = line.split("：", 1)[-1].split(":", 1)[-1].strip()

            elif "关键词：" in line or "关键词:" in line:
                value = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                result["keywords"] = [k.strip() for k in value.split("、") if k.strip()]

        return result

    def _parse_cached_response(self, cached_text: str) -> AIArticleResponse:
        """解析缓存响应"""
        result = self._parse_response(cached_text)
        result["model"] = self.llm.model
        return AIArticleResponse(**result)