"Restricted mathematical expression parser for MathTutor AI.\nUses Python's ast module with an allowlist of nodes to construct SymPy expressions.\nRejects arbitrary code, attributes, and imports."

import ast
import re
from typing import Tuple, Set, Optional
import sympy as sp


class SafeParserError(Exception):
    "Syntax or safety error raised by the expression parser."
    pass


# Safety limits
MAX_EXPR_LENGTH = 300
MAX_AST_DEPTH = 25
MAX_EXPONENT_VAL = 20

# Explicitly allowed AST nodes
ALLOWED_AST_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Constant,
    ast.Name,
    ast.Load,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.USub,
    ast.UAdd,
)

# Default variable names: single letters and supported physics symbols
ALLOWED_VARIABLES: Set[str] = {
    "x", "y", "z", "t", "a", "b", "c", "d", "h", "m", "v", "r", "F", "p"
}


def preprocess_input(expr_str: str) -> str:
    "Preprocess student input: normalize whitespace, accept decimal commas between digits, convert ^ to **, and insert explicit multiplication for 2x, 3(x+1), (x+1)(x-2), and x(x-1)."
    s = expr_str.strip()
    if not s:
        raise SafeParserError("The expression cannot be empty.")

    if len(s) > MAX_EXPR_LENGTH:
        raise SafeParserError(f"The expression exceeds the maximum allowed length ({MAX_EXPR_LENGTH} characters).")

    # Reject suspicious code characters
    if any(char in s for char in [";", ":", "_", "[", "]", "{", "}", "\\", "'", '"', "`", "&", "|", "$", "!", "@", "#"]):
        raise SafeParserError("The expression contains unsupported characters.")

    # Replace decimal commas between digits (e.g. 3,14 -> 3.14)
    s = re.sub(r'(\d+),(\d+)', r'\1.\2', s)

    # Replace ^ powers with **
    s = s.replace("^", "**")

    # Implicit multiplication: number followed by letter (2x -> 2*x)
    s = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', s)

    # Implicit multiplication: number followed by opening parenthesis
    s = re.sub(r'(\d+)\(', r'\1*(', s)

    # Implicit multiplication: letter followed by opening parenthesis
    s = re.sub(r'([a-zA-Z])\(', r'\1*(', s)

    # Implicit multiplication: closing parenthesis followed by opening parenthesis
    s = re.sub(r'\)\(', r')*(', s)

    # Implicit multiplication: closing parenthesis followed by a letter or number
    s = re.sub(r'\)([a-zA-Z0-9])', r')*\1', s)

    return s


def _check_ast_safety_and_depth(node: ast.AST, depth: int = 0) -> None:
    if depth > MAX_AST_DEPTH:
        raise SafeParserError(f"The expression is too complex (maximum depth {MAX_AST_DEPTH} exceeded).")

    if not isinstance(node, ALLOWED_AST_NODES):
        raise SafeParserError(f"Unsupported operation or element in the expression: {type(node).__name__}")

    if isinstance(node, ast.Name):
        if node.id not in ALLOWED_VARIABLES:
            raise SafeParserError(f"The variable '{node.id}' is outside the allowed scope.")

    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float)):
            raise SafeParserError("Only numeric constants (integers or decimals) are allowed.")

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
        # Limit the size of constant exponents
        if isinstance(node.right, ast.Constant):
            if abs(node.right.value) > MAX_EXPONENT_VAL:
                raise SafeParserError(f"The exponent {node.right.value} exceeds the safety limit ({MAX_EXPONENT_VAL}).")

    for child in ast.iter_child_nodes(node):
        _check_ast_safety_and_depth(child, depth + 1)


def _ast_to_sympy(node: ast.AST) -> sp.Expr:
    "Recursively convert a validated AST to a SymPy object."
    if isinstance(node, ast.Expression):
        return _ast_to_sympy(node.body)

    if isinstance(node, ast.Constant):
        val = node.value
        if isinstance(val, int):
            return sp.Integer(val)
        return sp.Rational(str(val))

    if isinstance(node, ast.Name):
        return sp.Symbol(node.id, real=True)

    if isinstance(node, ast.UnaryOp):
        operand = _ast_to_sympy(node.operand)
        if isinstance(node.op, ast.UAdd):
            return operand
        if isinstance(node.op, ast.USub):
            return -operand

    if isinstance(node, ast.BinOp):
        left = _ast_to_sympy(node.left)
        right = _ast_to_sympy(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            if right == 0:
                raise SafeParserError("Division by zero is not allowed.")
            return left / right
        if isinstance(node.op, ast.Pow):
            return left ** right

    raise SafeParserError(f"Could not process node: {type(node).__name__}")


def parse_expression(expr_str: str) -> sp.Expr:
    "Parse a mathematical expression into SymPy without eval or unsafe sympify."
    cleaned = preprocess_input(expr_str)
    try:
        tree = ast.parse(cleaned, mode='eval')
    except SyntaxError as e:
        raise SafeParserError(f"Mathematical syntax error: malformed expression ({e.msg}).")

    _check_ast_safety_and_depth(tree)
    return _ast_to_sympy(tree)


def parse_equation(eq_str: str) -> Tuple[sp.Expr, sp.Expr, sp.Symbol]:
    "Parse an equation containing '=' (e.g. '2x + 3 = 11').\nReturn (lhs_sympy, rhs_sympy, main_variable)."
    if "=" not in eq_str:
        raise SafeParserError("An equation must contain '=' between its two sides.")

    parts = eq_str.split("=")
    if len(parts) != 2:
        raise SafeParserError("The equation must contain exactly one '=' sign.")

    lhs_str = parts[0].strip()
    rhs_str = parts[1].strip()

    if not lhs_str or not rhs_str:
        raise SafeParserError("Both sides of the equation must contain an expression.")

    lhs = parse_expression(lhs_str)
    rhs = parse_expression(rhs_str)

    # Identify the unknown
    symbols = (lhs.free_symbols | rhs.free_symbols)
    if len(symbols) == 0:
        # Equation with no unknowns (e.g. 2 = 2 or 2 = 3)
        var = sp.Symbol("x", real=True)
    elif len(symbols) == 1:
        var = list(symbols)[0]
    else:
        # Version 0.1 supports only one unknown
        raise SafeParserError(f"Version 0.1 only supports equations with one unknown. Found: {symbols}")

    return lhs, rhs, var
