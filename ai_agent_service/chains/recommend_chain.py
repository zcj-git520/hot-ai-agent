"""
推荐Chain
实现基于RAG的学习路径推荐功能
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from langchain.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from ai_client import LLMFactory
from cache import cache
from config.settings import settings
from loguru import logger


@dataclass
class RecommendationRequest:
    """推荐请求模型"""
    user_profession: str
    learning_goals: Optional[List[str]] = None
    target_days: Optional[int] = None


@dataclass
class RecommendationResponse:
    """推荐响应模型"""
    learning_paths: List[Dict[str, Any]]
    model: str
    request_id: str


class RecommendChain:
    """推荐链（使用RAG模式）"""

    def __init__(self):
        """初始化推荐链"""
        self.llm = LLMFactory.create_client()
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        self._init_retriever()

    def _init_retriever(self):
        """初始化检索器"""
        try:
            # 这里应该从数据库加载知识库
            # 暂时使用FAISS模拟
            from langchain.vectorstores import FAISS

            # 创建虚拟向量数据库（实际应该从数据库加载）
            self.vector_store = FAISS.from_texts(
                ["设计师学习路径：UI/UX设计、用户体验、设计心理学、Figma高级技巧"],
                self.embeddings
            )
            logger.info("向量数据库初始化完成")

        except Exception as e:
            logger.error(f"向量数据库初始化失败: {str(e)}")
            self.vector_store = None

    def _init_prompt_template(self):
        """初始化Prompt模板"""
        self.prompt_template = ChatPromptTemplate.from_template("""
你是一个专业的学习路径规划专家。请根据用户职业背景和学习目标，推荐合适的学习路径。

用户职业：{profession}
学习目标：{goals}
目标时间：{days}天

推荐学习路径应包含：
1. 路径名称
2. 总时长
3. 每个阶段的学习内容
4. 推荐理由

请按照以下JSON格式输出：

```json
[
  {
    "name": "路径名称",
    "duration_days": 30,
    "stages": [
      {
        "name": "阶段名称",
        "content": "学习内容",
        "duration_days": 7
      }
    ],
    "reason": "推荐理由"
  }
]
```
""")

    def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        """
        执行推荐

        Args:
            request: 推荐请求

        Returns:
            RecommendationResponse: 推荐响应
        """
        try:
            logger.info(f"开始推荐学习路径: {request.user_profession}")

            # 检查缓存
            cache_key = f"recommend:{request.user_profession[:50]}"
            cached = cache.get(request.user_profession, "recommend")
            if cached:
                logger.info("从缓存获取推荐结果")
                return self._parse_cached_response(cached)

            # 准备查询
            goals_str = ""
            if request.learning_goals:
                goals_str = "\n".join(request.learning_goals)

            days_str = str(request.target_days) if request.target_days else "不限"

            # 使用LLM生成推荐（简化版）
            response = self._generate_recommendation(
                request.user_profession,
                goals_str,
                days_str
            )

            # 缓存结果
            cache.set(
                request.user_profession,
                str(response),
                "recommend",
                ttl=settings.cache_ttl
            )

            logger.info("学习路径推荐完成")
            return response

        except Exception as e:
            logger.error(f"推荐失败: {str(e)}")
            raise Exception(f"推荐失败: {str(e)}") from e

    def _generate_recommendation(self, profession: str, goals: str, days: str) -> RecommendationResponse:
        """
        生成推荐（简化版，使用LLM）

        Args:
            profession: 职业
            goals: 学习目标
            days: 目标天数

        Returns:
            RecommendationResponse: 推荐响应
        """
        try:
            # 这里应该使用RAG检索相关学习路径
            # 暂时使用LLM生成
            response_text = f"""
基于职业 {profession} 的学习推荐：

推荐路径1：入门级AI应用
- 时长：30天
- 内容：Python基础、AI基础概念、常用AI工具
- 理由：适合初学者快速入门

推荐路径2：职业进阶
- 时长：60天
- 内容：深度学习、行业应用、项目管理
- 理由：适合有一定基础想要提升的职业人士
"""

            paths = self._parse_recommendation(response_text)

            return RecommendationResponse(
                learning_paths=paths,
                model=self.llm.model,
                request_id=self.llm.request_id
            )

        except Exception as e:
            logger.error(f"生成推荐失败: {str(e)}")
            raise Exception(f"生成推荐失败: {str(e)}") from e

    def _parse_recommendation(self, response_text: str) -> List[Dict[str, Any]]:
        """
        解析推荐文本

        Args:
            response_text: 推荐文本

        Returns:
            List[Dict]: 学习路径列表
        """
        # 简化解析
        paths = []

        lines = response_text.strip().split('\n')

        current_path = {}
        for line in lines:
            line = line.strip()

            if line.startswith("推荐路径"):
                if current_path:
                    paths.append(current_path)
                current_path = {"name": line.split("：")[1].strip(), "stages": []}
            elif "时长" in line and current_path:
                duration = line.split("：")[1].strip().replace("天", "").strip()
                current_path["duration_days"] = int(duration)
            elif "内容" in line and current_path:
                content = line.split("：")[1].strip()
                current_path["stages"].append({
                    "name": "基础阶段",
                    "content": content,
                    "duration_days": int(current_path.get("duration_days", 30))
                })
            elif "理由" in line and current_path:
                current_path["reason"] = line.split("：")[1].strip()

        if current_path:
            paths.append(current_path)

        return paths

    def _parse_cached_response(self, cached_text: str) -> RecommendationResponse:
        """
        解析缓存响应

        Args:
            cached_text: 缓存的文本

        Returns:
            RecommendationResponse: 推荐响应
        """
        paths = self._parse_recommendation(cached_text)

        return RecommendationResponse(
            learning_paths=paths,
            model=self.llm.model,
            request_id=self.llm.request_id
        )
