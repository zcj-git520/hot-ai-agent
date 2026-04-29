"""
微信公众号文章抓取工具
"""
import re
import json
import hashlib
from typing import Optional, Dict, Any
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from langchain_core.tools import Tool

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class WechatArticle:
    """微信公众号文章"""
    title: str
    author: str
    content: str
    summary: str
    publish_time: str
    source_url: str
    cover_image: Optional[str] = None


def extract_biz_from_url(url: str) -> Optional[str]:
    """
    从微信文章 URL 中提取 __biz 参数

    Args:
        url: 微信文章 URL

    Returns:
        __biz 值或 None
    """
    patterns = [
        r'__biz=([^&]+)',
        r'biz=([^&]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_wechat_article(url: str) -> Dict[str, Any]:
    """
    获取微信公众号文章内容

    Args:
        url: 微信文章 URL (如 https://mp.weixin.qq.com/s?__biz=...)

    Returns:
        包含文章信息的字典
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
    }

    try:
        logger.info(f"开始抓取微信文章: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "title": "",
                "author": "",
                "content": "",
                "summary": "",
                "publish_time": "",
                "source_url": url
            }

        soup = BeautifulSoup(response.text, 'lxml')

        # 尝试多种方式提取标题
        title = ""
        title_tag = soup.find('h1', class_='article-title') or \
                    soup.find('h1', class_='rich_media_title') or \
                    soup.find('meta', property='og:title')
        if title_tag:
            title = title_tag.get_text(strip=True) or title_tag.get('content', '')
        else:
            # 备用方案：直接从 og:title 或 title 标签获取
            og_title = soup.find('meta', property='og:title')
            if og_title:
                title = og_title.get('content', '')

        # 提取作者
        author = ""
        author_tag = soup.find('span', class_='rich_media_meta rich_media_meta_text') or \
                     soup.find('meta', property='article:author')
        if author_tag:
            author = author_tag.get_text(strip=True) or author_tag.get('content', '')

        # 提取发布时间
        publish_time = ""
        time_tag = soup.find('em', id='publish_time') or \
                   soup.find('span', class_='rich_media_meta rich_media_meta_pub_date')
        if time_tag:
            publish_time = time_tag.get_text(strip=True)

        # 提取正文内容
        content = ""
        content_tag = soup.find('div', id='js_content') or \
                      soup.find('div', class_='rich_media_content') or \
                      soup.find('div', class_='article-content')
        if content_tag:
            # 移除 script 和 style 标签
            for tag in content_tag.find_all(['script', 'style']):
                tag.decompose()
            content = content_tag.get_text(separator='\n', strip=True)

        # 如果正文为空，尝试 og:description
        summary = ""
        if content:
            summary = content[:200] + "..." if len(content) > 200 else content
        else:
            desc_tag = soup.find('meta', property='og:description')
            if desc_tag:
                summary = desc_tag.get('content', '')

        # 提取封面图
        cover_image = ""
        cover_tag = soup.find('meta', property='og:image')
        if cover_tag:
            cover_image = cover_tag.get('content', '')

        # 检查是否成功提取到内容
        if not title and not content:
            logger.warning(f"未能提取到文章内容，可能是反爬机制: {url}")
            return {
                "success": False,
                "error": "未能提取文章内容，可能需要登录或页面结构变化",
                "title": "",
                "author": "",
                "content": "",
                "summary": "",
                "publish_time": "",
                "source_url": url
            }

        article = WechatArticle(
            title=title,
            author=author,
            content=content,
            summary=summary,
            publish_time=publish_time,
            source_url=url,
            cover_image=cover_image
        )

        logger.info(f"成功抓取文章: {article.title[:30]}...")
        return {
            "success": True,
            "error": "",
            "title": article.title,
            "author": article.author,
            "content": article.content,
            "summary": article.summary,
            "publish_time": article.publish_time,
            "source_url": article.source_url,
            "cover_image": article.cover_image
        }

    except requests.Timeout:
        logger.error(f"请求超时: {url}")
        return {
            "success": False,
            "error": "请求超时，请稍后重试",
            "title": "",
            "author": "",
            "content": "",
            "summary": "",
            "publish_time": "",
            "source_url": url
        }
    except requests.RequestException as e:
        logger.error(f"网络请求失败: {str(e)}")
        return {
            "success": False,
            "error": f"网络请求失败: {str(e)}",
            "title": "",
            "author": "",
            "content": "",
            "summary": "",
            "publish_time": "",
            "source_url": url
        }
    except Exception as e:
        logger.error(f"抓取失败: {str(e)}")
        return {
            "success": False,
            "error": f"抓取失败: {str(e)}",
            "title": "",
            "author": "",
            "content": "",
            "summary": "",
            "publish_time": "",
            "source_url": url
        }


def fetch_wechat_article_with_md5(url: str) -> Dict[str, Any]:
    """
    获取微信文章并生成缓存 key (使用 URL 的 MD5)

    Args:
        url: 微信文章 URL

    Returns:
        包含缓存 key 和文章信息的字典
    """
    result = fetch_wechat_article(url)
    if result["success"]:
        cache_key = hashlib.md5(url.encode()).hexdigest()
        result["cache_key"] = cache_key
    return result


# 导出为 LangChain Tool
wechat_fetcher_tool = Tool(
    name="wechat_article_fetcher",
    func=fetch_wechat_article,
    description="""
    获取微信公众号文章内容。通过提供微信文章链接，返回文章的标题、作者、正文内容、发布时间等信息。

    输入：微信公众号文章链接，如 https://mp.weixin.qq.com/s?__biz=MjM5NTg0NDE1Mw==&mid=2652627839&idx=2&sn=b542d97a02ae6adf771b23a4ba199258

    输出：包含以下字段的字典：
    - success: 是否成功
    - title: 文章标题
    - author: 作者
    - content: 正文内容
    - summary: 内容摘要
    - publish_time: 发布时间
    - source_url: 原始链接
    - cover_image: 封面图片
    - error: 错误信息（如果失败）

    注意：部分文章可能因微信反爬机制无法直接抓取，此时返回 success=false。
    """
)
