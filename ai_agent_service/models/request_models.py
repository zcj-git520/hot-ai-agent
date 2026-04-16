"""
请求模型
定义API请求的数据结构
"""
from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    """摘要请求"""
    content: str = Field(..., min_length=1, description="要摘要的内容")
    max_length: int = Field(200, ge=50, le=1000, description="摘要最大长度")
    include_keywords: bool = Field(True, description="是否包含关键词")


class ClassifyRequest(BaseModel):
    """分类请求"""
    content: str = Field(..., min_length=1, description="要分类的内容")
    categories: list[str] | None = Field(None, description="可选的分类列表")


class ProfessionAnalysisRequest(BaseModel):
    """职业分析请求"""
    profession: str = Field(..., min_length=1, description="职业名称")
    user_profile: dict[str, Any] | None = Field(None, description="用户画像")
    include_recommendations: bool = Field(True, description="是否包含建议")


class RecommendationRequest(BaseModel):
    """推荐请求"""
    user_profession: str = Field(..., min_length=1, description="用户职业")
    learning_goals: list[str] | None = Field(None, description="学习目标")
    target_days: int | None = Field(None, ge=1, le=365, description="目标天数")
