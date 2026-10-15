"Educational reviewer for algebraic procedures and step transitions.\nDiagnoses common sign, arithmetic, and division errors and validates equivalent alternative procedures."

from dataclasses import dataclass
from typing import List, Optional, Tuple
import sympy as sp

from ..math_engine.safe_parser import parse_equation, SafeParserError


@dataclass
class StepReviewResult:
    is_valid: bool
    step_index: int  # Index of the evaluated step (1-based)
    previous_line: str
    current_line: str
    message: str
    is_alternative_valid: bool = False
    suggested_correction: Optional[str] = None


def check_linear_step_transition(prev_line: str, curr_line: str, step_index: int = 1) -> StepReviewResult:
    "Compare consecutive lines of a linear equation and identify a valid step, an equivalent alternative, or a specific error."
    try:
        lhs_prev, rhs_prev, var_prev = parse_equation(prev_line)
    except SafeParserError as e:
        return StepReviewResult(
            is_valid=False,
            step_index=step_index,
            previous_line=prev_line,
            current_line=curr_line,
            message=f"Error in the previous line: {e}"
        )

    try:
        lhs_curr, rhs_curr, var_curr = parse_equation(curr_line)
    except SafeParserError as e:
        return StepReviewResult(
            is_valid=False,
            step_index=step_index,
            previous_line=prev_line,
            current_line=curr_line,
            message=f"Syntax error in the current step: {e}"
        )

    var = var_prev

    # Differences L - R
    diff_prev = sp.expand(lhs_prev - rhs_prev)
    diff_curr = sp.expand(lhs_curr - rhs_curr)

    poly_prev = sp.Poly(diff_prev, var) if diff_prev.has(var) else sp.Poly(0, var)
    poly_curr = sp.Poly(diff_curr, var) if diff_curr.has(var) else sp.Poly(0, var)

    a_prev = poly_prev.coeff_monomial(var)
    b_prev = poly_prev.coeff_monomial(1)

    a_curr = poly_curr.coeff_monomial(var)
    b_curr = poly_curr.coeff_monomial(1)

    # 1. Check equivalence up to a nonzero scalar multiple
    # diff_curr = k * diff_prev with k != 0
    if a_prev != 0:
        ratio_a = a_curr / a_prev
        if ratio_a != 0 and sp.simplify(b_curr - ratio_a * b_prev) == 0:
            if ratio_a == 1:
                return StepReviewResult(
                    is_valid=True,
                    step_index=step_index,
                    previous_line=prev_line,
                    current_line=curr_line,
                    message="Correct and valid step."
                )
            else:
                return StepReviewResult(
                    is_valid=True,
                    step_index=step_index,
                    previous_line=prev_line,
                    current_line=curr_line,
                    message=f"Valid alternative step: the equation is equivalent (both sides multiplied by {ratio_a}).",
                    is_alternative_valid=True
                )

    # If not equivalent, diagnose the specific error
    # Diagnosis A: incorrect sign when moving a constant
    # Example: 2x + 3 = 11 became 2x = 11 + 3 instead of 11 - 3
    # Detect a left-side constant added on the right instead of subtracted
    poly_l_prev = sp.Poly(lhs_prev, var) if lhs_prev.has(var) else sp.Poly(0, var)
    const_l_prev = lhs_prev - poly_l_prev.coeff_monomial(var) * var

    if const_l_prev != 0:
        # If the student added instead of subtracting:
        # Expected right side after addition: rhs_prev + const_l_prev
        wrong_rhs_add = sp.simplify(rhs_prev + const_l_prev)
        correct_rhs = sp.simplify(rhs_prev - const_l_prev)

        # Check whether rhs_curr matches addition instead of subtraction
        if sp.simplify(rhs_curr - wrong_rhs_add) == 0:
            val_int = int(const_l_prev) if const_l_prev.is_integer else const_l_prev
            op_needed = f"subtract {const_l_prev}" if const_l_prev > 0 else f"add {-const_l_prev}"
            sign_str = "-" if const_l_prev > 0 else "+"
            term_str = f"+{val_int}" if const_l_prev > 0 else f"{val_int}"
            return StepReviewResult(
                is_valid=False,
                step_index=step_index,
                previous_line=prev_line,
                current_line=curr_line,
                message=(
                    f"To remove the term {term_str} from the left side, {op_needed} on both sides. "
                    f"The correct step is {poly_l_prev.coeff_monomial(var)}*{var} = {rhs_prev} {sign_str} {abs(const_l_prev)}."
                ).replace("*", ""),
                suggested_correction=f"{poly_l_prev.coeff_monomial(var)}*{var} = {correct_rhs}".replace("*", "")
            )

    # Diagnosis B: multiplied instead of dividing, or divided only one side
    if a_prev != 1 and a_prev != 0:
        # Example: 2x = 8 became x = 8 or x = 16
        if a_curr == 1:
            # x was isolated, but what value was placed on the right?
            expected_val = sp.Rational(-b_prev, a_prev)
            actual_val = -b_curr
            if actual_val == -b_prev:
                return StepReviewResult(
                    is_valid=False,
                    step_index=step_index,
                    previous_line=prev_line,
                    current_line=curr_line,
                    message=f"To isolate {var}, divide both sides by its coefficient {a_prev}. The correct step is {var} = {-b_prev} / {a_prev} = {expected_val}.",
                    suggested_correction=f"{var} = {expected_val}"
                )
            elif actual_val == -b_prev * a_prev:
                return StepReviewResult(
                    is_valid=False,
                    step_index=step_index,
                    previous_line=prev_line,
                    current_line=curr_line,
                    message=f"You multiplied instead of dividing. Since {a_prev} multiplies {var}, the inverse operation is to divide by {a_prev}.",
                    suggested_correction=f"{var} = {expected_val}"
                )

    # Generic unverified transition
    return StepReviewResult(
        is_valid=False,
        step_index=step_index,
        previous_line=prev_line,
        current_line=curr_line,
        message="This transition does not preserve the previous equation's equality. Check the operations on both sides.",
        suggested_correction=None
    )


def review_student_procedure(lines: List[str]) -> List[StepReviewResult]:
    "Review a student's complete procedure line by line.\nIdentify the first incorrect transition and explain why it is incorrect."
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
            # Stop at the first error to provide focused feedback
            break

    return results
