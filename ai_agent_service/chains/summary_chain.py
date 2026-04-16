"""
摘要生成Chain
实现基于LLM的文本摘要功能
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

from ai_client import LLMFactory
from cache import cache
from config.settings import settings
from loguru import logger


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

    def __init__(self):
        """初始化摘要链"""
        self.llm = LLMFactory.create_client()
        self._init_prompt_template()

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

        self.chain = LLMChain(llm=self.llm.llm, prompt=self.prompt_template)

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
            cache_key = f"summary:{request.content[:50]}"
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
            response_text = self.chain.run(**prompt_params)

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
        """
        解析LLM响应

        Args:
            response_text: LLM响应文本

        Returns:
            tuple: (摘要, 关键词列表)
        """
        # 分离摘要和关键词部分
        lines = response_text.strip().split('\n')

        # 如果没有明确的分隔符，默认第一部分为摘要
        summary = response_text.strip()
        keywords = []

        # 尝试提取关键词
        for line in lines:
            line = line.strip()
            if line.startswith('关键词') or line.startswith('Keywords'):
                # 提取关键词部分
                keyword_part = line.split(':', 1)[1].strip()
                keywords = [k.strip() for k in keyword_part.split('，') if k.strip()]
                # 取前8个关键词
                keywords = keywords[:8]
                break

        return summary, keywords

    def _parse_cached_response(self, cached_text: str) -> SummaryResponse:
        """
        解析缓存响应

        Args:
            cached_text: 缓存的文本

        Returns:
            SummaryResponse: 摘要响应
        """
        summary, keywords = self._parse_response(cached_text)

        return SummaryResponse(
            summary=summary,
            keywords=keywords,
            length=len(summary),
            model=self.llm.model,
            request_id=self.llm.request_id
        )
