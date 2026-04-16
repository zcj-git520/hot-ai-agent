"""
响应模型
定义API响应的数据结构
"""
from pydantic import BaseModel
from typing import List, Dict, Any


class BaseResponse(BaseModel):
    """基础响应"""
    code: int = 200
    message: str = "success"
    data: Any


class SummarizeResponse(BaseResponse):
    """摘要响应"""
    summary: str
    keywords: List[str]
    length: int


class ClassifyResponse(BaseResponse):
    """分类响应"""
    category: str
    tags: List[str]
    confidence: float
    explanation: str


class ProfessionAnalysisResponse(BaseResponse):
    """职业分析响应"""
    risk_level: str
    automation_rate: float
    analysis: str
    recommendations: List[str]


class LearningPath(BaseModel):
    """学习路径"""
    name: str
    duration_days: int
    stages: List[Dict[str, Any]]
    reason: str


class RecommendationResponse(BaseResponse):
    """推荐响应"""
    learning_paths: List[LearningPath]
