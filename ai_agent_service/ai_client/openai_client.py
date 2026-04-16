"""
OpenAI客户端实现
使用LangChain OpenAI集成
"""
import time
import json
from typing import Optional, Dict, Any, List
import httpx
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from .base_client import BaseLLMClient, AIRequest, AIResponse, AIMetadata


class OpenAIClient(BaseLLMClient):
    """OpenAI客户端"""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        timeout: float = 30.0
    ):
        """
        初始化OpenAI客户端

        Args:
            api_key: OpenAI API密钥
            base_url: API基础URL
            model: 默认模型
            temperature: 温度参数
            max_tokens: 最大token数
            top_p: Top P参数
            timeout: 超时时间（秒）
        """
        super().__init__(api_key, base_url, model)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.timeout = timeout

        # 初始化LangChain的OpenAI客户端
        llm_kwargs = {
            "model_name": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "timeout": timeout,
        }

        if base_url:
            llm_kwargs["base_url"] = base_url

        self.llm = ChatOpenAI(**llm_kwargs)

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
        # 使用传入的参数或默认参数
        model = model or self.model
        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        top_p = top_p if top_p is not None else self.top_p

        try:
            start_time = time.time()

            # 使用LangChain生成
            messages = [HumanMessage(content=content)]
            response = self.llm.invoke(
                messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                **kwargs
            )

            # 计算延迟
            latency_ms = (time.time() - start_time) * 1000

            # 构造响应
            response_text = response.content

            return self._create_response(response_text, model, latency_ms, success=True)

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            metadata = self._create_metadata(False, latency_ms, str(e))
            raise Exception(f"OpenAI API调用失败: {str(e)}") from e

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
            messages: 消息列表 [{"role": "user", "content": "..."}, ...]
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Returns:
            AIResponse: AI响应
        """
        # 使用传入的参数或默认参数
        model = model or self.model
        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens if max_tokens is not None else self.max_tokens

        try:
            start_time = time.time()

            # 转换消息格式
            langchain_messages = []
            for msg in messages:
                role = msg["role"]
                content = msg["content"]

                if role == "system":
                    langchain_messages.append(SystemMessage(content=content))
                elif role == "user":
                    langchain_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    langchain_messages.append(AIMessage(content=content))

            # 使用LangChain生成
            response = self.llm.invoke(
                langchain_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            # 计算延迟
            latency_ms = (time.time() - start_time) * 1000

            # 构造响应
            response_text = response.content

            return self._create_response(response_text, model, latency_ms, success=True)

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            metadata = self._create_metadata(False, latency_ms, str(e))
            raise Exception(f"OpenAI Chat API调用失败: {str(e)}") from e

    def _create_response(self, response_text: str, model: str, latency_ms: float, success: bool) -> AIResponse:
        """创建响应对象"""
        metadata = self._create_metadata(success, latency_ms)

        # 从LangChain响应中提取使用信息
        usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

        extra_info = {
            "request_id": metadata.request_id,
            "latency_ms": latency_ms,
            "model": model,
            "metadata": metadata.dict()
        }

        return AIResponse(
            text=response_text,
            model=model,
            usage=usage,
            extra_info=extra_info
        )


# LangChain的消息类别名
from langchain.schema import AIMessage
