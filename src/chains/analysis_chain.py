"""
职业分析Chain
实现基于Agent模式的职业影响分析功能
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.tools import tool

from src.model.llm_factory import LLMFactory
from src.cache.redis_cache import cache
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProfessionAnalysisRequest:
    """职业分析请求模型"""
    profession: str
    user_profile: Optional[Dict[str, Any]] = None
    include_recommendations: bool = True


@dataclass
class ProfessionAnalysisResponse:
    """职业分析响应模型"""
    risk_level: str
    automation_rate: float
    analysis: str
    recommendations: List[str]
    model: str
    request_id: str


class ProfessionAnalysisChain:
    """职业分析链（使用Agent模式）"""

    def __init__(self, model_id: Optional[str] = None):
        """
        初始化职业分析链

        Args:
            model_id: 模型标识符，如 "glm", "deepseek", "qwen"。如果为None，使用默认模型
        """
        self._model_id = model_id
        self._llm = None
        self._init_tools()
        self._init_agent()

    @property
    def llm(self):
        """延迟初始化LLM客户端"""
        if self._llm is None:
            self._llm = LLMFactory.create_client(self._model_id)
        return self._llm

    def _init_tools(self):
        """初始化工具"""
        @tool
        def calculate_risk_score(risk_factors: str) -> str:
            """
            计算职业自动化风险评分

            Args:
                risk_factors: 风险因素描述

            Returns:
                str: 风险评分结果
            """
            return "计算完成"

        @tool
        def get_recommended_skills() -> str:
            """
            获取推荐的技能

            Returns:
                str: 技能列表
            """
            return "编程、数据分析、AI应用、项目管理"

        self.tools = [calculate_risk_score, get_recommended_skills]

    def _init_agent(self):
        """初始化Agent"""
        self.agent = create_agent(
            model=self.llm.llm,
            tools=self.tools,
            system_prompt="""你是一个专业的职业分析专家。请根据提供的职业信息和用户画像，分析该职业受AI自动化影响的情况。

分析要点：
1. 自动化风险评估（高/中/低）
2. 自动化率预测（0-100%）
3. 职业影响深度分析
4. 必要的转型建议

请按照以下格式输出：

风险等级：[高/中/低]
自动化率：[0-100]%
分析：[详细的分析内容]
建议：[3-5条具体建议]"""
        )

    def analyze(self, request: ProfessionAnalysisRequest) -> ProfessionAnalysisResponse:
        """
        执行职业分析

        Args:
            request: 职业分析请求

        Returns:
            ProfessionAnalysisResponse: 职业分析响应
        """
        try:
            logger.info(f"开始分析职业: {request.profession}")

            # 准备输入参数
            user_profile_str = ""
            if request.user_profile:
                user_profile_str = "\n".join(
                    [f"- {k}: {v}" for k, v in request.user_profile.items()]
                )

            # 调用Agent
            result = self.agent.invoke({
                "messages": [
                    {"role": "user", "content": f"职业信息：{request.profession}\n\n用户画像：{user_profile_str}"}
                ]
            })

            # 解析结果
            parsed = self._parse_result(result.get("output", ""))

            # 缓存结果
            cache.set(
                request.profession,
                str(result),
                "analysis",
                ttl=settings.cache_ttl
            )

            # 创建响应
            response = ProfessionAnalysisResponse(
                risk_level=parsed["risk_level"],
                automation_rate=parsed["automation_rate"],
                analysis=parsed["analysis"],
                recommendations=parsed["recommendations"],
                model=self.llm.model,
                request_id=self.llm.request_id
            )

            logger.info(f"职业分析完成: {response.risk_level}")
            return response

        except Exception as e:
            logger.error(f"职业分析失败: {str(e)}")
            raise Exception(f"职业分析失败: {str(e)}") from e

    def _parse_result(self, result_text: str) -> Dict[str, Any]:
        """解析Agent结果"""
        lines = result_text.strip().split('\n')

        parsed = {
            "risk_level": "中",
            "automation_rate": 50.0,
            "analysis": "",
            "recommendations": []
        }

        for line in lines:
            line = line.strip()

            if "风险等级" in line or "risk" in line.lower():
                if "：" in line:
                    level = line.split("：", 1)[1].strip()
                    parsed["risk_level"] = level.split("，")[0].strip()

            elif "自动化率" in line or "automation" in line.lower():
                if "：" in line:
                    rate_str = line.split("：", 1)[1].strip().split("，")[0].strip()
                    try:
                        parsed["automation_rate"] = float(rate_str)
                    except ValueError:
                        pass

            elif "分析：" in line:
                parsed["analysis"] = line.split("：", 1)[1].strip()

            elif "建议：" in line:
                suggestion_part = line.split("：", 1)[1].strip()
                parsed["recommendations"] = [s.strip() for s in suggestion_part.split("；") if s.strip()]

        return parsed
