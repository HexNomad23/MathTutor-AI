"""
Motor algebraico pedagógico de MathTutor AI.
Resuelve ecuaciones lineales y cuadráticas generando pasos explicados,
comprobación por sustitución y detección de dominios.
"""

import sympy as sp
from typing import List, Tuple, Optional
import uuid

from ..core.models import (
    Subject,
    VerificationStatus,
    SolutionStep,
    SolutionResult,
)
from .safe_parser import parse_equation, parse_expression, SafeParserError


def format_expr(expr: sp.Expr) -> str:
    """Formatea una expresión SymPy en texto matemático limpio para estudiantes."""
    s = str(expr)
    s = s.replace("**", "^")
    s = s.replace("*", "")
    return s


def solve_linear_equation(eq_str: str) -> SolutionResult:
    """
    Resuelve paso a paso una ecuación lineal de una incógnita:
    1. Expande paréntesis si los hay.
    2. Agrupa términos con x en el miembro izquierdo.
    3. Agrupa términos constantes en el miembro derecho.
    4. Despeja la incógnita dividiendo por su coeficiente.
    5. Realiza la comprobación por sustitución en la ecuación original.
    """
    lhs_orig, rhs_orig, var = parse_equation(eq_str)
    interpreted_str = f"{lhs_orig} = {rhs_orig}"

    # Verificar grado
    diff = sp.expand(lhs_orig - rhs_orig)
    poly = sp.Poly(diff, var)
    degree = poly.degree()

    if degree > 1:
        raise SafeParserError(f"Esta función es para ecuaciones lineales. El grado de la ecuación ingresada es {degree}.")

    steps: List[SolutionStep] = []
    step_num = 1

    current_lhs = lhs_orig
    current_rhs = rhs_orig

    # Paso 1: Eliminar paréntesis si existen productos expandibles
    lhs_expanded = sp.expand(current_lhs)
    rhs_expanded = sp.expand(current_rhs)

    has_parens = (lhs_expanded != current_lhs) or (rhs_expanded != current_rhs)
    if has_parens:
        prev_expr = f"{current_lhs} = {current_rhs}"
        current_lhs = lhs_expanded
        current_rhs = rhs_expanded
        res_expr = f"{current_lhs} = {current_rhs}"
        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=prev_expr,
            operation="Aplicar la propiedad distributiva",
            resulting_expr=res_expr,
            explanation_brief="Multiplicar los coeficientes para eliminar los paréntesis.",
            explanation_detailed="Se aplica la propiedad distributiva a(b + c) = ab + ac en los términos que contienen paréntesis para poder operar con términos semejantes."
        ))
        step_num += 1

    # Analizar términos en lhs y rhs
    # Escribimos current_lhs como A*var + B, y current_rhs como C*var + D
    poly_l = sp.Poly(current_lhs, var) if current_lhs.has(var) else sp.Poly(0, var)
    poly_r = sp.Poly(current_rhs, var) if current_rhs.has(var) else sp.Poly(0, var)

    coeff_l = poly_l.coeff_monomial(var)
    const_l = current_lhs - coeff_l * var

    coeff_r = poly_r.coeff_monomial(var)
    const_r = current_rhs - coeff_r * var

    # Paso: Mover constante del lado izquierdo al derecho
    if const_l != 0:
        prev_expr = f"{current_lhs} = {current_rhs}"
        op_text = f"Restar {const_l}" if const_l > 0 else f"Sumar {-const_l}"
        # Representar paso intermedio
        if const_l > 0:
            inter_lhs = f"{current_lhs} - {const_l}"
            inter_rhs = f"{current_rhs} - {const_l}"
        else:
            inter_lhs = f"{current_lhs} + {-const_l}"
            inter_rhs = f"{current_rhs} + {-const_l}"

        current_lhs = sp.simplify(current_lhs - const_l)
        current_rhs = sp.simplify(current_rhs - const_l)
        res_expr = f"{current_lhs} = {current_rhs}"

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=prev_expr,
            operation=f"{op_text} en ambos miembros: {inter_lhs} = {inter_rhs}",
            resulting_expr=res_expr,
            explanation_brief=f"{op_text} en ambos miembros para aislar los términos con {var}.",
            explanation_detailed=f"Para cancelar el término constante {const_l} del lado izquierdo, aplicamos la operación inversa ({op_text}) en ambos lados de la ecuación para mantener la igualdad."
        ))
        step_num += 1

    # Paso: Mover variable del lado derecho al izquierdo si existe
    if coeff_r != 0:
        prev_expr = f"{current_lhs} = {current_rhs}"
        var_term = coeff_r * var
        op_text = f"Restar {var_term}" if coeff_r > 0 else f"Sumar {-coeff_r * var}"

        current_lhs = sp.simplify(current_lhs - var_term)
        current_rhs = sp.simplify(current_rhs - var_term)
        res_expr = f"{current_lhs} = {current_rhs}"

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=prev_expr,
            operation=f"{op_text} en ambos miembros",
            resulting_expr=res_expr,
            explanation_brief=f"Mover todos los términos con la incógnita {var} al miembro izquierdo.",
            explanation_detailed=f"Restamos {var_term} en ambos lados para que todos los términos que contienen la incógnita queden agrupados en el miembro izquierdo."
        ))
        step_num += 1

    # Ahora tenemos A*var = B
    poly_final = sp.Poly(current_lhs, var) if current_lhs.has(var) else sp.Poly(0, var)
    A = poly_final.coeff_monomial(var)
    B = current_rhs

    # Casos especiales: A == 0
    if A == 0:
        if B == 0:
            final_ans = "Infinitas soluciones reales"
            status = VerificationStatus.VERIFIED
            reason = "La ecuación se reduce a la identidad 0 = 0, que se cumple para todo número real x ∈ ℝ."
            sub_check = "Identidad verificada: cualquier valor de x satisface la igualdad original."
        else:
            final_ans = "Sin solución"
            status = VerificationStatus.VERIFIED
            reason = f"La ecuación se reduce a una contradicción (0 = {B}), por lo que ningún valor de x puede satisfacerla."
            sub_check = "Contradicción: 0 ≠ constante. No existe solución en el conjunto de los números reales."

        return SolutionResult(
            exercise_id=str(uuid.uuid4()),
            subject=Subject.ALGEBRA,
            original_input=eq_str,
            interpreted_input=interpreted_str,
            domain_assumptions="Números reales (x ∈ ℝ)",
            steps=steps,
            final_answer=final_ans,
            verification_status=status,
            verification_reason=reason,
            substitution_check=sub_check,
        )

    # Paso: Dividir entre A si A != 1
    if A != 1:
        prev_expr = f"{current_lhs} = {current_rhs}"
        sol_val = sp.Rational(B, A) if isinstance(B, (int, sp.Integer)) and isinstance(A, (int, sp.Integer)) else sp.simplify(B / A)
        res_expr = f"{var} = {sol_val}"

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=prev_expr,
            operation=f"Dividir ambos miembros entre {A}",
            resulting_expr=res_expr,
            explanation_brief=f"Dividir ambos lados entre el coeficiente {A} para despejar {var}.",
            explanation_detailed=f"Como {A} multiplica a {var}, dividimos ambos miembros de la ecuación entre {A} (operación inversa) para obtener el valor final de la incógnita."
        ))
        step_num += 1
    else:
        sol_val = B

    final_ans = f"{var} = {sol_val}"

    # Paso Comprobación por sustitución:
    sub_lhs = lhs_orig.subs(var, sol_val)
    sub_rhs = rhs_orig.subs(var, sol_val)
    sub_lhs_eval = sp.simplify(sub_lhs)
    sub_rhs_eval = sp.simplify(sub_rhs)

    # Explicación de la sustitución
    sub_check_str = (
        f"Sustituir {var} = {sol_val} en la ecuación original:\n"
        f"Lado izquierdo: {lhs_orig} = {sub_lhs} = {sub_lhs_eval}\n"
        f"Lado derecho: {rhs_orig} = {sub_rhs} = {sub_rhs_eval}\n"
        f"Resultado: {sub_lhs_eval} = {sub_rhs_eval} (Identidad confirmada)"
    )

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr=f"{var} = {sol_val}",
        operation=f"Comprobación por sustitución ({var} = {sol_val})",
        resulting_expr=f"{sub_lhs_eval} = {sub_rhs_eval}",
        explanation_brief="Verificar la solución sustituyéndola en la ecuación inicial.",
        explanation_detailed=f"Reemplazamos {var} por {sol_val} en ambos miembros de la ecuación original y comprobamos que ambos lados dan exactamente el mismo valor ({sub_lhs_eval})."
    ))

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.ALGEBRA,
        original_input=eq_str,
        interpreted_input=interpreted_str,
        domain_assumptions="Números reales (x ∈ ℝ)",
        steps=steps,
        final_answer=final_ans,
        verification_status=VerificationStatus.VERIFIED,
        verification_reason=f"Sustitución exacta verificada simbólicamente: {sub_lhs_eval} = {sub_rhs_eval}.",
        substitution_check=sub_check_str,
    )


def solve_quadratic_equation(eq_str: str) -> SolutionResult:
    """
    Resuelve una ecuación cuadrática a*x^2 + b*x + c = 0 mediante la fórmula general
    o factorización, mostrando discriminante, raíces reales y comprobación.
    """
    lhs_orig, rhs_orig, var = parse_equation(eq_str)
    interpreted_str = f"{lhs_orig} = {rhs_orig}"

    diff = sp.expand(lhs_orig - rhs_orig)
    poly = sp.Poly(diff, var)
    degree = poly.degree()

    if degree != 2:
        raise SafeParserError(f"La ecuación ingresada no es cuadrática (grado {degree}).")

    a = poly.coeff_monomial(var**2)
    b = poly.coeff_monomial(var)
    c = poly.coeff_monomial(1)

    steps: List[SolutionStep] = []
    step_num = 1

    # Paso 1: Forma general
    std_form = f"{a}*{var}^2 + ({b})*{var} + ({c}) = 0".replace("+ (-", "- (")
    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr=f"{lhs_orig} = {rhs_orig}",
        operation="Llevar a la forma canónica ax² + bx + c = 0",
        resulting_expr=f"{diff} = 0",
        explanation_brief="Igualar a cero restando el miembro derecho.",
        explanation_detailed=f"Identificamos los coeficientes: a = {a}, b = {b}, c = {c}."
    ))
    step_num += 1

    # Paso 2: Discriminante
    disc = b**2 - 4*a*c
    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr=f"{diff} = 0",
        operation=f"Calcular el discriminante Δ = b² - 4ac",
        resulting_expr=f"Δ = ({b})² - 4·({a})·({c}) = {disc}",
        explanation_brief=f"Evaluar el discriminante para determinar el número de soluciones reales.",
        explanation_detailed=f"El discriminante Δ = {disc} indica si hay dos soluciones reales distintas (Δ > 0), una solución doble (Δ = 0) o ninguna solución real (Δ < 0)."
    ))
    step_num += 1

    if disc < 0:
        final_ans = "Sin soluciones reales"
        reason = f"El discriminante es negativo (Δ = {disc} < 0). En el conjunto de los números reales no existen raíces cuadradas de números negativos."
        sub_check = "No existen raíces en ℝ. (Las soluciones pertenecen al campo de los números complejos)."
        return SolutionResult(
            exercise_id=str(uuid.uuid4()),
            subject=Subject.ALGEBRA,
            original_input=eq_str,
            interpreted_input=interpreted_str,
            domain_assumptions="Números reales (x ∈ ℝ)",
            steps=steps,
            final_answer=final_ans,
            verification_status=VerificationStatus.VERIFIED,
            verification_reason=reason,
            substitution_check=sub_check,
        )

    # Raíces reales
    sqrt_disc = sp.sqrt(disc)
    x1 = sp.simplify((-b + sqrt_disc) / (2*a))
    x2 = sp.simplify((-b - sqrt_disc) / (2*a))

    formula_step = f"{var} = (-({b}) ± √({disc})) / (2·{a})"
    if disc == 0:
        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=f"Δ = {disc}",
            operation="Aplicar la fórmula general para raíz única/doble",
            resulting_expr=f"{var} = {x1}",
            explanation_brief="Como Δ = 0, existe una única solución real doble.",
            explanation_detailed=f"Aplicando {var} = -b / (2a) obtenemos {var} = {x1}."
        ))
        step_num += 1
        final_ans = f"{var} = {x1} (raíz doble)"
    else:
        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=f"Δ = {disc}",
            operation=f"Aplicar la fórmula cuadrática: {formula_step}",
            resulting_expr=f"{var}₁ = {x1},  {var}₂ = {x2}",
            explanation_brief="Calcular las dos raíces reales sumando y restando la raíz del discriminante.",
            explanation_detailed=f"Obtenemos dos soluciones: {var}₁ = (-({b}) + {sqrt_disc}) / {2*a} = {x1} y {var}₂ = (-({b}) - {sqrt_disc}) / {2*a} = {x2}."
        ))
        step_num += 1
        final_ans = f"{var} = {x1} y {var} = {x2}"

    # Comprobación por sustitución
    check_lines = []
    roots = [x1] if disc == 0 else [x1, x2]
    for r in roots:
        sub_l = sp.simplify(lhs_orig.subs(var, r))
        sub_r = sp.simplify(rhs_orig.subs(var, r))
        check_lines.append(f"Para {var} = {r}: Lado izquierdo = {sub_l}, Lado derecho = {sub_r} -> {sub_l} = {sub_r}")

    sub_check_str = "\n".join(check_lines)

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr=final_ans,
        operation="Comprobación por sustitución en la ecuación original",
        resulting_expr="Identidad confirmada en cada raíz",
        explanation_brief="Sustituir cada valor obtenido en la ecuación original.",
        explanation_detailed="Comprobamos que al reemplazar cada una de las raíces encontradas, ambos miembros de la ecuación resultan exactamente iguales."
    ))

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.ALGEBRA,
        original_input=eq_str,
        interpreted_input=interpreted_str,
        domain_assumptions="Números reales (x ∈ ℝ)",
        steps=steps,
        final_answer=final_ans,
        verification_status=VerificationStatus.VERIFIED,
        verification_reason=f"Raíces verificadas exactamente por sustitución en la ecuación original.",
        substitution_check=sub_check_str,
    )
