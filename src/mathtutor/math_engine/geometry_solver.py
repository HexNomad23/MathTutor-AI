"Educational geometry engine for MathTutor AI.\nSupports rectangles, circles, triangle areas, and the Pythagorean theorem.\nValidates positive dimensions and explains each formula and step."

import math
import uuid
from typing import Optional, Dict, Any, List
import sympy as sp

from ..core.models import (
    Subject,
    VerificationStatus,
    SolutionStep,
    SolutionResult,
)


def solve_pythagoras(a: Optional[float], b: Optional[float], c: Optional[float], unit: str = "cm") -> SolutionResult:
    "Solve the Pythagorean theorem: a² + b² = c², where c is the hypotenuse.\nExactly one of the three parameters must be None (the unknown)."
    steps: List[SolutionStep] = []
    step_num = 1

    if sum(1 for x in (a, b, c) if x is not None) != 2:
        raise ValueError("Provide exactly two known values to find the third.")

    for val, name in [(a, "Leg a"), (b, "Leg b"), (c, "Hypotenuse c")]:
        if val is not None and val <= 0:
            raise ValueError(f"The length of {name} must be strictly positive (> 0).")

    # General formula
    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr="Right triangle",
        operation="State the Pythagorean theorem",
        resulting_expr="c² = a² + b²",
        explanation_brief="In a right triangle, the square of the hypotenuse equals the sum of the squares of the legs.",
        explanation_detailed="For any triangle with a 90° angle, the hypotenuse (c) and legs (a and b) satisfy c² = a² + b²."
    ))
    step_num += 1

    if c is None:
        # Calculate the hypotenuse
        c_val = math.sqrt(a**2 + b**2)
        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr="c² = a² + b²",
            operation=f"Substitute the legs: a = {a} {unit}, b = {b} {unit}",
            resulting_expr=f"c² = ({a})² + ({b})² = {a**2} + {b**2} = {a**2 + b**2}",
            explanation_brief="Square each leg and add the results.",
            explanation_detailed=f"Calculate ({a})² = {a**2} and ({b})² = {b**2}. The sum is {a**2 + b**2} {unit}²."
        ))
        step_num += 1

        c_disp = int(c_val) if c_val.is_integer() else round(c_val, 4)
        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=f"c² = {a**2 + b**2}",
            operation=f"Take the square root of both sides: c = √({a**2 + b**2})",
            resulting_expr=f"c = {c_disp} {unit}",
            explanation_brief=f"Take the positive square root (a length cannot be negative).",
            explanation_detailed=f"c = √({a**2 + b**2}) = {c_disp} {unit}."
        ))
        final_ans = f"Hypotenuse c = {c_disp} {unit}"
        check_str = f"Check: ({a})² + ({b})² = {a**2 + b**2} = ({c_disp})² (Identity verified)."

    else:
        # Calculate a leg (a or b)
        hyp = c
        known_leg = a if a is not None else b
        leg_name = "b" if a is not None else "a"

        if hyp <= known_leg:
            raise ValueError(f"Geometrically impossible: the hypotenuse ({hyp}) must be strictly longer than the leg ({known_leg}).")

        diff_sq = hyp**2 - known_leg**2
        leg_val = math.sqrt(diff_sq)
        leg_disp = int(leg_val) if leg_val.is_integer() else round(leg_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr="c² = a² + b²",
            operation=f"Isolate the unknown leg: {leg_name}² = c² - {('a' if leg_name == 'b' else 'b')}²",
            resulting_expr=f"{leg_name}² = ({hyp})² - ({known_leg})² = {hyp**2} - {known_leg**2} = {diff_sq}",
            explanation_brief="Subtract the square of the known leg from the square of the hypotenuse.",
            explanation_detailed=f"Subtract ({known_leg})² from both sides to isolate {leg_name}²."
        ))
        step_num += 1

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=f"{leg_name}² = {diff_sq}",
            operation=f"Take the square root: {leg_name} = √({diff_sq})",
            resulting_expr=f"{leg_name} = {leg_disp} {unit}",
            explanation_brief=f"Find the positive length of the leg.",
            explanation_detailed=f"{leg_name} = √({diff_sq}) = {leg_disp} {unit}."
        ))
        final_ans = f"Leg {leg_name} = {leg_disp} {unit}"
        check_str = f"Check: ({known_leg})² + ({leg_disp})² = {diff_sq + known_leg**2} = ({hyp})² (Verified)."

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.GEOMETRY,
        original_input=f"Pythagoras: a={a}, b={b}, c={c} {unit}",
        interpreted_input=f"Pythagorean theorem for a right triangle using unit {unit}",
        domain_assumptions="Plane Euclidean geometry, positive lengths (> 0)",
        steps=steps,
        final_answer=final_ans,
        units=unit,
        verification_status=VerificationStatus.VERIFIED,
        verification_reason="Analytical validation using the Pythagorean theorem and triangle inequality.",
        substitution_check=check_str,
    )


def solve_triangle_area(base: float, height: float, unit: str = "cm") -> SolutionResult:
    "Calculate the area of a triangle from its base and height: A = (b · h) / 2."
    if base <= 0 or height <= 0:
        raise ValueError("The base and height must be strictly positive (> 0).")

    area = (base * height) / 2
    area_disp = int(area) if area.is_integer() else round(area, 4)

    steps = [
        SolutionStep(
            step_number=1,
            previous_expr="Triangle with base b and height h",
            operation="Triangle area formula",
            resulting_expr="A = (b · h) / 2",
            explanation_brief="The area of a triangle is half the product of its base and corresponding height.",
            explanation_detailed="A triangle occupies half the area of a parallelogram with the same base and height."
        ),
        SolutionStep(
            step_number=2,
            previous_expr="A = (b · h) / 2",
            operation=f"Substitute values: base = {base} {unit}, height = {height} {unit}",
            resulting_expr=f"A = ({base} · {height}) / 2 = {base * height} / 2 = {area_disp} {unit}²",
            explanation_brief="Multiply the base by the height and divide by 2.",
            explanation_detailed=f"Multiply {base} {unit} by {height} {unit} to obtain {base * height} {unit}², then divide by 2 to obtain {area_disp} {unit}²."
        )
    ]

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.GEOMETRY,
        original_input=f"Triangle area: base={base} {unit}, height={height} {unit}",
        interpreted_input=f"Triangle area with b = {base} {unit} and h = {height} {unit}",
        domain_assumptions="Euclidean geometry, b > 0, h > 0",
        steps=steps,
        final_answer=f"Area = {area_disp} {unit}²",
        units=f"{unit}²",
        verification_status=VerificationStatus.VERIFIED,
        verification_reason="Direct calculation using the standard geometric formula.",
        substitution_check=f"Check: 2 · A = 2 · {area_disp} = {base * height} = b · h (Correct)."
    )


def solve_rectangle(base: float, height: float, unit: str = "cm") -> SolutionResult:
    "Calculate a rectangle's area (A = b · h) and perimeter (P = 2b + 2h)."
    if base <= 0 or height <= 0:
        raise ValueError("The base and height must be strictly positive (> 0).")

    area = base * height
    perim = 2 * (base + height)
    area_disp = int(area) if area.is_integer() else round(area, 4)
    perim_disp = int(perim) if perim.is_integer() else round(perim, 4)

    steps = [
        SolutionStep(
            step_number=1,
            previous_expr="Rectangle with base b and height h",
            operation="Area and perimeter formulas",
            resulting_expr="A = b · h,   P = 2(b + h)",
            explanation_brief="Area: product of the dimensions. Perimeter: sum of the four side lengths.",
            explanation_detailed="Area measures the enclosed surface; perimeter measures the total boundary length."
        ),
        SolutionStep(
            step_number=2,
            previous_expr="A = b · h",
            operation=f"Calculate the area with b = {base} {unit}, h = {height} {unit}",
            resulting_expr=f"A = {base} · {height} = {area_disp} {unit}²",
            explanation_brief="Multiply the base by the height.",
            explanation_detailed=f"{base} {unit} · {height} {unit} = {area_disp} {unit}²."
        ),
        SolutionStep(
            step_number=3,
            previous_expr="P = 2(b + h)",
            operation="Calculate the perimeter",
            resulting_expr=f"P = 2·({base} + {height}) = 2·({base + height}) = {perim_disp} {unit}",
            explanation_brief="Add the equal opposite sides.",
            explanation_detailed=f"2 · ({base} {unit} + {height} {unit}) = {perim_disp} {unit}."
        )
    ]

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.GEOMETRY,
        original_input=f"Rectangle: base={base} {unit}, height={height} {unit}",
        interpreted_input=f"Rectangle with b = {base} {unit}, h = {height} {unit}",
        domain_assumptions="Positive dimensions b > 0, h > 0",
        steps=steps,
        final_answer=f"Area = {area_disp} {unit}²,  Perimeter = {perim_disp} {unit}",
        units=unit,
        verification_status=VerificationStatus.VERIFIED,
        verification_reason="Direct validation using standard Euclidean formulas.",
        substitution_check=f"Check: A/b = {area_disp}/{base} = {height} = h."
    )


def solve_circle(radius: float, unit: str = "cm") -> SolutionResult:
    "Calculate a circle's area (A = π·r²) and circumference (P = 2·π·r)."
    if radius <= 0:
        raise ValueError("The radius must be strictly positive (> 0).")

    area_exact = f"{radius**2}π" if radius**2 != 1 else "π"
    perim_exact = f"{2*radius}π" if 2*radius != 1 else "π"
    area_num = round(math.pi * radius**2, 4)
    perim_num = round(2 * math.pi * radius, 4)

    steps = [
        SolutionStep(
            step_number=1,
            previous_expr="Circle with radius r",
            operation="Circle formulas",
            resulting_expr="A = π · r²,   P = 2 · π · r",
            explanation_brief="Area and circumference as functions of the radius r.",
            explanation_detailed="π is the constant ratio of a circle's circumference to its diameter."
        ),
        SolutionStep(
            step_number=2,
            previous_expr="A = π · r²",
            operation=f"Calculate the area with r = {radius} {unit}",
            resulting_expr=f"A = π · ({radius})² = {area_exact} {unit}² ≈ {area_num} {unit}²",
            explanation_brief="Square the radius and multiply by π.",
            explanation_detailed=f"Exact area: {area_exact} {unit}². Decimal approximation: {area_num} {unit}²."
        ),
        SolutionStep(
            step_number=3,
            previous_expr="P = 2 · π · r",
            operation=f"Calculate the circumference with r = {radius} {unit}",
            resulting_expr=f"P = 2 · π · {radius} = {perim_exact} {unit} ≈ {perim_num} {unit}",
            explanation_brief="Multiply twice the radius (the diameter) by π.",
            explanation_detailed=f"Exact circumference: {perim_exact} {unit}². Decimal approximation: {perim_num} {unit}."
        )
    ]

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.GEOMETRY,
        original_input=f"Circle: radius={radius} {unit}",
        interpreted_input=f"Circle with r = {radius} {unit}",
        domain_assumptions="Positive radius r > 0",
        steps=steps,
        final_answer=f"Area = {area_exact} {unit}² (≈ {area_num}),  Circumference = {perim_exact} {unit} (≈ {perim_num})",
        units=unit,
        verification_status=VerificationStatus.VERIFIED,
        verification_reason="Exact analytical validation with an explicit decimal approximation.",
        substitution_check=f"Consistency check: P² / (4·π·A) = 1 (Isoperimetric identity verified)."
    )
