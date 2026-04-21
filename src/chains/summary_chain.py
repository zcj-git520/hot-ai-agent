"""
摘要生成Chain
实现基于LLM的文本摘要功能
"""
from typing import Optional, List
from dataclasses import dataclass
from langchain_core.prompts import ChatPromptTemplate

from src.model.llm_factory import LLMFactory
from src.cache.redis_cache import cache
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SummaryRequest:
    """摘要请求模型"""
    content: str
    max_length: int = 200
    include_keywords: bool = True
    language: str = "中文"


@dataclass
class SummaryResponse:
    """摘要响应模型"""
    summary: str
    keywords: List[str]
    length: int
    model: str
    request_id: str


class SummaryChain:
    """摘要生成链"""

    def __init__(self, model_id: Optional[str] = None):
        """
        初始化摘要链

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
你是一个专业的文本摘要助手。请根据提供的内容生成一份简洁而准确的摘要。

原始内容：
{content}

要求：
1. 摘要长度在 {max_length} 字以内
2. 提取并列出 5-10 个关键词
3. 保持原文的核心信息和逻辑结构
4. 使用简洁明了的语言
5. 如果包含关键词提取要求，请在摘要后单独列出关键词

请直接输出结果，不需要额外的介绍性文字。

摘要：
""")

        self._chain = None

    @property
    def chain(self):
        """获取chain，延迟绑定llm"""
        if self._chain is None:
            self._chain = self.prompt_template | self.llm.llm
        return self._chain

    def generate(self, request: SummaryRequest) -> SummaryResponse:
        """
        生成摘要

        Args:
            request: 摘要请求

        Returns:
            SummaryResponse: 摘要响应
        """
        try:
            # 检查缓存
            cached = cache.get(request.content, "summary")
            if cached:
                logger.info("从缓存获取摘要")
                return self._parse_cached_response(cached)

            logger.info("开始生成摘要")

            # 准备Prompt参数
            prompt_params = {
                "content": request.content,
                "max_length": request.max_length
            }

            # 调用LLM
            response = self.chain.invoke(prompt_params)
            response_text = response.content if hasattr(response, 'content') else str(response)

            # 解析响应
            summary, keywords = self._parse_response(response_text)

            # 缓存结果
            cache.set(
                request.content,
                response_text,
                "summary",
                ttl=settings.cache_ttl
            )

            # 创建响应
            response = SummaryResponse(
                summary=summary,
                keywords=keywords,
                length=len(summary),
                model=self.llm.model,
                request_id=self.llm.request_id
            )

            logger.info(f"摘要生成成功，长度: {len(summary)} 字")
            return response

        except Exception as e:
            logger.error(f"摘要生成失败: {str(e)}")
            raise Exception(f"摘要生成失败: {str(e)}") from e

    def _parse_response(self, response_text: str) -> tuple:
        """解析LLM响应"""
        lines = response_text.strip().split('\n')

        summary = response_text.strip()
        keywords = []

        for line in lines:
            line = line.strip()
            if line.startswith('关键词') or line.startswith('Keywords'):
                keyword_part = line.split(':', 1)[1].strip()
                keywords = [k.strip() for k in keyword_part.split('，') if k.strip()]
                keywords = keywords[:8]
                break

        return summary, keywords

    def _parse_cached_response(self, cached_text: str) -> SummaryResponse:
        """解析缓存响应"""
        summary, keywords = self._parse_response(cached_text)

        return SummaryResponse(
            summary=summary,
            keywords=keywords,
            length=len(summary),
            model=self.llm.model,
            request_id=self.llm.request_id
        )
