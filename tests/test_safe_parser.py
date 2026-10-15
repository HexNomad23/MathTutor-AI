"""
Pruebas para el Safe Parser de MathTutor AI.
"""

import pytest
import sympy as sp
from mathtutor.math_engine.safe_parser import (
    parse_expression,
    parse_equation,
    SafeParserError,
    preprocess_input,
)


def test_safe_parser_basic_linear():
    expr = parse_expression("2x + 3")
    x = sp.Symbol("x", real=True)
    assert sp.simplify(expr - (2*x + 3)) == 0


def test_safe_parser_equation():
    lhs, rhs, var = parse_equation("2x + 3 = 11")
    assert var.name == "x"
    assert lhs == 2*var + 3
    assert rhs == 11


def test_safe_parser_parentheses_and_powers():
    expr = parse_expression("3(x - 2)^2 + 4,5")
    x = sp.Symbol("x", real=True)
    expected = 3*(x - 2)**2 + sp.Rational("4.5")
    assert sp.simplify(expr - expected) == 0


def test_safe_parser_implicit_multiplication():
    assert preprocess_input("2x") == "2*x"
    assert preprocess_input("3(x-2)") == "3*(x-2)"
    assert preprocess_input("(x+1)(x-2)") == "(x+1)*(x-2)"
    assert preprocess_input("x(x+1)") == "x*(x+1)"


def test_safe_parser_security_rejections():
    # Intento de inyección de código / ejecución
    with pytest.raises(SafeParserError):
        parse_expression("__import__('os').system('dir')")

    with pytest.raises(SafeParserError):
        parse_expression("eval('1+1')")

    with pytest.raises(SafeParserError):
        parse_expression("x.__class__")

    with pytest.raises(SafeParserError):
        parse_expression("open('secret.txt')")

    with pytest.raises(SafeParserError):
        parse_expression("; drop table;")

    with pytest.raises(SafeParserError):
        parse_expression("")


def test_safe_parser_limits():
    # Exponente excesivo
    with pytest.raises(SafeParserError):
        parse_expression("x^100")

    # Múltiples incógnitas rechazadas en parse_equation
    with pytest.raises(SafeParserError):
        parse_equation("2x + 3y = 10")
