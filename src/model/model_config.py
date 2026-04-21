"""
模型配置数据类
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ModelType(Enum):
    """模型类型"""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    GLM = "glm"
    CUSTOM = "custom"


@dataclass
class ModelConfig:
    """模型配置数据类"""
    name: str  # 配置标识名
    model_name: str  # 实际模型名
    api_key: str
    api_base: str
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 1.0
    timeout: float = 30.0
    model_type: str = "openai"  # openai, deepseek, qwen, glm, custom

    @property
    def type(self) -> ModelType:
        """获取模型类型枚举"""
        try:
            return ModelType(self.model_type)
        except ValueError:
            return ModelType.CUSTOM
