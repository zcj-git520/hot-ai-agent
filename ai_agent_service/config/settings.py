"""
配置管理模块
统一管理环境变量和配置
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # 应用配置
    app_name: str = "AI Agent Service"
    version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8889
    debug: bool = True
    log_level: str = "INFO"

    # AI配置
    ai_provider: str = "openai"  # openai, anthropic
    ai_model: str = "gpt-4"
    ai_api_key: str = ""
    ai_base_url: Optional[str] = None
    ai_max_tokens: int = 2000
    ai_temperature: float = 0.7
    ai_top_p: float = 1.0
    ai_stream: bool = False

    # OpenAI配置
    openai_api_key: str = ""
    openai_base_url: Optional[str] = None

    # Anthropic配置
    anthropic_api_key: str = ""
    anthropic_base_url: Optional[str] = None

    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_url: str = ""

    # MySQL配置
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "hot_ai"
    mysql_url: str = ""

    # API配置
    api_prefix: str = "/api"
    cors_origins: list = ["*"]

    # 缓存配置
    cache_ttl: int = 3600  # 1小时
    cache_prefix: str = "ai_response:"

    # 日志配置
    log_file: str = "logs/ai_agent_service.log"

    # 向量数据库配置（可选）
    vector_store_path: str = "./vector_store"
    vector_store_type: str = "chroma"  # chroma, faiss

    # Rate Limit配置
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # 秒

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_redis_url()
        self._init_mysql_url()

    def _init_redis_url(self):
        """初始化Redis URL"""
        if self.redis_password:
            self.redis_url = f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        else:
            self.redis_url = f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def _init_mysql_url(self):
        """初始化MySQL URL"""
        self.mysql_url = f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"

    @property
    def get_api_key(self) -> str:
        """获取AI提供商的API Key"""
        if self.ai_provider == "openai":
            return self.openai_api_key
        elif self.ai_provider == "anthropic":
            return self.anthropic_api_key
        else:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}")


# 全局配置实例
settings = Settings()
