"""
AI Agent服务主入口
基于FastAPI的Web服务
"""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config.settings import settings
from loguru import logger
from models import *
from chains import *
from utils.logger import logger as app_logger

# 全局对象
summary_chain: Optional[SummaryChain] = None
classify_chain: Optional[ClassifyChain] = None
analysis_chain: Optional[ProfessionAnalysisChain] = None
recommend_chain: Optional[RecommendChain] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("初始化AI Agent服务...")

    try:
        # 初始化各Chain
        global summary_chain, classify_chain, analysis_chain, recommend_chain

        summary_chain = SummaryChain()
        logger.info("摘要生成链初始化完成")

        classify_chain = ClassifyChain()
        logger.info("智能分类链初始化完成")

        analysis_chain = ProfessionAnalysisChain()
        logger.info("职业分析链初始化完成")

        recommend_chain = RecommendChain()
        logger.info("推荐链初始化完成")

        logger.info("AI Agent服务启动成功")

    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}")
        raise

    yield

    # 关闭时执行
    logger.info("AI Agent服务正在关闭...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="AI Agent智能体模块 - 提供AI驱动的摘要、分类、分析和推荐功能",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查端点
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return {
        "code": 200,
        "message": "OK",
        "data": {
            "app": settings.app_name,
            "version": settings.version,
            "ai_provider": settings.ai_provider,
            "ai_model": settings.ai_model
        }
    }


# API路由
@app.post("/api/ai/summarize", tags=["摘要生成"], response_model=BaseResponse)
async def summarize(request: SummarizeRequest):
    """AI摘要生成"""
    try:
        if not summary_chain:
            raise HTTPException(status_code=500, detail="摘要服务未初始化")

        result = summary_chain.generate(request)
        return result

    except Exception as e:
        app_logger.error(f"摘要生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/classify", tags=["智能分类"], response_model=BaseResponse)
async def classify(request: ClassifyRequest):
    """智能文章分类"""
    try:
        if not classify_chain:
            raise HTTPException(status_code=500, detail="分类服务未初始化")

        result = classify_chain.classify(request)
        return result

    except Exception as e:
        app_logger.error(f"智能分类失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/profession/analyze", tags=["职业分析"], response_model=BaseResponse)
async def analyze_profession(request: ProfessionAnalysisRequest):
    """职业影响分析"""
    try:
        if not analysis_chain:
            raise HTTPException(status_code=500, detail="职业分析服务未初始化")

        result = analysis_chain.analyze(request)
        return result

    except Exception as e:
        app_logger.error(f"职业分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/learning-path/recommend", tags=["学习推荐"], response_model=BaseResponse)
async def recommend_learning_path(request: RecommendationRequest):
    """学习路径推荐"""
    try:
        if not recommend_chain:
            raise HTTPException(status_code=500, detail="推荐服务未初始化")

        result = recommend_chain.recommend(request)
        return result

    except Exception as e:
        app_logger.error(f"学习路径推荐失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/status", tags=["API状态"])
async def api_status():
    """查看API状态"""
    return {
        "code": 200,
        "message": "success",
        "data": {
            "services": {
                "summarize": summary_chain is not None,
                "classify": classify_chain is not None,
                "analyze": analysis_chain is not None,
                "recommend": recommend_chain is not None
            },
            "models": {
                "provider": settings.ai_provider,
                "model": settings.ai_model
            }
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
