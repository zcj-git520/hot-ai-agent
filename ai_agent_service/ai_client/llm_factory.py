"""
LLM工厂
根据配置创建相应的AI客户端
"""
from typing import Optional
from config.settings import settings
from .base_client import BaseLLMClient
from .openai_client import OpenAIClient


class LLMFactory:
    """LLM工厂类"""

    @staticmethod
    def create_client() -> BaseLLMClient:
        """
        根据配置创建AI客户端

        Returns:
            BaseLLMClient: AI客户端实例
        """
        provider = settings.ai_provider

        if provider == "openai":
            return LLMFactory._create_openai_client()
        elif provider == "anthropic":
            raise NotImplementedError("Anthropic客户端暂未实现，请先使用OpenAI")
        else:
            raise ValueError(f"不支持的AI提供商: {provider}")

    @staticmethod
    def _create_openai_client() -> OpenAIClient:
        """
        创建OpenAI客户端

        Returns:
            OpenAIClient: OpenAI客户端实例
        """
        api_key = settings.get_api_key
        base_url = settings.openai_base_url

        return OpenAIClient(
            api_key=api_key,
            base_url=base_url,
            model=settings.ai_model,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
            top_p=settings.ai_top_p,
            timeout=30.0
        )
