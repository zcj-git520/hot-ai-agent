"""
文本翻译Chain
实现将文本翻译为中文的功能，支持大文章分块翻译
"""
from typing import Optional, List
from dataclasses import dataclass, field
import hashlib
import re
from langchain_core.prompts import ChatPromptTemplate

from src.model.llm_factory import LLMFactory
from src.cache.redis_cache import cache
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TranslateRequest:
    """翻译请求模型"""
    content: str
    source_language: str = "auto"  # 源语言，auto表示自动检测
    target_language: str = ""  # 目标语言，空字符串表示由模型自动判断


@dataclass
class TranslateResponse:
    """翻译响应模型"""
    translated_text: str
    source_text: str
    source_language: str
    target_language: str
    model: str


class TranslateChain:
    """文本翻译链"""
    
    # 大文章分块翻译配置
    CHUNK_SIZE = 3000  # 分块大小（字符数），增加到3000以减少块数
    OVERLAP = 150  # 分块重叠字符数，保持上下文连贯性
    LARGE_TEXT_THRESHOLD = 5000  # 触发分块翻译的阈值（字符数）
    MAX_WORKERS = 5  # 并发翻译的最大线程数

    def __init__(self, model_id: Optional[str] = None):
        """
        初始化翻译链

        Args:
            model_id: 模型标识符，如 "glm", "deepseek", "qwen"。如果为None，使用默认模型
        """
        self._model_id = model_id
        self._llm = None
        self._init_prompt_template()

    @property
    def llm(self):
        """延迟初始化LLM客户端"""
        if self._llm is None:
            self._llm = LLMFactory.create_client(self._model_id)
        return self._llm

    def _init_prompt_template(self):
        """初始化Prompt模板"""
        self.prompt_template = ChatPromptTemplate.from_template("""
你是一个专业的翻译助手。请将以下文本翻译为目标语言。

要求：
1. 保持原文的意思和语气
2. 使用自然流畅的目标语言表达
3. 保留专有名词（如人名、地名、品牌名等）的原文或提供通用译名
4. 语言方向：原文为中文时，目标语言为英文；原文为非中文时，目标语言为中文
5. 只输出翻译结果，不要添加任何解释或额外内容

原文：
{content}

翻译结果：
""")

        self._chain = None

    @property
    def chain(self):
        """获取chain，延迟绑定llm"""
        if self._chain is None:
            self._chain = self.prompt_template | self.llm.llm
        return self._chain

    def translate(self, request: TranslateRequest) -> TranslateResponse:
        """
        翻译文本（支持大文章分块翻译）

        Args:
            request: 翻译请求

        Returns:
            TranslateResponse: 翻译响应
        """
        try:
            content_length = len(request.content)
            
            # 判断是否需要分块翻译
            if content_length > self.LARGE_TEXT_THRESHOLD:
                logger.info(f"检测到长文本({content_length}字符)，启用分块翻译模式")
                return self._translate_large_text(request)
            else:
                logger.info(f"开始翻译短文本({content_length}字符)")
                return self._translate_small_text(request)

        except Exception as e:
            logger.error(f"翻译失败: {str(e)}")
            raise Exception(f"翻译失败: {str(e)}") from e

    def _translate_small_text(self, request: TranslateRequest) -> TranslateResponse:
        """
        翻译短文本（不分块）
        
        Args:
            request: 翻译请求
            
        Returns:
            TranslateResponse: 翻译响应
        """
        # 生成缓存key（使用hash避免过长）
        content_hash = hashlib.md5(request.content.encode('utf-8')).hexdigest()
        cache_key = f"{content_hash}"
        
        # 检查缓存
        cached = cache.get(cache_key, "translate")
        if cached:
            logger.info("从缓存获取翻译结果")
            cached_data = cache.get(cache_key, "translate_meta")
            if cached_data:
                import json
                meta = json.loads(cached_data)
                return TranslateResponse(
                    translated_text=cached,
                    source_text=request.content,
                    source_language=meta.get("source_language", "auto"),
                    target_language=meta.get("target_language", ""),
                    model=self.llm.model
                )
        
        # 调用LLM翻译
        response = self.chain.invoke({"content": request.content})
        response_text = response.content if hasattr(response, 'content') else str(response)
        translated_text = response_text.strip()
        
        # 判断翻译方向
        import json
        is_chinese = self._is_chinese_text(request.content)
        source_lang = "cn" if is_chinese else "en"
        target_lang = "en" if is_chinese else "cn"
        
        # 缓存结果
        cache.set(cache_key, translated_text, "translate", ttl=settings.cache_ttl)
        cache.set(cache_key, json.dumps({"source_language": source_lang, "target_language": target_lang}), "translate_meta", ttl=settings.cache_ttl)
        
        logger.info(f"翻译成功: {source_lang} -> {target_lang}")
        
        return TranslateResponse(
            translated_text=translated_text,
            source_text=request.content,
            source_language=source_lang,
            target_language=target_lang,
            model=self.llm.model
        )
    
    def _translate_large_text(self, request: TranslateRequest) -> TranslateResponse:
        """
        翻译大文章（分块翻译，支持并发）
        
        Args:
            request: 翻译请求
            
        Returns:
            TranslateResponse: 翻译响应
        """
        import json
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        start_time = time.time()
        
        # 生成缓存key
        content_hash = hashlib.md5(request.content.encode('utf-8')).hexdigest()
        cache_key = f"large_{content_hash}_{self.CHUNK_SIZE}"
        
        # 检查整体缓存
        cached = cache.get(cache_key, "translate_large")
        if cached:
            logger.info("从缓存获取大文章翻译结果")
            cached_data = cache.get(cache_key, "translate_large_meta")
            if cached_data:
                meta = json.loads(cached_data)
                elapsed = time.time() - start_time
                logger.info(f"缓存命中，耗时: {elapsed:.2f}秒")
                return TranslateResponse(
                    translated_text=cached,
                    source_text=request.content,
                    source_language=meta.get("source_language", "auto"),
                    target_language=meta.get("target_language", ""),
                    model=self.llm.model
                )
        
        # 分割文本为块
        chunks = self._split_text_into_chunks(request.content, self.CHUNK_SIZE, self.OVERLAP)
        total_chunks = len(chunks)
        logger.info(f"将文本分割为 {total_chunks} 个块进行翻译（并发数: {self.MAX_WORKERS}）")
        
        # 使用线程池并发翻译
        translated_chunks = [None] * total_chunks  # 预分配列表保持顺序
        cache_hits = 0
        
        def translate_chunk(args):
            """翻译单个块的函数"""
            i, chunk = args
            chunk_start = time.time()
            
            # 检查块缓存
            chunk_hash = hashlib.md5(chunk.encode('utf-8')).hexdigest()
            chunk_cache_key = f"chunk_{chunk_hash}"
            cached_chunk = cache.get(chunk_cache_key, "translate_chunk")
            
            if cached_chunk:
                elapsed = time.time() - chunk_start
                logger.info(f"第 {i+1}/{total_chunks} 块从缓存获取 (耗时: {elapsed:.2f}s)")
                return i, cached_chunk, True
            else:
                # 翻译当前块
                response = self.chain.invoke({"content": chunk})
                response_text = response.content if hasattr(response, 'content') else str(response)
                translated_chunk = response_text.strip()
                
                # 缓存翻译后的块
                cache.set(chunk_cache_key, translated_chunk, "translate_chunk", ttl=settings.cache_ttl)
                elapsed = time.time() - chunk_start
                logger.info(f"第 {i+1}/{total_chunks} 块翻译完成 (耗时: {elapsed:.2f}s)")
                return i, translated_chunk, False
        
        # 并发执行翻译
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            # 提交所有任务
            future_to_index = {
                executor.submit(translate_chunk, (i, chunk)): i 
                for i, chunk in enumerate(chunks)
            }
            
            # 收集结果
            for future in as_completed(future_to_index):
                try:
                    index, translated_text, is_cached = future.result()
                    translated_chunks[index] = translated_text
                    if is_cached:
                        cache_hits += 1
                except Exception as e:
                    logger.error(f"翻译块失败: {e}")
                    raise
        
        logger.info(f"所有块翻译完成，缓存命中: {cache_hits}/{total_chunks}")
        
        # 合并翻译结果
        merge_start = time.time()
        final_translation = self._merge_translated_chunks(translated_chunks, self.OVERLAP)
        merge_elapsed = time.time() - merge_start
        logger.info(f"结果合并完成 (耗时: {merge_elapsed:.2f}s)")
        
        # 判断翻译方向
        is_chinese = self._is_chinese_text(request.content)
        source_lang = "cn" if is_chinese else "en"
        target_lang = "en" if is_chinese else "cn"
        
        # 缓存整体结果
        cache.set(cache_key, final_translation, "translate_large", ttl=settings.cache_ttl * 24)  # 大文章缓存更久
        cache.set(cache_key, json.dumps({"source_language": source_lang, "target_language": target_lang}), "translate_large_meta", ttl=settings.cache_ttl * 24)
        
        total_elapsed = time.time() - start_time
        logger.info(f"大文章翻译完成: {source_lang} -> {target_lang}, 共 {total_chunks} 块, 总耗时: {total_elapsed:.2f}秒")
        
        return TranslateResponse(
            translated_text=final_translation,
            source_text=request.content,
            source_language=source_lang,
            target_language=target_lang,
            model=self.llm.model
        )
    
    def _split_text_into_chunks(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        将文本分割为块，尽量在句子边界分割
        
        Args:
            text: 原始文本
            chunk_size: 每块大小
            overlap: 重叠字符数
            
        Returns:
            List[str]: 文本块列表
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + chunk_size, text_length)
            
            # 如果不是最后一块，尝试在句子边界分割
            if end < text_length:
                # 查找最近的句子结束符（。！？.!?）
                search_range = text[start:end]
                sentence_endings = ['。', '！', '？', '.', '!', '?', '\n']
                
                best_split = -1
                for ending in sentence_endings:
                    pos = search_range.rfind(ending)
                    if pos > chunk_size * 0.5:  # 至少在50%位置之后
                        best_split = max(best_split, pos)
                
                if best_split > 0:
                    end = start + best_split + 1
            
            chunk = text[start:end].strip()
            if chunk:  # 只添加非空块
                chunks.append(chunk)
            
            # 移动到下一个块，考虑重叠
            start = end - overlap if end < text_length else text_length
        
        return chunks
    
    def _merge_translated_chunks(self, translated_chunks: List[str], overlap: int) -> str:
        """
        合并翻译后的块，处理重叠部分
        
        Args:
            translated_chunks: 翻译后的文本块列表
            overlap: 重叠字符数
            
        Returns:
            str: 合并后的完整文本
        """
        if not translated_chunks:
            return ""
        
        if len(translated_chunks) == 1:
            return translated_chunks[0]
        
        merged = translated_chunks[0]
        
        for i in range(1, len(translated_chunks)):
            current_chunk = translated_chunks[i]
            
            # 简单拼接（重叠部分由LLM自然处理，通常不会有明显重复）
            # 如果需要更精确的去重，可以实现基于编辑距离的重叠检测
            merged += "\n" + current_chunk
        
        return merged

    def _is_chinese_text(self, text: str) -> bool:
        """
        判断文本是否为中文

        Args:
            text: 待检测文本

        Returns:
            bool: 是否为中文
        """
        chinese_count = 0
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                chinese_count += 1
        # 如果中文字符超过总字符数的30%，认为是中文
        return chinese_count > len(text) * 0.3 if text else False

    def _parse_cached_response(self, cached_text: str, request: TranslateRequest) -> TranslateResponse:
        """解析缓存响应"""
        is_chinese = self._is_chinese_text(request.content)
        source_lang = "cn" if is_chinese else "en"
        target_lang = "en" if is_chinese else "cn"

        return TranslateResponse(
            translated_text=cached_text,
            source_text=request.content,
            source_language=source_lang,
            target_language=target_lang,
            model=self.llm.model
        )
