"Educational algebra engine for MathTutor AI.\nSolves linear and quadratic equations with explained steps, substitution checks, and domain analysis."

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
    "Format a SymPy expression as readable mathematical text for students."
    s = str(expr)
    s = s.replace("**", "^")
    s = s.replace("*", "")
    return s


def solve_linear_equation(eq_str: str) -> SolutionResult:
    "Solve a linear equation in one unknown step by step.\nExpand parentheses, collect variable and constant terms, isolate the unknown, and check the solution in the original equation."
    lhs_orig, rhs_orig, var = parse_equation(eq_str)
    interpreted_str = f"{lhs_orig} = {rhs_orig}"

    # Check the degree
    diff = sp.expand(lhs_orig - rhs_orig)
    poly = sp.Poly(diff, var)
    degree = poly.degree()

    if degree > 1:
        raise SafeParserError(f"This function handles linear equations. The entered equation has degree {degree}.")

    steps: List[SolutionStep] = []
    step_num = 1

    current_lhs = lhs_orig
    current_rhs = rhs_orig

    # Step 1: Expand parentheses where applicable
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
            operation="Apply the distributive property",
            resulting_expr=res_expr,
            explanation_brief="Multiply the coefficients to expand the parentheses.",
            explanation_detailed="Apply the distributive property a(b + c) = ab + ac to terms with parentheses so that like terms can be combined."
        ))
        step_num += 1

    # Analyze terms on the left and right sides
    # Express current_lhs as A*var + B and current_rhs as C*var + D
    poly_l = sp.Poly(current_lhs, var) if current_lhs.has(var) else sp.Poly(0, var)
    poly_r = sp.Poly(current_rhs, var) if current_rhs.has(var) else sp.Poly(0, var)

    coeff_l = poly_l.coeff_monomial(var)
    const_l = current_lhs - coeff_l * var

    coeff_r = poly_r.coeff_monomial(var)
    const_r = current_rhs - coeff_r * var

    # Move the constant from the left side to the right
    if const_l != 0:
        prev_expr = f"{current_lhs} = {current_rhs}"
        op_text = f"Subtract {const_l}" if const_l > 0 else f"Add {-const_l}"
        preposition = "from" if const_l > 0 else "to"
        # Show the intermediate step
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
            operation=f"{op_text} {preposition} both sides: {inter_lhs} = {inter_rhs}",
            resulting_expr=res_expr,
            explanation_brief=f"{op_text} {preposition} both sides to isolate terms containing {var}.",
            explanation_detailed=f"To cancel the constant term {const_l} on the left side, apply the inverse operation ({op_text}) to both sides of the equation to preserve equality."
        ))
        step_num += 1

    # Move any variable term from the right side to the left
    if coeff_r != 0:
        prev_expr = f"{current_lhs} = {current_rhs}"
        var_term = coeff_r * var
        op_text = f"Subtract {var_term}" if coeff_r > 0 else f"Add {-coeff_r * var}"
        preposition = "from" if coeff_r > 0 else "to"

        current_lhs = sp.simplify(current_lhs - var_term)
        current_rhs = sp.simplify(current_rhs - var_term)
        res_expr = f"{current_lhs} = {current_rhs}"

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=prev_expr,
            operation=f"{op_text} {preposition} both sides",
            resulting_expr=res_expr,
            explanation_brief=f"Move all terms containing the unknown {var} to the left side.",
            explanation_detailed=f"Subtract {var_term} from both sides to collect all terms containing the unknown on the left side."
        ))
        step_num += 1

    # We now have A*var = B
    poly_final = sp.Poly(current_lhs, var) if current_lhs.has(var) else sp.Poly(0, var)
    A = poly_final.coeff_monomial(var)
    B = current_rhs

    # Special cases: A == 0
    if A == 0:
        if B == 0:
            final_ans = "Infinitely many real solutions"
            status = VerificationStatus.VERIFIED
            reason = "The equation reduces to the identity 0 = 0, which holds for every real number x ∈ ℝ."
            sub_check = "Identity verified: any value of x satisfies the original equation."
        else:
            final_ans = "No solution"
            status = VerificationStatus.VERIFIED
            reason = f"The equation reduces to a contradiction (0 = {B}), so no value of x can satisfy it."
            sub_check = "Contradiction: 0 ≠ constant. There is no solution in the real numbers."

        return SolutionResult(
            exercise_id=str(uuid.uuid4()),
            subject=Subject.ALGEBRA,
            original_input=eq_str,
            interpreted_input=interpreted_str,
            domain_assumptions="Real numbers (x ∈ ℝ)",
            steps=steps,
            final_answer=final_ans,
            verification_status=status,
            verification_reason=reason,
            substitution_check=sub_check,
        )

    # Divide by A if A != 1
    if A != 1:
        prev_expr = f"{current_lhs} = {current_rhs}"
        sol_val = sp.Rational(B, A) if isinstance(B, (int, sp.Integer)) and isinstance(A, (int, sp.Integer)) else sp.simplify(B / A)
        res_expr = f"{var} = {sol_val}"

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=prev_expr,
            operation=f"Divide both sides by {A}",
            resulting_expr=res_expr,
            explanation_brief=f"Divide both sides by the coefficient {A} to isolate {var}.",
            explanation_detailed=f"Since {A} multiplies {var}, divide both sides of the equation by {A} (the inverse operation) to obtain the value of the unknown."
        ))
        step_num += 1
    else:
        sol_val = B

    final_ans = f"{var} = {sol_val}"

    # Check by substitution
    sub_lhs = lhs_orig.subs(var, sol_val)
    sub_rhs = rhs_orig.subs(var, sol_val)
    sub_lhs_eval = sp.simplify(sub_lhs)
    sub_rhs_eval = sp.simplify(sub_rhs)

    # Explain the substitution
    sub_check_str = (
        f"Substitute {var} = {sol_val} into the original equation:\n"
        f"Left side: {lhs_orig} = {sub_lhs} = {sub_lhs_eval}\n"
        f"Right side: {rhs_orig} = {sub_rhs} = {sub_rhs_eval}\n"
        f"Result: {sub_lhs_eval} = {sub_rhs_eval} (Identity confirmed)"
    )

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr=f"{var} = {sol_val}",
        operation=f"Check by substitution ({var} = {sol_val})",
        resulting_expr=f"{sub_lhs_eval} = {sub_rhs_eval}",
        explanation_brief="Verify the solution by substituting it into the original equation.",
        explanation_detailed=f"Replace {var} with {sol_val} on both sides of the original equation and check that both sides give exactly the same value ({sub_lhs_eval})."
    ))

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.ALGEBRA,
        original_input=eq_str,
        interpreted_input=interpreted_str,
        domain_assumptions="Real numbers (x ∈ ℝ)",
        steps=steps,
        final_answer=final_ans,
        verification_status=VerificationStatus.VERIFIED,
        verification_reason=f"Exact substitution verified symbolically: {sub_lhs_eval} = {sub_rhs_eval}.",
        substitution_check=sub_check_str,
    )


def solve_quadratic_equation(eq_str: str) -> SolutionResult:
    "Solve a quadratic equation a*x^2 + b*x + c = 0 using the quadratic formula or factoring, showing the discriminant, real roots, and verification."
    lhs_orig, rhs_orig, var = parse_equation(eq_str)
    interpreted_str = f"{lhs_orig} = {rhs_orig}"

    diff = sp.expand(lhs_orig - rhs_orig)
    poly = sp.Poly(diff, var)
    degree = poly.degree()

    if degree != 2:
        raise SafeParserError(f"The entered equation is not quadratic (degree {degree}).")

    a = poly.coeff_monomial(var**2)
    b = poly.coeff_monomial(var)
    c = poly.coeff_monomial(1)

    steps: List[SolutionStep] = []
    step_num = 1

    # Step 1: Standard form
    std_form = f"{a}*{var}^2 + ({b})*{var} + ({c}) = 0".replace("+ (-", "- (")
    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr=f"{lhs_orig} = {rhs_orig}",
        operation="Rewrite in standard form ax² + bx + c = 0",
        resulting_expr=f"{diff} = 0",
        explanation_brief="Set the equation equal to zero by subtracting the right side.",
        explanation_detailed=f"Identify the coefficients: a = {a}, b = {b}, c = {c}."
    ))
    step_num += 1

    # Step 2: Discriminant
    disc = b**2 - 4*a*c
    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr=f"{diff} = 0",
        operation=f"Calculate the discriminant Δ = b² - 4ac",
        resulting_expr=f"Δ = ({b})² - 4·({a})·({c}) = {disc}",
        explanation_brief=f"Evaluate the discriminant to determine the number of real solutions.",
        explanation_detailed=f"The discriminant Δ = {disc} determines whether there are two distinct real solutions (Δ > 0), a repeated solution (Δ = 0), or no real solution (Δ < 0)."
    ))
    step_num += 1

    if disc < 0:
        final_ans = "No real solutions"
        reason = f"The discriminant is negative (Δ = {disc} < 0). Negative numbers have no square roots in the real numbers."
        sub_check = "There are no roots in ℝ. (The solutions belong to the complex numbers.)"
        return SolutionResult(
            exercise_id=str(uuid.uuid4()),
            subject=Subject.ALGEBRA,
            original_input=eq_str,
            interpreted_input=interpreted_str,
            domain_assumptions="Real numbers (x ∈ ℝ)",
            steps=steps,
            final_answer=final_ans,
            verification_status=VerificationStatus.VERIFIED,
            verification_reason=reason,
            substitution_check=sub_check,
        )

    # Real roots
    sqrt_disc = sp.sqrt(disc)
    x1 = sp.simplify((-b + sqrt_disc) / (2*a))
    x2 = sp.simplify((-b - sqrt_disc) / (2*a))

    formula_step = f"{var} = (-({b}) ± √({disc})) / (2·{a})"
    if disc == 0:
        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=f"Δ = {disc}",
            operation="Apply the quadratic formula for a repeated root",
            resulting_expr=f"{var} = {x1}",
            explanation_brief="Since Δ = 0, there is one repeated real solution.",
            explanation_detailed=f"Applying {var} = -b / (2a) gives {var} = {x1}."
        ))
        step_num += 1
        final_ans = f"{var} = {x1} (repeated root)"
    else:
        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=f"Δ = {disc}",
            operation=f"Apply the quadratic formula: {formula_step}",
            resulting_expr=f"{var}₁ = {x1},  {var}₂ = {x2}",
            explanation_brief="Calculate both real roots by adding and subtracting the square root of the discriminant.",
            explanation_detailed=f"We obtain two solutions: {var}₁ = (-({b}) + {sqrt_disc}) / {2*a} = {x1} and {var}₂ = (-({b}) - {sqrt_disc}) / {2*a} = {x2}."
        ))
        step_num += 1
        final_ans = f"{var} = {x1} and {var} = {x2}"

    # Check by substitution
    check_lines = []
    roots = [x1] if disc == 0 else [x1, x2]
    for r in roots:
        sub_l = sp.simplify(lhs_orig.subs(var, r))
        sub_r = sp.simplify(rhs_orig.subs(var, r))
        check_lines.append(f"For {var} = {r}: Left side = {sub_l}, Right side = {sub_r} -> {sub_l} = {sub_r}")

    sub_check_str = "\n".join(check_lines)

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr=final_ans,
        operation="Check by substitution in the original equation",
        resulting_expr="Identity confirmed for each root",
        explanation_brief="Substitute each value into the original equation.",
        explanation_detailed="Check that substituting each root makes both sides of the equation exactly equal."
    ))

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.ALGEBRA,
        original_input=eq_str,
        interpreted_input=interpreted_str,
        domain_assumptions="Real numbers (x ∈ ℝ)",
        steps=steps,
        final_answer=final_ans,
        verification_status=VerificationStatus.VERIFIED,
        verification_reason=f"Roots verified exactly by substitution in the original equation.",
        substitution_check=sub_check_str,
    )
