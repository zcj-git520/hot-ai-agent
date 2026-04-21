"""
应用配置管理
从 config.yml 和环境变量加载配置
"""
import os
from pathlib import Path
from typing import Dict, Optional
import yaml
from src.model.model_config import ModelConfig


class Settings:
    """应用配置类"""

    def __init__(self):
        """初始化配置，优先从 config.yml 读取，环境变量覆盖"""
        # 加载 config.yml
        config_path = Path(__file__).parent.parent / "conf" / "config.yml"
        self.config = {}
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"警告: 加载 config.yml 失败: {e}")
        
        # LLM 配置 - 从 llm 节点读取
        llm_config = self.config.get('llm', {})
        self.model_name = llm_config.get('modelName', 'qwen-plus')
        self.api_key = llm_config.get('apiKey', '')
        self.api_base = llm_config.get('apiBase', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        self.max_tokens = llm_config.get('maxTokens', 1024)
        self.embedding_model_name = llm_config.get('embeddingModelName', 'text-embedding-v4')
        
        # 兼容旧的环境变量方式（可选）
        self.api_key = os.getenv("OPENAI_API_KEY") or self.api_key
        self.api_base = os.getenv("OPENAI_BASE_URL") or self.api_base

        # Redis 配置
        redis_config = self.config.get('redis', {})
        self.redis_host = os.getenv("REDIS_HOST") or redis_config.get('host', 'localhost')
        self.redis_port = int(os.getenv("REDIS_PORT") or str(redis_config.get('port', 6379)))
        self.redis_password = os.getenv("REDIS_PASSWORD") or redis_config.get('password', '')
        self.redis_db = int(os.getenv("REDIS_DB") or str(redis_config.get('db', 0)))
        self.cache_prefix = os.getenv("CACHE_PREFIX") or redis_config.get('cache_prefix', 'ai_agent:')
        self.cache_ttl = int(os.getenv("CACHE_TTL") or str(redis_config.get('cache_ttl', 3600)))

        # 应用配置
        app_config = self.config.get('app', {})
        self.app_host = os.getenv("APP_HOST") or app_config.get('host', '0.0.0.0')
        self.app_port = int(os.getenv("APP_PORT") or str(app_config.get('port', 8000)))
        self.debug = os.getenv("DEBUG", "").lower() == "true" or app_config.get('debug', False)
        self.log_level = os.getenv("LOG_LEVEL") or app_config.get('log_level', 'INFO')

        # RAG 配置
        rag_config = self.config.get('rag', {})
        self.chroma_persist_dir = os.getenv("CHROMA_PERSIST_DIR") or rag_config.get('chroma_persist_dir', './chroma_db')
        self.chroma_collection = os.getenv("CHROMA_COLLECTION") or rag_config.get('chroma_collection', 'documents')
        self.embedding_model = os.getenv("EMBEDDING_MODEL") or rag_config.get('embedding_model', 'text-embedding-3-small')

        # 多模型配置
        self.default_model: str = "default"
        self.models: Dict[str, ModelConfig] = {}
        self._load_multi_model_config()

    def _load_multi_model_config(self):
        """加载多模型配置"""
        llm_config = self.config.get('llm', {})
        models_config = llm_config.get('models', {})

        if models_config:
            # 新格式：多模型配置
            self.default_model = llm_config.get('default', 'glm')
            for model_id, config in models_config.items():
                self.models[model_id] = ModelConfig(
                    name=model_id,
                    model_name=config.get('modelName', ''),
                    api_key=config.get('apiKey', ''),
                    api_base=config.get('apiBase', ''),
                    max_tokens=config.get('maxTokens', 1024),
                    temperature=config.get('temperature', 0.7),
                    top_p=config.get('topP', 1.0),
                    timeout=config.get('timeout', 30.0),
                    model_type=config.get('type', 'openai')
                )
        else:
            # 旧格式：单模型配置（向后兼容）
            self.default_model = "default"
            self.models["default"] = ModelConfig(
                name="default",
                model_name=self.model_name,
                api_key=self.api_key,
                api_base=self.api_base,
                max_tokens=self.max_tokens,
                temperature=0.7,
                top_p=1.0,
                timeout=30.0,
                model_type="openai"
            )

    def get_model_config(self, model_id: Optional[str] = None) -> ModelConfig:
        """获取模型配置"""
        if model_id is None:
            model_id = self.default_model
        return self.models.get(model_id, self.models[self.default_model])


# 全局配置实例
settings = Settings()
