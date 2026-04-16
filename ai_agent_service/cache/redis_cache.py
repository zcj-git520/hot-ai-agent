"""
Redis缓存管理器
实现AI处理结果的缓存功能
"""
import hashlib
import json
import time
from typing import Optional, Dict, Any
from redis import Redis
from loguru import logger

from config.settings import settings


class RedisCache:
    """Redis缓存管理器"""

    def __init__(self):
        """初始化Redis缓存"""
        self.redis_client = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=False
        )
        self.prefix = settings.cache_prefix
        self.ttl = settings.cache_ttl
        self._test_connection()

    def _test_connection(self):
        """测试Redis连接"""
        try:
            self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.warning(f"Redis连接失败: {str(e)}")

    def _generate_key(self, content: str, suffix: str = "") -> str:
        """
        生成缓存键

        Args:
            content: 原始内容
            suffix: 键后缀

        Returns:
            str: 缓存键
        """
        # 使用内容的MD5作为基础键
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        key = f"{self.prefix}{content_hash}"

        if suffix:
            key = f"{key}:{suffix}"

        return key

    def get(self, content: str, suffix: str = "") -> Optional[str]:
        """
        获取缓存

        Args:
            content: 原始内容
            suffix: 键后缀

        Returns:
            Optional[str]: 缓存的值，如果不存在则返回None
        """
        key = self._generate_key(content, suffix)

        try:
            cached_value = self.redis_client.get(key)
            if cached_value:
                logger.debug(f"缓存命中: {key}")
                return cached_value.decode('utf-8')
            return None
        except Exception as e:
            logger.error(f"获取缓存失败: {str(e)}")
            return None

    def set(
        self,
        content: str,
        value: str,
        suffix: str = "",
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存

        Args:
            content: 原始内容
            value: 要缓存的值
            suffix: 键后缀
            ttl: 缓存过期时间（秒），如果为None则使用默认值

        Returns:
            bool: 是否设置成功
        """
        key = self._generate_key(content, suffix)
        expire_time = ttl or self.ttl

        try:
            self.redis_client.setex(key, expire_time, value)
            logger.debug(f"缓存设置成功: {key}, TTL: {expire_time}秒")
            return True
        except Exception as e:
            logger.error(f"设置缓存失败: {str(e)}")
            return False

    def delete(self, content: str, suffix: str = "") -> bool:
        """
        删除缓存

        Args:
            content: 原始内容
            suffix: 键后缀

        Returns:
            bool: 是否删除成功
        """
        key = self._generate_key(content, suffix)

        try:
            self.redis_client.delete(key)
            logger.debug(f"缓存删除成功: {key}")
            return True
        except Exception as e:
            logger.error(f"删除缓存失败: {str(e)}")
            return False

    def exists(self, content: str, suffix: str = "") -> bool:
        """
        检查缓存是否存在

        Args:
            content: 原始内容
            suffix: 键后缀

        Returns:
            bool: 是否存在
        """
        key = self._generate_key(content, suffix)

        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"检查缓存失败: {str(e)}")
            return False

    def increment(self, key: str) -> int:
        """
        增加计数器

        Args:
            key: 计数器键

        Returns:
            int: 增加后的值
        """
        try:
            return self.redis_client.incr(key)
        except Exception as e:
            logger.error(f"增加计数器失败: {str(e)}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            # 获取所有缓存键
            keys = []
            for key in self.redis_client.scan_iter(match=f"{self.prefix}*"):
                keys.append(key.decode('utf-8'))

            return {
                "total_keys": len(keys),
                "prefix": self.prefix,
                "ttl": self.ttl
            }
        except Exception as e:
            logger.error(f"获取缓存统计失败: {str(e)}")
            return {}

    def clear_pattern(self, pattern: str) -> int:
        """
        清除匹配模式的缓存键

        Args:
            pattern: 键模式

        Returns:
            int: 删除的键数量
        """
        try:
            deleted = 0
            for key in self.redis_client.scan_iter(match=pattern):
                self.redis_client.delete(key)
                deleted += 1

            logger.info(f"清除匹配模式缓存成功: {pattern}, 删除数量: {deleted}")
            return deleted
        except Exception as e:
            logger.error(f"清除缓存失败: {str(e)}")
            return 0

    def clear_all(self) -> bool:
        """
        清除所有缓存

        Returns:
            bool: 是否清除成功
        """
        try:
            return self.clear_pattern(f"{self.prefix}*")
        except Exception as e:
            logger.error(f"清除所有缓存失败: {str(e)}")
            return False


# 全局缓存实例
cache = RedisCache()
