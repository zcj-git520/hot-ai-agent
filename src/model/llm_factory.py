"""
LLM工厂
根据配置创建相应的AI客户端
"""
from typing import Optional, Dict
from .base_client import BaseLLMClient
from .openai_client import OpenAIClient
from .model_config import ModelConfig


def _get_settings():
    """延迟导入 settings 避免循环依赖"""
    from src.config.settings import settings
    return settings


class LLMFactory:
    """LLM工厂类"""

    # 缓存已创建的客户端实例
    _client_cache: Dict[str, BaseLLMClient] = {}

    @staticmethod
    def create_client(model_id: Optional[str] = None) -> BaseLLMClient:
        """
        根据模型ID创建AI客户端

        Args:
            model_id: 模型标识符，如 "glm", "deepseek", "qwen"
                     如果为None，使用默认模型

        Returns:
            BaseLLMClient: AI客户端实例
        """
        # 获取模型配置
        model_config = _get_settings().get_model_config(model_id)

        # 检查缓存
        cache_key = model_config.name
        if cache_key in LLMFactory._client_cache:
            return LLMFactory._client_cache[cache_key]

        # 创建客户端（统一使用OpenAI兼容接口）
        client = LLMFactory._create_openai_client(model_config)

        # 缓存客户端
        LLMFactory._client_cache[cache_key] = client
        return client

    @staticmethod
    def _create_openai_client(config: ModelConfig) -> OpenAIClient:
        """
        创建OpenAI兼容客户端

        Args:
            config: 模型配置

        Returns:
            OpenAIClient: OpenAI客户端实例
        """
        return OpenAIClient(
            api_key=config.api_key,
            base_url=config.api_base,
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            top_p=config.top_p,
            timeout=config.timeout
        )

    @staticmethod
    def clear_cache():
        """清除客户端缓存"""
        LLMFactory._client_cache.clear()

    @staticmethod
    def get_available_models() -> Dict[str, str]:
        """获取可用的模型列表"""
        return {name: cfg.model_name for name, cfg in _get_settings().models.items()}
