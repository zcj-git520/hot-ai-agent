"""
AI客户端基类
定义统一的LLM调用接口
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import json


@dataclass
class AIRequest:
    """AI请求模型"""
    content: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    stream: bool = False
    extra_params: Optional[Dict[str, Any]] = None


@dataclass
class AIResponse:
    """AI响应模型"""
    text: str
    model: str
    usage: Dict[str, int]
    extra_info: Optional[Dict[str, Any]] = None


@dataclass
class AIMetadata:
    """AI元数据"""
    provider: str
    model: str
    request_id: str
    latency_ms: float
    success: bool
    error_message: Optional[str] = None


class BaseLLMClient(ABC):
    """AI客户端基类"""

    def __init__(self, api_key: str, base_url: Optional[str] = None, model: str = "gpt-4"):
        """
        初始化AI客户端

        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 默认模型
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.request_id = 0

    @abstractmethod
    def generate(
        self,
        content: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        stream: bool = False,
        **kwargs
    ) -> AIResponse:
        """
        生成AI响应

        Args:
            content: 输入内容
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            top_p: Top P参数
            stream: 是否流式输出
            **kwargs: 其他参数

        Returns:
            AIResponse: AI响应
        """
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """
        聊天接口

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Returns:
            AIResponse: AI响应
        """
        pass

    def _create_metadata(self, success: bool, latency_ms: float, error_message: Optional[str] = None) -> AIMetadata:
        """创建元数据"""
        self.request_id += 1
        return AIMetadata(
            provider=self.__class__.__name__,
            model=self.model,
            request_id=str(self.request_id),
            latency_ms=latency_ms,
            success=success,
            error_message=error_message
        )

    def _parse_response(self, response_data: Dict[str, Any], response_text: str) -> AIResponse:
        """解析响应数据"""
        usage = response_data.get("usage", {})
        extra_info = {
            "choices": response_data.get("choices", []),
            "model": response_data.get("model"),
        }

        return AIResponse(
            text=response_text,
            model=self.model,
            usage=usage,
            extra_info=extra_info
        )
