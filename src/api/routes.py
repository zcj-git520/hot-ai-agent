"""
API 路由定义
"""
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from src.chains.translate_chain import TranslateChain, TranslateRequest
from src.chains.ai_article_chain import AIArticleChain, AIArticleRequest
from src.tools.wechat_fetcher import fetch_wechat_article
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class QueryRequest(BaseModel):
    """查询请求"""
    question: str = Field(..., description="用户问题", min_length=1)
    top_k: int = Field(default=3, description="返回结果数量", ge=1, le=10)
    conversation_id: Optional[str] = Field(None, description="会话 ID")


class QueryResponse(BaseModel):
    """查询响应"""
    answer: str
    sources: List[str] = []
    conversation_id: Optional[str] = None


class IngestRequest(BaseModel):
    """文档导入请求"""
    collection: str = Field(default="default", description="集合名称")
    paths: List[str] = Field(..., description="文件路径列表")


class IngestResponse(BaseModel):
    """文档导入响应"""
    success: bool
    documents_processed: int
    collection: str


class TranslateRequestModel(BaseModel):
    """翻译请求模型"""
    content: str = Field(..., description="待翻译的文本", min_length=1)
    source_language: str = Field(default="auto", description="源语言，auto表示自动检测")
    target_language: str = Field(default="", description="目标语言，空表示自动判断：中文->英文，非中文->中文")
    model: Optional[str] = Field(None, description="模型标识符: glm, deepseek, qwen, custom")


class AIArticleRequestModel(BaseModel):
    """AI文章分析请求模型"""
    title: str = Field(..., description="文章标题", min_length=1)
    content: str = Field(..., description="文章内容", min_length=10)
    model: Optional[str] = Field(None, description="模型标识符: glm, deepseek, qwen, custom")


class AIArticleResponseModel(BaseModel):
    """AI文章分析响应模型"""
    category: str                       # 分类：动态/学习/工具/职业
    confidence: float                   # 置信度 0-1
    reason: str                         # 分类理由
    is_ai_related: bool                 # 是否AI相关内容
    key_points: List[str]              # 核心要点
    summary: str                        # 摘要
    keywords: List[str]                 # 关键词
    model: str                          # 使用的模型


class WechatArticleRequestModel(BaseModel):
    """微信公众号文章获取请求模型"""
    url: str = Field(..., description="微信公众号文章链接", min_length=1)


class WechatArticleResponseModel(BaseModel):
    """微信公众号文章获取响应模型"""
    success: bool
    title: str
    author: str
    content: str
    summary: str
    publish_time: str
    source_url: str
    cover_image: Optional[str] = None
    error: str = ""


@router.post("/translate")
async def translate_text(request: TranslateRequestModel):
    """
    文本翻译接口

    语言方向：中文->英文，非中文->中文
    支持大文章自动分块翻译
    """
    start_time = time.time()
    content_length = len(request.content)
    is_large_text = content_length > 5000
    
    # 记录请求日志
    logger.info(f"收到翻译请求 | 长度: {content_length}字符 | 类型: {'长文章' if is_large_text else '短文本'} | 模型: {request.model or 'default'}")
    logger.debug(f"请求内容预览: {request.content[:100]}...")
    
    try:
        translate_chain = TranslateChain(model_id=request.model)

        translate_request = TranslateRequest(
            content=request.content,
            source_language=request.source_language,
            target_language=request.target_language
        )
        
        logger.info("开始执行翻译...")
        result = translate_chain.translate(translate_request)
        
        elapsed_time = time.time() - start_time
        
        # 记录响应日志
        logger.info(
            f"翻译完成 | "
            f"耗时: {elapsed_time:.2f}秒 | "
            f"原文长度: {content_length} | "
            f"译文长度: {len(result.translated_text)} | "
            f"语言方向: {result.source_language}->{result.target_language} | "
            f"模型: {result.model}"
        )
        
        return {
            "success": True,
            "translated_text": result.translated_text,
            "source_language": result.source_language,
            "target_language": result.target_language,
            "model": result.model,
            "content_length": content_length,
            "is_large_text": is_large_text,
            "processing_time": round(elapsed_time, 2)
        }
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"翻译失败 | 耗时: {elapsed_time:.2f}秒 | 错误: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"翻译失败：{str(e)}")


@router.post("/ai-article", response_model=AIArticleResponseModel)
async def analyze_ai_article(request: AIArticleRequestModel):
    """
    AI文章分析接口

    对文章进行AI相关性判断和分类：
    - 判断是否为AI相关内容
    - 分类：动态/学习/工具/职业
    - 提取核心要点、摘要和关键词
    """
    start_time = time.time()
    content_length = len(request.content)

    logger.info(f"收到AI文章分析请求 | 标题: {request.title[:50]}... | 长度: {content_length}字符 | 模型: {request.model or 'default'}")

    try:
        ai_article_chain = AIArticleChain(model_id=request.model)

        ai_request = AIArticleRequest(
            title=request.title,
            content=request.content
        )

        logger.info("开始执行AI文章分析...")
        result = ai_article_chain.analyze(ai_request)

        elapsed_time = time.time() - start_time

        logger.info(
            f"分析完成 | "
            f"耗时: {elapsed_time:.2f}秒 | "
            f"AI相关: {result.is_ai_related} | "
            f"分类: {result.category}({result.confidence}) | "
            f"模型: {result.model}"
        )

        return AIArticleResponseModel(
            category=result.category,
            confidence=result.confidence,
            reason=result.reason,
            is_ai_related=result.is_ai_related,
            key_points=result.key_points,
            summary=result.summary,
            keywords=result.keywords,
            model=result.model
        )

    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"AI文章分析失败 | 耗时: {elapsed_time:.2f}秒 | 错误: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"AI文章分析失败：{str(e)}")


@router.post("/wechat-article", response_model=WechatArticleResponseModel)
async def get_wechat_article(request: WechatArticleRequestModel):
    """
    获取微信公众号文章内容

    通过提供微信文章链接，直接获取文章的标题、作者、正文内容等信息。
    """
    start_time = time.time()
    logger.info(f"收到微信文章获取请求 | URL: {request.url[:80]}...")

    try:
        result = fetch_wechat_article(request.url)
        elapsed_time = time.time() - start_time

        logger.info(
            f"微信文章获取{'成功' if result['success'] else '失败'} | "
            f"耗时: {elapsed_time:.2f}秒 | "
            f"标题: {result.get('title', '')[:30]}..."
        )

        return WechatArticleResponseModel(
            success=result["success"],
            title=result.get("title", ""),
            author=result.get("author", ""),
            content=result.get("content", ""),
            summary=result.get("summary", ""),
            publish_time=result.get("publish_time", ""),
            source_url=result.get("source_url", ""),
            cover_image=result.get("cover_image"),
            error=result.get("error", "")
        )

    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"微信文章获取失败 | 耗时: {elapsed_time:.2f}秒 | 错误: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"获取微信文章失败：{str(e)}")
