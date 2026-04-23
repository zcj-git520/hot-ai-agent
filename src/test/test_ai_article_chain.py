"""
AI文章分析Chain测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass

from src.chains.ai_article_chain import (
    AIArticleChain,
    AIArticleRequest,
    AIArticleResponse,
    AI_CONTENT_CATEGORIES
)


class TestAIArticleChain:
    """AIArticleChain 测试类"""

    @pytest.fixture
    def chain(self):
        """创建Chain实例"""
        return AIArticleChain(model_id="glm")

    @pytest.fixture
    def sample_request(self):
        """样例请求"""
        return AIArticleRequest(
            title="OpenAI发布GPT-5新一代大语言模型",
            content="""
            OpenAI在今日正式发布了GPT-5，这是继GPT-4之后的又一次重大突破。
            GPT-5采用了全新的架构，在推理能力和多模态理解方面有了显著提升。
            据悉，GPT-5将在下个月开始向Plus用户开放测试。
            """
        )

    def test_categories_constant(self):
        """测试分类常量定义"""
        assert AI_CONTENT_CATEGORIES == ["动态", "学习", "工具", "职业"]
        assert len(AI_CONTENT_CATEGORIES) == 4

    def test_request_dataclass(self, sample_request):
        """测试请求数据类"""
        assert sample_request.title == "OpenAI发布GPT-5新一代大语言模型"
        assert sample_request.max_length == 2000
        assert len(sample_request.content) > 0

    def test_response_dataclass(self):
        """测试响应数据类"""
        response = AIArticleResponse(
            category="动态",
            confidence=0.9,
            reason="行业新闻",
            is_ai_related=True,
            key_points=["要点1", "要点2"],
            summary="摘要",
            keywords=["AI", "GPT"],
            model="glm"
        )
        assert response.category == "动态"
        assert response.confidence == 0.9
        assert response.is_ai_related is True
        assert len(response.key_points) == 2

    def test_chain_initialization(self, chain):
        """测试Chain初始化"""
        assert chain._model_id == "glm"
        assert chain._llm is None
        assert chain._chain is None
        assert chain.CATEGORIES_DISPLAY == "动态、学习、工具、职业"

    @patch('src.chains.ai_article_chain.LLMFactory')
    def test_llm_lazy_initialization(self, mock_factory, chain):
        """测试LLM延迟初始化"""
        mock_client = Mock()
        mock_client.model = "glm"
        mock_factory.create_client.return_value = mock_client

        # 第一次访问触发初始化
        llm1 = chain.llm
        mock_factory.create_client.assert_called_once_with("glm")

        # 第二次访问返回相同实例
        llm2 = chain.llm
        assert llm1 is llm2
        assert mock_factory.create_client.call_count == 1

    def test_parse_response_正常情况(self, chain):
        """测试响应解析 - 正常情况"""
        response_text = """
是否AI相关：是
分类：动态
置信度：0.85
分类理由：文章报道了AI行业最新动态
核心要点：GPT-5发布、新架构设计、下月测试
摘要：OpenAI发布GPT-5新一代大模型
关键词：OpenAI、GPT-5、大语言模型
        """

        result = chain._parse_response(response_text)
        print(result)

        assert result["is_ai_related"] is True
        assert result["category"] == "动态"
        assert result["confidence"] == 0.85
        assert result["reason"] == "文章报道了AI行业最新动态"
        assert len(result["key_points"]) == 3
        assert result["summary"] == "OpenAI发布GPT-5新一代大模型"
        assert len(result["keywords"]) == 3

    def test_parse_response_非AI相关(self, chain):
        """测试响应解析 - 非AI相关内容"""
        response_text = """
是否AI相关：否
分类：动态
置信度：0.0
分类理由：文章与AI无关
核心要点：无
摘要：无
关键词：无
        """

        result = chain._parse_response(response_text)

        assert result["is_ai_related"] is False
        assert result["confidence"] == 0.0

    def test_parse_response_学习分类(self, chain):
        """测试响应解析 - 学习分类"""
        response_text = """
是否AI相关：是
分类：学习
置信度：0.92
分类理由：文章提供AI学习教程
核心要点：机器学习基础、实战项目、课程推荐
摘要：系统学习机器学习的完整路径
关键词：机器学习、学习路径、教程
        """

        result = chain._parse_response(response_text)

        assert result["category"] == "学习"
        assert result["confidence"] == 0.92

    def test_parse_response_工具分类(self, chain):
        """测试响应解析 - 工具分类"""
        response_text = """
是否AI相关：是
分类：工具
置信度：0.88
分类理由：文章推荐AI效率工具
核心要点：Copilot评测、Cursor对比、Prompt技巧
摘要：几款提升编程效率的AI工具推荐
关键词：Copilot、Cursor、效率工具
        """

        result = chain._parse_response(response_text)

        assert result["category"] == "工具"
        assert result["confidence"] == 0.88

    def test_parse_response_职业分类(self, chain):
        """测试响应解析 - 职业分类"""
        response_text = """
是否AI相关：是
分类：职业
置信度：0.80
分类理由：文章讨论AI岗位薪资趋势
核心要点：算法岗薪资、AI招聘需求、面试技巧
摘要：2024年AI岗位薪资趋势分析
关键词：算法工程师、薪资、招聘
        """

        result = chain._parse_response(response_text)

        assert result["category"] == "职业"
        assert result["confidence"] == 0.80

    def test_parse_response_英文格式(self, chain):
        """测试响应解析 - 英文冒号格式"""
        response_text = """
是否AI相关: Yes
分类: 动态
置信度: 0.75
分类理由: News about AI
核心要点: 要点1、要点2、要点3
摘要: AI news summary
关键词: AI、NLP、News
        """

        result = chain._parse_response(response_text)

        assert result["is_ai_related"] is True
        assert result["category"] == "动态"

    def test_parse_response_置信度解析失败(self, chain):
        """测试响应解析 - 置信度解析失败时使用默认值"""
        response_text = """
是否AI相关：是
分类：动态
置信度：无效数值
分类理由：测试
核心要点：要点1、要点2
摘要：摘要
关键词：关键词1、关键词2
        """

        result = chain._parse_response(response_text)

        assert result["confidence"] == 0.5  # 默认值

    def test_parse_response_空内容(self, chain):
        """测试响应解析 - 空内容"""
        response_text = ""

        result = chain._parse_response(response_text)

        assert result["category"] == "动态"  # 默认值
        assert result["confidence"] == 0.0
        assert result["is_ai_related"] is True  # 默认值

    def test_parse_response_缺少字段(self, chain):
        """测试响应解析 - 缺少部分字段"""
        response_text = """
是否AI相关：是
分类：学习
        """

        result = chain._parse_response(response_text)

        assert result["is_ai_related"] is True
        assert result["category"] == "学习"
        assert result["key_points"] == []  # 未提供则为空列表

    @patch('src.chains.ai_article_chain.cache')
    @patch.object(AIArticleChain, 'chain', new_callable=lambda: property(lambda self: Mock()))
    def test_analyze_缓存命中(self, mock_chain_prop, mock_cache, chain, sample_request):
        """测试分析 - 缓存命中"""
        cached_text = """
是否AI相关：是
分类：动态
置信度：0.85
分类理由：从缓存获取
核心要点：要点1、要点2、要点3
摘要：缓存摘要
关键词：AI、缓存
        """

        mock_cache.get.return_value = cached_text
        chain._llm = Mock(model="glm")

        result = chain.analyze(sample_request)

        mock_cache.get.assert_called_once()
        assert result.category == "动态"
        assert result.confidence == 0.85

    @patch('src.chains.ai_article_chain.cache')
    @patch.object(AIArticleChain, 'chain', new_callable=lambda: property(lambda self: Mock()))
    def test_analyze_缓存未命中(self, mock_chain_prop, mock_cache, chain, sample_request):
        """测试分析 - 缓存未命中"""
        mock_cache.get.return_value = None

        mock_response = Mock()
        mock_response.content = """
是否AI相关：是
分类：学习
置信度：0.90
分类理由：教程内容
核心要点：教程要点1、教程要点2、教程要点3
摘要：学习教程摘要
关键词：教程、学习、资源
        """

        mock_chain = Mock()
        mock_chain.invoke.return_value = mock_response
        chain._chain = mock_chain
        chain._llm = Mock(model="glm")

        result = chain.analyze(sample_request)

        mock_cache.set.assert_called_once()
        assert result.category == "学习"
        assert result.confidence == 0.90
        assert result.is_ai_related is True

    @patch('src.chains.ai_article_chain.cache')
    @patch.object(AIArticleChain, 'chain', new_callable=lambda: property(lambda self: Mock()))
    def test_analyze_异常处理(self, mock_chain_prop, mock_cache, chain, sample_request):
        """测试分析 - 异常处理"""
        mock_cache.get.return_value = None
        chain._chain = Mock()
        chain._chain.invoke.side_effect = Exception("LLM调用失败")

        with pytest.raises(Exception) as exc_info:
            chain.analyze(sample_request)

        assert "AI文章分析失败" in str(exc_info.value)


class TestAIArticleCategories:
    """分类边界测试"""

    def test_all_categories_recognized(self):
        """测试所有分类都能被正确识别"""
        for category in AI_CONTENT_CATEGORIES:
            assert category in ["动态", "学习", "工具", "职业"]

    def test_category_count(self):
        """测试分类数量"""
        assert len(AI_CONTENT_CATEGORIES) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])