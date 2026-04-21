"""
智能分类Chain
实现基于LLM的内容分类功能
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
class ClassifyRequest:
    """分类请求模型"""
    content: str
    categories: List[str]
    max_length: int = 500


@dataclass
class ClassifyResponse:
    """分类响应模型"""
    category: str
    confidence: float
    reason: str
    model: str


class ClassifyChain:
    """智能分类链"""

    def __init__(self, model_id: Optional[str] = None):
        """
        初始化分类链

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
你是一个专业的内容分类专家。请根据提供的内容，从给定的类别中选择最合适的一个类别。

待分类内容：
{content}

可选类别：
{categories}

要求：
1. 只能从给定的类别中选择一个
2. 给出分类的置信度（0-1之间的小数）
3. 简要说明分类理由

请按照以下格式输出：
类别：[选择的类别]
置信度：[0-1的小数]
理由：[简要理由]
""")

        self._chain = None

    @property
    def chain(self):
        """获取chain，延迟绑定llm"""
        if self._chain is None:
            self._chain = self.prompt_template | self.llm.llm
        return self._chain

    def classify(self, request: ClassifyRequest) -> ClassifyResponse:
        """
        执行分类

        Args:
            request: 分类请求

        Returns:
            ClassifyResponse: 分类响应
        """
        try:
            # 检查缓存
            cached = cache.get(request.content, "classify")
            if cached:
                logger.info("从缓存获取分类结果")
                return self._parse_cached_response(cached)

            logger.info("开始内容分类")

            # 准备Prompt参数
            categories_str = "、".join(request.categories)
            prompt_params = {
                "content": request.content[:request.max_length],
                "categories": categories_str
            }

            # 调用LLM
            response = self.chain.invoke(prompt_params)
            response_text = response.content if hasattr(response, 'content') else str(response)

            # 解析响应
            category, confidence, reason = self._parse_response(response_text)

            # 缓存结果
            cache.set(
                request.content,
                response_text,
                "classify",
                ttl=settings.cache_ttl
            )

            # 创建响应
            response = ClassifyResponse(
                category=category,
                confidence=confidence,
                reason=reason,
                model=self.llm.model
            )

            logger.info(f"分类完成: {category}")
            return response

        except Exception as e:
            logger.error(f"分类失败: {str(e)}")
            raise Exception(f"分类失败: {str(e)}") from e

    def _parse_response(self, response_text: str) -> tuple:
        """解析LLM响应"""
        lines = response_text.strip().split('\n')

        category = ""
        confidence = 0.0
        reason = ""

        for line in lines:
            line = line.strip()

            if "类别" in line or "category" in line.lower():
                if "：" in line:
                    category = line.split("：", 1)[1].strip()
                elif ":" in line:
                    category = line.split(":", 1)[1].strip()

            elif "置信度" in line or "confidence" in line.lower():
                if "：" in line:
                    conf_str = line.split("：", 1)[1].strip()
                elif ":" in line:
                    conf_str = line.split(":", 1)[1].strip()
                else:
                    conf_str = "0.5"

                try:
                    confidence = float(conf_str)
                except ValueError:
                    confidence = 0.5

            elif "理由" in line or "reason" in line.lower():
                if "：" in line:
                    reason = line.split("：", 1)[1].strip()
                elif ":" in line:
                    reason = line.split(":", 1)[1].strip()

        return category, confidence, reason

    def _parse_cached_response(self, cached_text: str) -> ClassifyResponse:
        """解析缓存响应"""
        category, confidence, reason = self._parse_response(cached_text)

        return ClassifyResponse(
            category=category,
            confidence=confidence,
            reason=reason,
            model=self.llm.model
        )
