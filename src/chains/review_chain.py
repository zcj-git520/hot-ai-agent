"""
文章审核Chain
对文章进行AI相关性判断和深度评估
"""
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum
from langchain_core.prompts import ChatPromptTemplate

from src.model.llm_factory import LLMFactory
from src.cache.redis_cache import cache
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AIDirectness(Enum):
    """AI相关度等级"""
    DIRECT = "direct"           # 直接相关：AI核心技术和应用
    INDIRECT = "indirect"       # 间接相关：AI辅助或涉及AI
    UNRELATED = "unrelated"      # 无关：不涉及AI技术


class DepthLevel(Enum):
    """文章深度等级"""
    SURFACE = "surface"          # 表层：新闻快讯、简单介绍
    TECHNICAL = "technical"       # 技术性：原理解析、深度评测
    RESEARCH = "research"         # 研究级：学术论文、深度研究


@dataclass
class ReviewRequest:
    """审核请求模型"""
    title: str
    content: str
    max_length: int = 2000


@dataclass
class ReviewResponse:
    """审核响应模型"""
    is_ai_related: bool           # 是否与AI相关
    ai_directness: str             # AI相关度: direct/indirect/unrelated
    ai_relevance_score: float      # AI相关性评分 (0-1)
    depth_level: str               # 深度等级: surface/technical/research
    depth_score: float             # 深度评分 (0-1)
    key_points: List[str]         # 文章核心要点
    summary: str                   # 文章摘要
    keywords: List[str]            # 关键词列表
    reason: str                    # 判断理由


class ReviewChain:
    """文章审核链"""

    def __init__(self, model_id: Optional[str] = None):
        """
        初始化审核链

        Args:
            model_id: 模型标识符，如 "glm", "deepseek", "qwen"。如果为None，使用默认模型
        """
        self._model_id = model_id
        self._llm = None
        self._init_prompt_template()

    @property
    def llm(self):
        """延迟初始化LLM客户端"""
        if self._llm is None:
            self._llm = LLMFactory.create_client(self._model_id)
        return self._llm

    def _init_prompt_template(self):
        """初始化Prompt模板"""
        self.prompt_template = ChatPromptTemplate.from_template("""
你是一个专业的AI内容审核专家。请对提供的文章进行深度分析，判断其是否与AI相关，并评估其内容深度。

文章标题：{title}

文章内容：
{content}

请进行以下两项评估：

1. AI相关性判断：
   - 判断文章是否与AI（人工智能）相关
   - AI直接相关：AI核心技术（机器学习、深度学习、NLP、CV等）、AI产品应用、AI行业动态
   - AI间接相关：涉及AI但非核心主题、数字化转型、科技趋势等
   - 无关：不涉及任何AI相关内容

2. 内容深度评估：
   - 表层（surface）：新闻快讯、产品发布、简单介绍、事件报道
   - 技术性（technical）：原理解析、深度评测、技术对比、实操指南
   - 研究级（research）：学术论文、深度研究、理论探讨、趋势预测

请按照以下格式输出（每项占一行）：
AI相关：是/否
AI相关度：direct/indirect/unrelated
AI相关性评分：[0-1的小数]
深度等级：surface/technical/research
深度评分：[0-1的小数]
核心要点：[要点1]、[要点2]、[要点3]（用中文逗号分隔）
摘要：[50字以内的文章摘要]
关键词：[关键词1]、[关键词2]、[关键词3]（用中文逗号分隔）
判断理由：[简要说明你的判断依据]
""")

        self._chain = None

    @property
    def chain(self):
        """获取chain，延迟绑定llm"""
        if self._chain is None:
            self._chain = self.prompt_template | self.llm.llm
        return self._chain

    def review(self, request: ReviewRequest) -> ReviewResponse:
        """
        执行文章审核

        Args:
            request: 审核请求

        Returns:
            ReviewResponse: 审核响应
        """
        try:
            # 构建缓存键
            cache_key = f"{request.title}:{request.content[:200]}"

            # 检查缓存
            cached = cache.get(cache_key, "review")
            if cached:
                logger.info("从缓存获取审核结果")
                return self._parse_cached_response(cached)

            logger.info("开始文章审核")

            # 准备Prompt参数
            prompt_params = {
                "title": request.title,
                "content": request.content[:request.max_length]
            }

            # 调用LLM
            response = self.chain.invoke(prompt_params)
            response_text = response.content if hasattr(response, 'content') else str(response)

            # 解析响应
            result = self._parse_response(response_text)

            # 缓存结果
            cache.set(
                cache_key,
                response_text,
                "review",
                ttl=settings.cache_ttl
            )

            logger.info(f"审核完成 | AI相关: {result['is_ai_related']} | 深度: {result['depth_level']}")
            return ReviewResponse(**result)

        except Exception as e:
            logger.error(f"审核失败: {str(e)}")
            raise Exception(f"文章审核失败: {str(e)}") from e

    def _parse_response(self, response_text: str) -> dict:
        """解析LLM响应"""
        lines = response_text.strip().split('\n')

        result = {
            "is_ai_related": False,
            "ai_directness": "unrelated",
            "ai_relevance_score": 0.0,
            "depth_level": "surface",
            "depth_score": 0.0,
            "key_points": [],
            "summary": "",
            "keywords": [],
            "reason": ""
        }

        for line in lines:
            line = line.strip()

            if "AI相关：" in line or "AI相关:" in line:
                value = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                result["is_ai_related"] = value in ["是", "yes", "Yes", "YES", "true", "True", "TRUE"]

            elif "AI相关度：" in line or "AI相关度:" in line:
                value = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                if value in ["direct", "indirect", "unrelated"]:
                    result["ai_directness"] = value

            elif "AI相关性评分：" in line or "AI相关性评分:" in line:
                value = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                try:
                    result["ai_relevance_score"] = float(value)
                except ValueError:
                    result["ai_relevance_score"] = 0.0

            elif "深度等级：" in line or "深度等级:" in line:
                value = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                if value in ["surface", "technical", "research"]:
                    result["depth_level"] = value

            elif "深度评分：" in line or "深度评分:" in line:
                value = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                try:
                    result["depth_score"] = float(value)
                except ValueError:
                    result["depth_score"] = 0.0

            elif "核心要点：" in line or "核心要点:" in line:
                value = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                result["key_points"] = [p.strip() for p in value.split("、") if p.strip()]

            elif "摘要：" in line or "摘要:" in line:
                result["summary"] = line.split("：", 1)[-1].split(":", 1)[-1].strip()

            elif "关键词：" in line or "关键词:" in line:
                value = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                result["keywords"] = [k.strip() for k in value.split("、") if k.strip()]

            elif "判断理由：" in line or "判断理由:" in line:
                result["reason"] = line.split("：", 1)[-1].split(":", 1)[-1].strip()

        return result

    def _parse_cached_response(self, cached_text: str) -> ReviewResponse:
        """解析缓存响应"""
        result = self._parse_response(cached_text)
        return ReviewResponse(**result)