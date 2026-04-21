"""
模型类型枚举
"""
from enum import Enum


class ModelType(Enum):
    """支持的模型类型"""
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    OPENAI = "openai"
    GLM = "glm"
