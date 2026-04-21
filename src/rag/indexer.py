"""
文档索引器 - 负责文档的导入和向量化
"""
import os
from pathlib import Path
from typing import List, Optional

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    DirectoryLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentIndexer:
    """文档索引器"""

    def __init__(self):
        """初始化索引器"""
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model_name,
            api_key=settings.api_key,
            base_url=settings.api_base
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len
        )

    def _get_loader(self, file_path: str):
        """根据文件类型获取合适的加载器"""
        ext = Path(file_path).suffix.lower()

        loaders = {
            '.pdf': PyPDFLoader,
            '.txt': TextLoader,
            '.md': UnstructuredMarkdownLoader,
            '.markdown': UnstructuredMarkdownLoader,
        }

        loader_class = loaders.get(ext)
        if not loader_class:
            logger.warning(f"不支持的文件类型：{ext}")
            return None

        return loader_class(file_path)

    def ingest_documents(
        self,
        paths: List[str],
        collection: Optional[str] = None
    ) -> int:
        """
        导入文档到向量数据库

        Args:
            paths: 文件路径列表
            collection: 集合名称

        Returns:
            处理的文档数量
        """
        collection = collection or settings.chroma_collection

        all_chunks = []
        processed_count = 0

        for path in paths:
            logger.info(f"处理文件：{path}")

            if os.path.isdir(path):
                # 目录处理
                loader = DirectoryLoader(
                    path,
                    glob="**/*.pdf",
                    loader_cls=PyPDFLoader
                )
            else:
                loader = self._get_loader(path)

            if not loader:
                continue

            try:
                documents = loader.load()
                chunks = self.text_splitter.split_documents(documents)
                all_chunks.extend(chunks)
                processed_count += 1
                logger.info(f"文件 {path} 处理完成，分块数：{len(chunks)}")
            except Exception as e:
                logger.error(f"处理文件 {path} 失败：{e}")
                continue

        if not all_chunks:
            return 0

        # 存储到向量数据库
        vectorstore = Chroma.from_documents(
            documents=all_chunks,
            embedding=self.embeddings,
            collection_name=collection,
            persist_directory=settings.chroma_persist_dir
        )

        logger.info(f"索引完成：{len(all_chunks)} 个文本块")
        return processed_count

    def list_collections(self) -> List[str]:
        """列出所有集合"""
        try:
            from chromadb import Client
            client = Client()
            return [col.name for col in client.list_collections()]
        except Exception as e:
            logger.error(f"获取集合列表失败：{e}")
            return []

    def delete_collection(self, collection: str) -> bool:
        """删除集合"""
        try:
            from chromadb import Client
            client = Client()
            client.delete_collection(collection)
            logger.info(f"集合 {collection} 已删除")
            return True
        except Exception as e:
            logger.error(f"删除集合失败：{e}")
            return False

    def search(
        self,
        query: str,
        collection: Optional[str] = None,
        k: int = 3
    ) -> List[dict]:
        """
        搜索相关文档

        Args:
            query: 查询文本
            collection: 集合名称
            k: 返回结果数量

        Returns:
            相关文档列表
        """
        collection = collection or settings.chroma_collection

        vectorstore = Chroma(
            collection_name=collection,
            embedding_function=self.embeddings,
            persist_directory=settings.chroma_persist_dir
        )

        results = vectorstore.similarity_search_with_score(query, k=k)

        return [
            {"content": doc.page_content, "score": score, "metadata": doc.metadata}
            for doc, score in results
        ]
