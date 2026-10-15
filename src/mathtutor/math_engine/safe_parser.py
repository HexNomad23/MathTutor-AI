"""
Analizador seguro de expresiones matemáticas (Safe Parser) para MathTutor AI.
Garantiza que la entrada del usuario no ejecute código arbitrario, atributos o importaciones.
Utiliza el módulo ast estándar con lista blanca de nodos y transformación a expresiones SymPy.
"""

import ast
import re
from typing import Tuple, Set, Optional
import sympy as sp


class SafeParserError(Exception):
    """Excepción para errores de sintaxis o seguridad en el parser."""
    pass


# Límite de seguridad
MAX_EXPR_LENGTH = 300
MAX_AST_DEPTH = 25
MAX_EXPONENT_VAL = 20

# Nodos AST estrictamente permitidos
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

# Nombres de variables permitidos por defecto (alfabéticos de una letra o específicos de física)
ALLOWED_VARIABLES: Set[str] = {
    "x", "y", "z", "t", "a", "b", "c", "d", "h", "m", "v", "r", "F", "p"
}


def preprocess_input(expr_str: str) -> str:
    """
    Preprocesa la entrada del estudiante:
    - Normaliza espacios.
    - Soporta coma decimal cuando está entre dígitos (ej: 3,5 -> 3.5).
    - Convierte potencias '^' a '**'.
    - Convierte multiplicación implícita:
      - 2x -> 2*x
      - 3(x+1) -> 3*(x+1)
      - (x+1)(x-2) -> (x+1)*(x-2)
      - x(x-1) -> x*(x-1)
    """
    s = expr_str.strip()
    if not s:
        raise SafeParserError("La expresión no puede estar vacía.")

    if len(s) > MAX_EXPR_LENGTH:
        raise SafeParserError(f"La expresión excede la longitud máxima permitida ({MAX_EXPR_LENGTH} caracteres).")

    # Rechazar caracteres sospechosos de código
    if any(char in s for char in [";", ":", "_", "[", "]", "{", "}", "\\", "'", '"', "`", "&", "|", "$", "!", "@", "#"]):
        raise SafeParserError("La expresión contiene caracteres no permitidos.")

    # Reemplazar coma decimal entre números (ej. 3,14 -> 3.14)
    s = re.sub(r'(\d+),(\d+)', r'\1.\2', s)

    # Reemplazar potencias con ^ por **
    s = s.replace("^", "**")

    # Multiplicación implícita: número seguido de letra (ej: 2x -> 2*x)
    s = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', s)

    # Multiplicación implícita: número seguido de paréntesis abierto (ej: 3(x+1) -> 3*(x+1))
    s = re.sub(r'(\d+)\(', r'\1*(', s)

    # Multiplicación implícita: letra seguida de paréntesis abierto (ej: x(x+1) -> x*(x+1))
    s = re.sub(r'([a-zA-Z])\(', r'\1*(', s)

    # Multiplicación implícita: paréntesis cerrado seguido de paréntesis abierto (ej: (x+1)(x-2) -> (x+1)*(x-2))
    s = re.sub(r'\)\(', r')*(', s)

    # Multiplicación implícita: paréntesis cerrado seguido de letra o número (ej: (x+1)x -> (x+1)*x)
    s = re.sub(r'\)([a-zA-Z0-9])', r')*\1', s)

    return s


def _check_ast_safety_and_depth(node: ast.AST, depth: int = 0) -> None:
    if depth > MAX_AST_DEPTH:
        raise SafeParserError(f"La expresión es demasiado compleja (profundidad máxima {MAX_AST_DEPTH} superada).")

    if not isinstance(node, ALLOWED_AST_NODES):
        raise SafeParserError(f"Operación o elemento no permitido en la expresión: {type(node).__name__}")

    if isinstance(node, ast.Name):
        if node.id not in ALLOWED_VARIABLES:
            raise SafeParserError(f"La variable '{node.id}' no está dentro del alcance permitido.")

    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float)):
            raise SafeParserError("Solo se permiten constantes numéricas (enteros o decimales).")

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
        # Limitar tamaño de exponentes constantes
        if isinstance(node.right, ast.Constant):
            if abs(node.right.value) > MAX_EXPONENT_VAL:
                raise SafeParserError(f"El exponente {node.right.value} supera el límite seguro ({MAX_EXPONENT_VAL}).")

    for child in ast.iter_child_nodes(node):
        _check_ast_safety_and_depth(child, depth + 1)


def _ast_to_sympy(node: ast.AST) -> sp.Expr:
    """Convierte de forma recursiva y segura el árbol AST verificado a un objeto SymPy."""
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
                raise SafeParserError("División entre cero no permitida.")
            return left / right
        if isinstance(node.op, ast.Pow):
            return left ** right

    raise SafeParserError(f"No se pudo procesar el nodo: {type(node).__name__}")


def parse_expression(expr_str: str) -> sp.Expr:
    """
    Parsea de forma segura una expresión matemática a SymPy sin usar eval ni sympify no seguro.
    """
    cleaned = preprocess_input(expr_str)
    try:
        tree = ast.parse(cleaned, mode='eval')
    except SyntaxError as e:
        raise SafeParserError(f"Error de sintaxis matemática: expresión mal formada ({e.msg}).")

    _check_ast_safety_and_depth(tree)
    return _ast_to_sympy(tree)


def parse_equation(eq_str: str) -> Tuple[sp.Expr, sp.Expr, sp.Symbol]:
    """
    Parsea una ecuación con signo '=' (ej. '2x + 3 = 11').
    Retorna (lhs_sympy, rhs_sympy, variable_principal).
    """
    if "=" not in eq_str:
        raise SafeParserError("Una ecuación debe contener el signo '=' separando ambos miembros.")

    parts = eq_str.split("=")
    if len(parts) != 2:
        raise SafeParserError("La ecuación debe contener exactamente un signo '='.")

    lhs_str = parts[0].strip()
    rhs_str = parts[1].strip()

    if not lhs_str or not rhs_str:
        raise SafeParserError("Ambos lados de la ecuación deben tener una expresión.")

    lhs = parse_expression(lhs_str)
    rhs = parse_expression(rhs_str)

    # Identificar la incógnita
    symbols = (lhs.free_symbols | rhs.free_symbols)
    if len(symbols) == 0:
        # Ecuación sin incógnitas (ej: 2 = 2 o 2 = 3)
        var = sp.Symbol("x", real=True)
    elif len(symbols) == 1:
        var = list(symbols)[0]
    else:
        # En v0.1 solo soportamos una incógnita
        raise SafeParserError(f"En la versión 0.1 solo se admiten ecuaciones con una incógnita. Se detectaron: {symbols}")

    return lhs, rhs, var
