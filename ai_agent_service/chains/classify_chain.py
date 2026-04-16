"""
智能分类Chain
实现基于LLM的文章分类和标签生成功能
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
class ClassifyRequest:
    """分类请求模型"""
    content: str
    categories: Optional[List[str]] = None
    include_confidence: bool = True


@dataclass
class ClassifyResponse:
    """分类响应模型"""
    category: str
    tags: List[str]
    confidence: float
    explanation: str
    model: str
    request_id: str


class ClassifyChain:
    """智能分类链"""

    # 默认分类
    DEFAULT_CATEGORIES = ["news", "impact", "learn", "tool"]

    def __init__(self):
        """初始化分类链"""
        self.llm = LLMFactory.create_client()
        self._init_prompt_template()

    def _init_prompt_template(self):
        """初始化Prompt模板"""
        self.prompt_template = ChatPromptTemplate.from_template("""
你是一个专业的文章分类助手。请根据提供的文章内容进行分类和标签推荐。

文章内容：
{content}

分类要求：
{categories}

请按照以下格式输出：

类别：[主要分类名称]
置信度：[0-1之间的数值，表示分类的确定性]
标签：[用逗号分隔的3-8个标签]
解释：[简要说明分类原因]

请直接输出结果，不需要额外的介绍性文字。
""")

        self.chain = LLMChain(llm=self.llm.llm, prompt=self.prompt_template)

    def classify(self, request: ClassifyRequest) -> ClassifyResponse:
        """
        执行分类

        Args:
            request: 分类请求

        Returns:
            ClassifyResponse: 分类响应
        """
        try:
            # 使用默认分类
            if request.categories is None:
                categories = self.DEFAULT_CATEGORIES
            else:
                categories = request.categories

            # 检查缓存
            cache_key = f"classify:{request.content[:50]}"
            cached = cache.get(request.content, "classify")
            if cached:
                logger.info("从缓存获取分类结果")
                return self._parse_cached_response(cached)

            logger.info(f"开始分类，分类: {categories}")

            # 准备Prompt参数
            categories_str = "\n".join([f"- {cat}" for cat in categories])
            prompt_params = {
                "content": request.content,
                "categories": categories_str
            }

            # 调用LLM
            response_text = self.chain.run(**prompt_params)

            # 解析响应
            result = self._parse_response(response_text, categories)

            # 缓存结果
            cache.set(
                request.content,
                response_text,
                "classify",
                ttl=settings.cache_ttl
            )

            # 创建响应
            response = ClassifyResponse(
                category=result["category"],
                tags=result["tags"],
                confidence=result["confidence"],
                explanation=result["explanation"],
                model=self.llm.model,
                request_id=self.llm.request_id
            )

            logger.info(f"分类完成: {response.category}")
            return response

        except Exception as e:
            logger.error(f"分类失败: {str(e)}")
            raise Exception(f"分类失败: {str(e)}") from e

    def _parse_response(self, response_text: str, categories: List[str]) -> Dict[str, Any]:
        """
        解析LLM响应

        Args:
            response_text: LLM响应文本
            categories: 可用分类列表

        Returns:
            Dict: 解析结果
        """
        lines = response_text.strip().split('\n')

        result = {
            "category": "",
            "tags": [],
            "confidence": 0.0,
            "explanation": ""
        }

        for line in lines:
            line = line.strip()

            # 解析类别
            if line.startswith("类别：") or line.startswith("Category:"):
                result["category"] = line.split("：", 1)[1].split("，")[0].strip()

            # 解析置信度
            elif line.startswith("置信度：") or line.startswith("Confidence:"):
                try:
                    confidence_str = line.split("：", 1)[1].split("，")[0].strip()
                    result["confidence"] = float(confidence_str)
                except:
                    result["confidence"] = 0.8

            # 解析标签
            elif line.startswith("标签：") or line.startswith("Tags:"):
                tag_part = line.split("：", 1)[1].strip()
                result["tags"] = [t.strip() for t in tag_part.split("，") if t.strip()]

            # 解析解释
            elif line.startswith("解释：") or line.startswith("Explanation:"):
                explanation_part = line.split("：", 1)[1].strip()
                result["explanation"] = explanation_part

        # 如果没有明确分类，根据置信度选择
        if not result["category"] and categories:
            result["category"] = categories[0]

        return result

    def _parse_cached_response(self, cached_text: str) -> ClassifyResponse:
        """
        解析缓存响应

        Args:
            cached_text: 缓存的文本

        Returns:
            ClassifyResponse: 分类响应
        """
        # 解析缓存文本
        parsed = self._parse_response(cached_text, self.DEFAULT_CATEGORIES)

        return ClassifyResponse(
            category=parsed["category"],
            tags=parsed["tags"],
            confidence=parsed["confidence"],
            explanation=parsed["explanation"],
            model=self.llm.model,
            request_id=self.llm.request_id
        )
