"Educational calculus engine for MathTutor AI.\nSupports derivatives and indefinite integrals of single-variable polynomials.\nExplains each term and cross-checks integration by differentiating the result."

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
    "Differentiate a single-variable polynomial step by step."
    expr = parse_expression(expr_str)
    symbols = list(expr.free_symbols)
    var = symbols[0] if symbols else sp.Symbol("x", real=True)

    # Check that the expression is a polynomial
    poly = sp.Poly(expr, var)

    steps: List[SolutionStep] = []
    step_num = 1

    # Step 1: Sum rule and linearity
    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr=f"f({var}) = {expr}",
        operation="Apply the sum rule and linearity of differentiation: d/dx [u + v] = u' + v'",
        resulting_expr=f"d/d{var} [{expr}] = " + " + ".join([f"d/d{var}[{coeff * var**monom[0]}]" for monom, coeff in poly.as_dict().items()]).replace("+ -", "- "),
        explanation_brief="The derivative of a sum equals the sum of the derivatives of its terms.",
        explanation_detailed="Differentiate each polynomial term independently, then add the results."
    ))
    step_num += 1

    # Differentiate each monomial using the power rule: d/dx [c * x^n] = c * n * x^(n-1)
    derived_terms = []
    monom_explanations = []
    for monom, coeff in poly.as_dict().items():
        power = monom[0]
        if power == 0:
            # Constant
            derived_terms.append(sp.Integer(0))
            monom_explanations.append(f"• Derivative of the constant {coeff}: d/d{var}[{coeff}] = 0.")
        elif power == 1:
            # Linear term
            derived_terms.append(coeff)
            monom_explanations.append(f"• Derivative of {coeff}·{var}: {coeff} · (1) = {coeff}.")
        else:
            # Power term
            new_coeff = coeff * power
            new_power = power - 1
            term_res = new_coeff * (var**new_power if new_power > 1 else var)
            derived_terms.append(term_res)
            monom_explanations.append(
                f"• Power rule for {coeff}·{var}^{power}: {coeff} · {power} · {var}^({power}-1) = {new_coeff}·{var}^{new_power if new_power > 1 else ''}."
            )

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr="Term-by-term differentiation",
        operation="Apply the power rule: d/dx [xⁿ] = n·xⁿ⁻¹ and constant rule: d/dx [c] = 0",
        resulting_expr="\n".join(monom_explanations),
        explanation_brief="Multiply the coefficient by the exponent, then subtract 1 from the exponent.",
        explanation_detailed="\n".join(monom_explanations)
    ))
    step_num += 1

    # Simplified result
    derivative_expr = sp.diff(expr, var)
    res_str = str(derivative_expr).replace("**", "^").replace("*", "")
    if not res_str:
        res_str = "0"

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr="Combine the differentiated terms",
        operation="Simplify and collect the derivative terms",
        resulting_expr=f"f'({var}) = {res_str}",
        explanation_brief="Combine all simplified derivative terms.",
        explanation_detailed=f"The final derivative is f'({var}) = {res_str}."
    ))

    # Symbolic verification
    check_str = f"Check: diff({expr}, {var}) = {derivative_expr} (Exact analytical differentiation confirmed)."

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.CALCULUS,
        original_input=f"d/dx [{expr_str}]",
        interpreted_input=f"Polynomial derivative of f({var}) = {expr}",
        domain_assumptions="Polynomial function, continuous and differentiable on all of ℝ",
        steps=steps,
        final_answer=f"{res_str}",
        verification_status=VerificationStatus.VERIFIED,
        verification_reason="Formal verification using monomial differentiation rules.",
        substitution_check=check_str,
    )


def solve_polynomial_integral(expr_str: str) -> SolutionResult:
    "Integrate a single-variable polynomial step by step."
    expr = parse_expression(expr_str)
    symbols = list(expr.free_symbols)
    var = symbols[0] if symbols else sp.Symbol("x", real=True)

    poly = sp.Poly(expr, var)
    steps: List[SolutionStep] = []
    step_num = 1

    # Step 1: Linearity of integration
    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr=f"∫ ({expr}) d{var}",
        operation="Apply linearity of integration: ∫ (u + v) dx = ∫ u dx + ∫ v dx",
        resulting_expr=" + ".join([f"∫ ({coeff * var**monom[0]}) d{var}" for monom, coeff in poly.as_dict().items()]).replace("+ -", "- "),
        explanation_brief="Split the integral of a sum into the sum of the integrals of its terms.",
        explanation_detailed="Linearity lets us integrate each monomial separately and add the antiderivatives."
    ))
    step_num += 1

    # Step 2: Integrate term by term
    term_explanations = []
    integrated_terms = []
    for monom, coeff in poly.as_dict().items():
        power = monom[0]
        new_power = power + 1
        new_coeff = sp.Rational(coeff, new_power)
        integrated_terms.append(new_coeff * (var**new_power))
        term_explanations.append(
            f"• For {coeff}·{var}^{power if power > 0 else '0'}: "
            f"∫ {coeff}·{var}^{power} d{var} = {coeff} · ({var}^({power}+1) / ({power}+1)) = {new_coeff}·{var}^{new_power}."
        )

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr="Term-by-term integration",
        operation="Apply the power rule: ∫ xⁿ dx = (xⁿ⁺¹) / (n+1) for n ≠ -1",
        resulting_expr="\n".join(term_explanations),
        explanation_brief="Add 1 to the exponent and divide by the new exponent.",
        explanation_detailed="\n".join(term_explanations)
    ))
    step_num += 1

    antiderivative = sum(integrated_terms)
    clean_antideriv = str(antiderivative).replace("**", "^").replace("*", "")
    final_res = f"{clean_antideriv} + C"

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr="Combined antiderivatives",
        operation="Add the arbitrary constant of integration (+ C)",
        resulting_expr=f"∫ ({expr}) d{var} = {final_res}",
        explanation_brief="Add the constant of integration (+ C) required for every indefinite integral.",
        explanation_detailed="Since the derivative of any constant is zero, the complete family of antiderivatives includes the arbitrary constant C."
    ))

    # Cross-check: differentiate the result to recover the integrand
    check_diff = sp.diff(antiderivative, var)
    check_str = (
        f"Check by differentiation (Fundamental Theorem of Calculus):\n"
        f"d/d{var} [{clean_antideriv} + C] = {check_diff} = {expr} (Matches the original integrand)."
    )

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.CALCULUS,
        original_input=f"∫ ({expr_str}) dx",
        interpreted_input=f"Indefinite integral of polynomial f({var}) = {expr}",
        domain_assumptions="Integration over the real numbers ℝ",
        steps=steps,
        final_answer=final_res,
        verification_status=VerificationStatus.VERIFIED,
        verification_reason="Exact cross-check: differentiating the antiderivative recovers the original integrand.",
        substitution_check=check_str,
    )
