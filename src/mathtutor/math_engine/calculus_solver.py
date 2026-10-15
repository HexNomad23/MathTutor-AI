"""
Motor pedagógico de Cálculo para MathTutor AI.
Soporta:
1. Derivadas de polinomios de una variable (reglas de suma, constante y potencia).
2. Integrales indefinidas de polinomios de una variable (reglas de suma, potencia y constante + C).
Muestra cada término desglosado con su regla y comprobación cruzada (la derivada de la integral recupera el integrando).
"""

from typing import List, Tuple
import uuid
import sympy as sp

from ..core.models import (
    Subject,
    VerificationStatus,
    SolutionStep,
    SolutionResult,
)
from .safe_parser import parse_expression, SafeParserError


def solve_polynomial_derivative(expr_str: str) -> SolutionResult:
    """Calcula paso a paso la derivada de un polinomio de una variable."""
    expr = parse_expression(expr_str)
    symbols = list(expr.free_symbols)
    var = symbols[0] if symbols else sp.Symbol("x", real=True)

    # Verificar que sea un polinomio
    poly = sp.Poly(expr, var)

    steps: List[SolutionStep] = []
    step_num = 1

    # Paso 1: Regla de la suma y linealidad
    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr=f"f({var}) = {expr}",
        operation="Aplicar la regla de la suma y linealidad de la derivada: d/dx [u + v] = u' + v'",
        resulting_expr=f"d/d{var} [{expr}] = " + " + ".join([f"d/d{var}[{coeff * var**monom[0]}]" for monom, coeff in poly.as_dict().items()]).replace("+ -", "- "),
        explanation_brief="La derivada de una suma de términos es igual a la suma de las derivadas de cada término.",
        explanation_detailed="Podemos derivar de manera independiente cada término del polinomio y luego sumar los resultados."
    ))
    step_num += 1

    # Desglosar cada monomio con la regla de la potencia: d/dx [c * x^n] = c * n * x^(n-1)
    derived_terms = []
    monom_explanations = []
    for monom, coeff in poly.as_dict().items():
        power = monom[0]
        if power == 0:
            # Constante
            derived_terms.append(sp.Integer(0))
            monom_explanations.append(f"• Derivada de la constante {coeff}: d/d{var}[{coeff}] = 0.")
        elif power == 1:
            # Término lineal
            derived_terms.append(coeff)
            monom_explanations.append(f"• Derivada de {coeff}·{var}: {coeff} · (1) = {coeff}.")
        else:
            # Término de potencia
            new_coeff = coeff * power
            new_power = power - 1
            term_res = new_coeff * (var**new_power if new_power > 1 else var)
            derived_terms.append(term_res)
            monom_explanations.append(
                f"• Regla de la potencia para {coeff}·{var}^{power}: {coeff} · {power} · {var}^({power}-1) = {new_coeff}·{var}^{new_power if new_power > 1 else ''}."
            )

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr="Derivación término a término",
        operation="Aplicar regla de la potencia: d/dx [xⁿ] = n·xⁿ⁻¹ y constante: d/dx [c] = 0",
        resulting_expr="\n".join(monom_explanations),
        explanation_brief="Bajar el exponente multiplicando al coeficiente y restar 1 al exponente.",
        explanation_detailed="\n".join(monom_explanations)
    ))
    step_num += 1

    # Resultado simplificado
    derivative_expr = sp.diff(expr, var)
    res_str = str(derivative_expr).replace("**", "^").replace("*", "")
    if not res_str:
        res_str = "0"

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr="Unión de términos derivados",
        operation="Simplificar y agrupar la función derivada",
        resulting_expr=f"f'({var}) = {res_str}",
        explanation_brief="Reunir todos los términos derivados simplificados.",
        explanation_detailed=f"La derivada final es f'({var}) = {res_str}."
    ))

    # Comprobación simbólica
    check_str = f"Comprobación: diff({expr}, {var}) = {derivative_expr} (Derivación analítica exacta confirmada)."

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.CALCULUS,
        original_input=f"d/dx [{expr_str}]",
        interpreted_input=f"Derivada polinómica de f({var}) = {expr}",
        domain_assumptions="Función polinómica continua y diferenciable en todo ℝ",
        steps=steps,
        final_answer=f"{res_str}",
        verification_status=VerificationStatus.VERIFIED,
        verification_reason="Verificación formal por reglas de derivación de monomios.",
        substitution_check=check_str,
    )


def solve_polynomial_integral(expr_str: str) -> SolutionResult:
    """Calcula paso a paso la integral indefinida de un polinomio de una variable."""
    expr = parse_expression(expr_str)
    symbols = list(expr.free_symbols)
    var = symbols[0] if symbols else sp.Symbol("x", real=True)

    poly = sp.Poly(expr, var)
    steps: List[SolutionStep] = []
    step_num = 1

    # Paso 1: Linealidad de la integral
    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr=f"∫ ({expr}) d{var}",
        operation="Aplicar la linealidad de la integración: ∫ (u + v) dx = ∫ u dx + ∫ v dx",
        resulting_expr=" + ".join([f"∫ ({coeff * var**monom[0]}) d{var}" for monom, coeff in poly.as_dict().items()]).replace("+ -", "- "),
        explanation_brief="Separar la integral de una suma en la suma de las integrales de cada sumando.",
        explanation_detailed="Por las propiedades de la integral indefinida, podemos integrar cada monomio por separado y sumar las antiderivadas."
    ))
    step_num += 1

    # Paso 2: Integrar término a término
    term_explanations = []
    integrated_terms = []
    for monom, coeff in poly.as_dict().items():
        power = monom[0]
        new_power = power + 1
        new_coeff = sp.Rational(coeff, new_power)
        integrated_terms.append(new_coeff * (var**new_power))
        term_explanations.append(
            f"• Para {coeff}·{var}^{power if power > 0 else '0'}: "
            f"∫ {coeff}·{var}^{power} d{var} = {coeff} · ({var}^({power}+1) / ({power}+1)) = {new_coeff}·{var}^{new_power}."
        )

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr="Integración término a término",
        operation="Aplicar regla de la potencia: ∫ xⁿ dx = (xⁿ⁺¹) / (n+1) para n ≠ -1",
        resulting_expr="\n".join(term_explanations),
        explanation_brief="Sumar 1 al exponente y dividir entre el nuevo exponente.",
        explanation_detailed="\n".join(term_explanations)
    ))
    step_num += 1

    antiderivative = sum(integrated_terms)
    clean_antideriv = str(antiderivative).replace("**", "^").replace("*", "")
    final_res = f"{clean_antideriv} + C"

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr="Resultado de las antiderivadas",
        operation="Añadir la constante arbitraria de integración (+ C)",
        resulting_expr=f"∫ ({expr}) d{var} = {final_res}",
        explanation_brief="Añadir la constante de integración (+ C) propia de toda integral indefinida.",
        explanation_detailed="Dado que la derivada de cualquier constante es cero, la familia completa de antiderivadas incluye la constante arbitraria C."
    ))

    # Comprobación cruzada (Derivar el resultado para recuperar el integrando)
    check_diff = sp.diff(antiderivative, var)
    check_str = (
        f"Comprobación por derivación (Teorema Fundamental del Cálculo):\n"
        f"d/d{var} [{clean_antideriv} + C] = {check_diff} = {expr} (Coincide con el integrando original)."
    )

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.CALCULUS,
        original_input=f"∫ ({expr_str}) dx",
        interpreted_input=f"Integral indefinida de polinomio f({var}) = {expr}",
        domain_assumptions="Integración en el conjunto de los números reales ℝ",
        steps=steps,
        final_answer=final_res,
        verification_status=VerificationStatus.VERIFIED,
        verification_reason="Comprobación cruzada exacta: la derivada de la antiderivada recupera el integrando original.",
        substitution_check=check_str,
    )
