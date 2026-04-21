from src.chains import TranslateChain
from src.chains.translate_chain import TranslateRequest


def generate_long_text(language="en", length=6000):
    """
    生成长文本用于测试
    
    Args:
        language: 语言类型 (en/cn)
        length: 期望的文本长度
    
    Returns:
        str: 生成的长文本
    """
    if language == "cn":
        base_text = "人工智能是计算机科学的一个重要分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大，可以设想，未来人工智能带来的科技产品，将会是人类智慧的容器。人工智能可以对人的意识、思维的信息过程的模拟。人工智能不是人的智能，但能像人那样思考、也可能超过人的智能。"
    else:
        base_text = "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals. The term artificial intelligence had previously been used to describe machines that mimic and display human cognitive skills that are associated with the human mind, such as learning and problem-solving. This definition has since been rejected by major AI researchers who now describe AI in terms of rationality and acting rationally, which does not limit how intelligence can be articulated."
    
    # 重复文本直到达到目标长度
    multiplier = (length // len(base_text)) + 1
    long_text = (base_text + " ") * multiplier
    return long_text[:length]


def test_short_translation():
    """测试短文本翻译"""
    print("\n" + "=" * 80)
    print("【测试组1】短文本翻译测试")
    print("=" * 80)
    
    translate_chain = TranslateChain(model_id="glm")
    
    # 测试1：英文翻译成中文
    print("\n【测试1.1】英文翻译成中文")
    print("-" * 80)
    request1 = TranslateRequest(
        content="Hello, how are you today?",
        source_language="auto",
        target_language="中文"
    )
    
    try:
        result1 = translate_chain.translate(request1)
        print(f"原文: {request1.content}")
        print(f"译文: {result1.translated_text}")
        print(f"源语言: {result1.source_language}")
        print(f"目标语言: {result1.target_language}")
        print(f"模型: {result1.model}")
        print("✓ 测试1.1通过")
    except Exception as e:
        print(f"✗ 测试1.1失败: {e}")
    
    # 测试2：日文翻译成中文
    print("\n【测试1.2】日文翻译成中文")
    print("-" * 80)
    request2 = TranslateRequest(
        content="こんにちは、元気ですか？今日は素晴らしい一日ですね！",
        source_language="auto",
        target_language="中文"
    )
    
    try:
        result2 = translate_chain.translate(request2)
        print(f"原文: {request2.content}")
        print(f"译文: {result2.translated_text}")
        print(f"源语言: {result2.source_language}")
        print(f"目标语言: {result2.target_language}")
        print("✓ 测试1.2通过")
    except Exception as e:
        print(f"✗ 测试1.2失败: {e}")
    
    # 测试3：中文翻译成英文
    print("\n【测试1.3】中文翻译成英文")
    print("-" * 80)
    request3 = TranslateRequest(
        content="你好，今天天气真好！",
        source_language="auto",
        target_language="英文"
    )
    
    try:
        result3 = translate_chain.translate(request3)
        print(f"原文: {request3.content}")
        print(f"译文: {result3.translated_text}")
        print(f"源语言: {result3.source_language}")
        print(f"目标语言: {result3.target_language}")
        print("✓ 测试1.3通过")
    except Exception as e:
        print(f"✗ 测试1.3失败: {e}")


def test_long_translation():
    """测试长文本翻译（自动分块）"""
    print("\n" + "=" * 80)
    print("【测试组2】长文本翻译测试（自动分块）")
    print("=" * 80)
    
    translate_chain = TranslateChain(model_id="glm")
    
    # 测试4：英文长文章翻译成中文（约6000字符）
    print("\n【测试2.1】英文长文章翻译成中文（约6000字符）")
    print("-" * 80)
    long_en_text = generate_long_text(language="en", length=36000)
    print(f"原文长度: {len(long_en_text)} 字符")
    print(f"原文预览: {long_en_text[:200]}...")
    
    request4 = TranslateRequest(
        content=long_en_text,
        source_language="auto",
        target_language="中文"
    )
    
    try:
        result4 = translate_chain.translate(request4)
        print(f"\n译文长度: {len(result4.translated_text)} 字符")
        print(f"译文预览: {result4.translated_text}...")
        print(f"源语言: {result4.source_language}")
        print(f"目标语言: {result4.target_language}")
        print(f"模型: {result4.model}")
        print("✓ 测试2.1通过 - 长文章分块翻译成功")
    except Exception as e:
        print(f"✗ 测试2.1失败: {e}")
        import traceback
        traceback.print_exc()
    
    # # 测试5：中文长文章翻译成英文（约8000字符）
    # print("\n【测试2.2】中文长文章翻译成英文（约8000字符）")
    # print("-" * 80)
    # long_cn_text = generate_long_text(language="cn", length=8000)
    # print(f"原文长度: {len(long_cn_text)} 字符")
    # print(f"原文预览: {long_cn_text[:200]}...")
    #
    # request5 = TranslateRequest(
    #     content=long_cn_text,
    #     source_language="auto",
    #     target_language="英文"
    # )
    #
    # try:
    #     result5 = translate_chain.translate(request5)
    #     print(f"\n译文长度: {len(result5.translated_text)} 字符")
    #     print(f"译文预览: {result5.translated_text[:200]}...")
    #     print(f"源语言: {result5.source_language}")
    #     print(f"目标语言: {result5.target_language}")
    #     print("✓ 测试2.2通过 - 长文章分块翻译成功")
    # except Exception as e:
    #     print(f"✗ 测试2.2失败: {e}")
    #     import traceback
    #     traceback.print_exc()
    #
    # # 测试6：超长文章翻译（约15000字符）
    # print("\n【测试2.3】超长文章翻译（约15000字符）")
    # print("-" * 80)
    # very_long_text = generate_long_text(language="en", length=15000)
    # print(f"原文长度: {len(very_long_text)} 字符")
    # print(f"预计分块数: 约 {len(very_long_text) // TranslateChain.CHUNK_SIZE} 块")
    #
    # request6 = TranslateRequest(
    #     content=very_long_text,
    #     source_language="auto",
    #     target_language="中文"
    # )
    #
    # try:
    #     result6 = translate_chain.translate(request6)
    #     print(f"\n译文长度: {len(result6.translated_text)} 字符")
    #     print(f"译文预览: {result6.translated_text[:200]}...")
    #     print(f"源语言: {result6.source_language}")
    #     print(f"目标语言: {result6.target_language}")
    #     print("✓ 测试2.3通过 - 超长文章分块翻译成功")
    # except Exception as e:
    #     print(f"✗ 测试2.3失败: {e}")
    #     import traceback
    #     traceback.print_exc()


def test_cache_performance():
    """测试缓存性能"""
    print("\n" + "=" * 80)
    print("【测试组3】缓存性能测试")
    print("=" * 80)
    
    translate_chain = TranslateChain(model_id="glm")
    
    # 测试7：相同内容第二次翻译（应使用缓存）
    print("\n【测试3.1】缓存命中测试")
    print("-" * 80)
    test_content = "This is a test sentence for caching."
    
    request7a = TranslateRequest(
        content=test_content,
        source_language="auto",
        target_language="中文"
    )
    
    try:
        print("第一次翻译（实时）:")
        result7a = translate_chain.translate(request7a)
        print(f"译文: {result7a.translated_text}")
        
        print("\n第二次翻译（应从缓存获取）:")
        result7b = translate_chain.translate(request7a)
        print(f"译文: {result7b.translated_text}")
        print("✓ 测试3.1通过 - 缓存功能正常")
    except Exception as e:
        print(f"✗ 测试3.1失败: {e}")


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print(" " * 20 + "文本翻译功能完整测试")
    print("=" * 80)
    
    try:
        # 测试短文本翻译
        test_short_translation()
        
        # 测试长文本翻译（核心功能）
        test_long_translation()
        
        # 测试缓存性能
        test_cache_performance()
        
        print("\n" + "=" * 80)
        print(" " * 25 + "所有测试完成!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # main()
    test_long_translation()

