"""
计算器工具
"""
from langchain_core.tools import Tool
import ast
import operator


# 安全的数学运算符
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def safe_eval(expr: str) -> str:
    """
    安全地计算数学表达式
    
    Args:
        expr: 数学表达式字符串
        
    Returns:
        计算结果
    """
    try:
        node = ast.parse(expr, mode='eval')
        return str(_eval_node(node.body))
    except Exception as e:
        return f"计算错误：{str(e)}"


def _eval_node(node):
    """递归计算 AST 节点"""
    if isinstance(node, ast.Num):  # Python < 3.8
        return node.n
    elif isinstance(node, ast.Constant):  # Python >= 3.8
        return node.value
    elif isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return OPERATORS[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        return OPERATORS[type(node.op)](operand)
    else:
        raise TypeError(f"不支持的操作：{type(node)}")


def calculate(expression: str) -> str:
    """
    计算数学表达式
    
    Args:
        expression: 数学表达式，如 "1+2*3"
        
    Returns:
        计算结果
    """
    # 清理输入
    expr = expression.strip()
    
    # 只允许数字和基本运算符
    allowed_chars = set("0123456789+-*/.() ")
    if not all(c in allowed_chars for c in expr):
        return "错误：表达式包含非法字符"
    
    return safe_eval(expr)


# 导出工具
calculator_tool = Tool(
    name="calculator",
    func=calculate,
    description="计算数学表达式。输入应该是纯数学表达式，如 '1+2*3' 或 '(10-5)*2'。"
)
