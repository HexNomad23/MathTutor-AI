"""
Revisor pedagógico de procedimientos y transiciones paso a paso para Álgebra.
Diagnóstica errores comunes (signo al trasponer, error de cálculo, omisión de división)
y valida procedimientos alternativos matemáticamente equivalentes.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import sympy as sp

from ..math_engine.safe_parser import parse_equation, SafeParserError


@dataclass
class StepReviewResult:
    is_valid: bool
    step_index: int  # Índice del paso evaluado (1-indexed)
    previous_line: str
    current_line: str
    message: str
    is_alternative_valid: bool = False
    suggested_correction: Optional[str] = None


def check_linear_step_transition(prev_line: str, curr_line: str, step_index: int = 1) -> StepReviewResult:
    """
    Compara dos líneas consecutivas de una ecuación lineal y diagnostica si el paso es válido,
    equivalente alternativo o contiene un error específico.
    """
    try:
        lhs_prev, rhs_prev, var_prev = parse_equation(prev_line)
    except SafeParserError as e:
        return StepReviewResult(
            is_valid=False,
            step_index=step_index,
            previous_line=prev_line,
            current_line=curr_line,
            message=f"Error en la línea anterior: {e}"
        )

    try:
        lhs_curr, rhs_curr, var_curr = parse_equation(curr_line)
    except SafeParserError as e:
        return StepReviewResult(
            is_valid=False,
            step_index=step_index,
            previous_line=prev_line,
            current_line=curr_line,
            message=f"Error de sintaxis en el paso actual: {e}"
        )

    var = var_prev

    # Diferencias L - R
    diff_prev = sp.expand(lhs_prev - rhs_prev)
    diff_curr = sp.expand(lhs_curr - rhs_curr)

    poly_prev = sp.Poly(diff_prev, var) if diff_prev.has(var) else sp.Poly(0, var)
    poly_curr = sp.Poly(diff_curr, var) if diff_curr.has(var) else sp.Poly(0, var)

    a_prev = poly_prev.coeff_monomial(var)
    b_prev = poly_prev.coeff_monomial(1)

    a_curr = poly_curr.coeff_monomial(var)
    b_curr = poly_curr.coeff_monomial(1)

    # 1. Comprobar si son exactamente equivalentes (múltiplo escalar no nulo)
    # diff_curr = k * diff_prev con k != 0
    if a_prev != 0:
        ratio_a = a_curr / a_prev
        if ratio_a != 0 and sp.simplify(b_curr - ratio_a * b_prev) == 0:
            if ratio_a == 1:
                return StepReviewResult(
                    is_valid=True,
                    step_index=step_index,
                    previous_line=prev_line,
                    current_line=curr_line,
                    message="Paso correcto y válido."
                )
            else:
                return StepReviewResult(
                    is_valid=True,
                    step_index=step_index,
                    previous_line=prev_line,
                    current_line=curr_line,
                    message=f"Paso alternativo válido: la ecuación es equivalente (multiplicada en ambos lados por {ratio_a}).",
                    is_alternative_valid=True
                )

    # Si no son equivalentes, diagnosticar el error específico
    # Diagnóstico A: El alumno cambió de signo erróneamente al trasponer una constante
    # Ejemplo: de 2x + 3 = 11 pasó a 2x = 11 + 3 (en vez de 11 - 3)
    # Detectamos si en prev había una constante en lhs (+c) y en curr aparece sumada en rhs en vez de restada
    poly_l_prev = sp.Poly(lhs_prev, var) if lhs_prev.has(var) else sp.Poly(0, var)
    const_l_prev = lhs_prev - poly_l_prev.coeff_monomial(var) * var

    if const_l_prev != 0:
        # Si sumó en vez de restar:
        # Lado derecho esperado con suma: rhs_prev + const_l_prev
        wrong_rhs_add = sp.simplify(rhs_prev + const_l_prev)
        correct_rhs = sp.simplify(rhs_prev - const_l_prev)

        # Comprobar si rhs_curr coincide con haber sumado en vez de restar
        if sp.simplify(rhs_curr - wrong_rhs_add) == 0:
            val_int = int(const_l_prev) if const_l_prev.is_integer else const_l_prev
            op_needed = f"restar {const_l_prev}" if const_l_prev > 0 else f"sumar {-const_l_prev}"
            sign_str = "-" if const_l_prev > 0 else "+"
            term_str = f"+{val_int}" if const_l_prev > 0 else f"{val_int}"
            return StepReviewResult(
                is_valid=False,
                step_index=step_index,
                previous_line=prev_line,
                current_line=curr_line,
                message=(
                    f"Para eliminar el término {term_str} del lado izquierdo, debes {op_needed} en ambos lados. "
                    f"El paso correcto es {poly_l_prev.coeff_monomial(var)}*{var} = {rhs_prev} {sign_str} {abs(const_l_prev)}."
                ).replace("*", ""),
                suggested_correction=f"{poly_l_prev.coeff_monomial(var)}*{var} = {correct_rhs}".replace("*", "")
            )

    # Diagnóstico B: Error al despejar el coeficiente (multiplicó en vez de dividir o no dividió ambos)
    if a_prev != 1 and a_prev != 0:
        # Por ejemplo: de 2x = 8 pasó a x = 8 (olvidó dividir) o x = 16 (multiplicó)
        if a_curr == 1:
            # Despejó x, pero ¿qué valor puso a la derecha?
            expected_val = sp.Rational(-b_prev, a_prev)
            actual_val = -b_curr
            if actual_val == -b_prev:
                return StepReviewResult(
                    is_valid=False,
                    step_index=step_index,
                    previous_line=prev_line,
                    current_line=curr_line,
                    message=f"Para despejar {var}, debes dividir ambos miembros entre su coeficiente {a_prev}. El paso correcto es {var} = {-b_prev} / {a_prev} = {expected_val}.",
                    suggested_correction=f"{var} = {expected_val}"
                )
            elif actual_val == -b_prev * a_prev:
                return StepReviewResult(
                    is_valid=False,
                    step_index=step_index,
                    previous_line=prev_line,
                    current_line=curr_line,
                    message=f"Has multiplicado en vez de dividir. Como {a_prev} multiplica a {var}, la operación inversa para despejar es dividir entre {a_prev}.",
                    suggested_correction=f"{var} = {expected_val}"
                )

    # Diagnóstico genérico no verificado
    return StepReviewResult(
        is_valid=False,
        step_index=step_index,
        previous_line=prev_line,
        current_line=curr_line,
        message="Esta transición no mantiene la igualdad matemática respecto a la ecuación anterior. Revisa las operaciones realizadas en ambos miembros.",
        suggested_correction=None
    )


def review_student_procedure(lines: List[str]) -> List[StepReviewResult]:
    """
    Revisa un procedimiento completo entregado por el estudiante línea por línea.
    Identifica la primera transición incorrecta y detalla las razones.
    """
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    if len(cleaned_lines) < 2:
        return []

    results = []
    for i in range(len(cleaned_lines) - 1):
        prev = cleaned_lines[i]
        curr = cleaned_lines[i+1]
        res = check_linear_step_transition(prev, curr, step_index=i+1)
        results.append(res)
        if not res.is_valid:
            # Detenerse en el primer error para retroalimentación enfocada
            break

    return results
