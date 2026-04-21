"""
API 路由定义
"""
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from src.chains.translate_chain import TranslateChain, TranslateRequest
from src.chains.review_chain import ReviewChain, ReviewRequest
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


class ReviewRequestModel(BaseModel):
    """文章审核请求模型"""
    title: str = Field(..., description="文章标题", min_length=1)
    content: str = Field(..., description="文章内容", min_length=10)
    model: Optional[str] = Field(None, description="模型标识符: glm, deepseek, qwen, custom")


class ReviewResponseModel(BaseModel):
    """文章审核响应模型"""
    is_ai_related: bool
    ai_directness: str
    ai_relevance_score: float
    depth_level: str
    depth_score: float
    key_points: List[str]
    summary: str
    keywords: List[str]
    reason: str
    model: str


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


@router.post("/review", response_model=ReviewResponseModel)
async def review_article(request: ReviewRequestModel):
    """
    文章审核接口

    对文章进行AI相关性判断和深度评估：
    - AI相关性：判断文章是否与AI相关（direct/indirect/unrelated）
    - 内容深度：评估文章深度（surface/technical/research）
    - 提取核心要点、摘要和关键词
    """
    start_time = time.time()
    content_length = len(request.content)

    logger.info(f"收到文章审核请求 | 标题: {request.title[:50]}... | 长度: {content_length}字符 | 模型: {request.model or 'default'}")

    try:
        review_chain = ReviewChain(model_id=request.model)

        review_request = ReviewRequest(
            title=request.title,
            content=request.content
        )

        logger.info("开始执行文章审核...")
        result = review_chain.review(review_request)

        elapsed_time = time.time() - start_time

        logger.info(
            f"审核完成 | "
            f"耗时: {elapsed_time:.2f}秒 | "
            f"AI相关: {result.is_ai_related}({result.ai_directness}) | "
            f"深度: {result.depth_level}({result.depth_score}) | "
            f"模型: {result.model}"
        )

        return ReviewResponseModel(
            is_ai_related=result.is_ai_related,
            ai_directness=result.ai_directness,
            ai_relevance_score=result.ai_relevance_score,
            depth_level=result.depth_level,
            depth_score=result.depth_score,
            key_points=result.key_points,
            summary=result.summary,
            keywords=result.keywords,
            reason=result.reason,
            model=result.model
        )

    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"文章审核失败 | 耗时: {elapsed_time:.2f}秒 | 错误: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"文章审核失败：{str(e)}")
