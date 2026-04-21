"""
AI 智能体构建器
"""
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate

from src.config.settings import settings
from src.agent.prompts import SYSTEM_PROMPT, AGENT_PROMPT
from src.tools.calculator import calculator_tool
from src.tools.web_search import search_tool


def create_agent():
    """
    创建 AI 智能体

    Returns:
        CompiledStateGraph: 配置好的智能体
    """
    # 初始化 LLM
    llm = ChatOpenAI(
        model=settings.model_name,
        temperature=0.7,
        api_key=settings.api_key,
        base_url=settings.api_base
    )

    # 初始化工具
    tools = [
        calculator_tool,
        search_tool
    ]

    # 构建系统提示
    system_prompt = "\n".join([
        msg[1] if isinstance(msg, tuple) and msg[0] == "system" else ""
        for msg in AGENT_PROMPT
        if isinstance(msg, tuple) and msg[0] == "system"
    ])

    # 创建 Agent（使用位置参数）
    agent = create_agent(
        llm,  # 第一个参数：model
        tools,  # 第二个参数：tools
        system_prompt=system_prompt if system_prompt else None,
        debug=settings.debug,
    )

    return agent


def create_rag_chain():
    """
    创建 RAG 检索链

    Returns:
        检索链对象
    """

    # 初始化嵌入模型
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model_name,
        api_key=settings.api_key,
        base_url=settings.api_base
    )

    # 加载向量存储
    vectorstore = Chroma(
        collection_name=settings.chroma_collection,
        embedding_function=embeddings,
        persist_directory=settings.chroma_persist_dir
    )

    # 初始化 LLM
    llm = ChatOpenAI(
        model=settings.model_name,
        temperature=0.7,
        api_key=settings.api_key,
        base_url=settings.api_base
    )

    # 创建检索器
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.7, "k": 3}
    )

    # 创建检索问答链
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    return qa_chain
