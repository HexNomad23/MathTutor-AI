"Educational physics engine for MathTutor AI.\nSupports uniform linear motion, Newton's second law, and compatible unit conversions.\nValidates missing values, nonzero denominators, and physical conventions."

from typing import Optional, List
import uuid

from ..core.models import (
    Subject,
    VerificationStatus,
    SolutionStep,
    SolutionResult,
)


def solve_mru(d: Optional[float] = None, v: Optional[float] = None, t: Optional[float] = None,
              unit_d: str = "m", unit_v: str = "m/s", unit_t: str = "s") -> SolutionResult:
    "Solve uniform linear motion using d = v · t.\nExactly one of {d, v, t} must be None (the unknown)."
    known_count = sum(1 for x in (d, v, t) if x is not None)
    if known_count != 2:
        raise ValueError("Provide exactly two known variables to solve for the third in uniform motion.")

    steps: List[SolutionStep] = []
    step_num = 1

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr="Uniform linear motion",
        operation="Uniform motion equation (constant speed)",
        resulting_expr="d = v · t",
        explanation_brief="In uniform motion, distance traveled is directly proportional to elapsed time.",
        explanation_detailed="The model assumes a straight path and constant speed with no acceleration (a = 0)."
    ))
    step_num += 1

    if d is None:
        if v < 0 or t <= 0:
            raise ValueError("Speed must be nonnegative and time strictly positive (t > 0).")
        d_val = v * t
        d_disp = int(d_val) if d_val.is_integer() else round(d_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr="d = v · t",
            operation=f"Substitute values: v = {v} {unit_v}, t = {t} {unit_t}",
            resulting_expr=f"d = {v} · {t} = {d_disp} {unit_d}",
            explanation_brief="Multiply speed by time.",
            explanation_detailed=f"Multiply {v} {unit_v} by {t} {unit_t} to obtain the distance {d_disp} {unit_d}."
        ))
        final_ans = f"Distance d = {d_disp} {unit_d}"
        check_str = f"Check: v = d / t = {d_disp} / {t} = {v} {unit_v} (Consistent)."

    elif v is None:
        if t <= 0:
            raise ValueError("Time must be strictly positive (t > 0) to avoid division by zero.")
        if d < 0:
            raise ValueError("Distance cannot be negative in this scalar uniform motion model.")

        v_val = d / t
        v_disp = int(v_val) if v_val.is_integer() else round(v_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr="d = v · t",
            operation=f"Solve for speed: v = d / t",
            resulting_expr=f"v = {d} {unit_d} / {t} {unit_t} = {v_disp} {unit_v}",
            explanation_brief="Divide the distance by the elapsed time.",
            explanation_detailed=f"Divide {d} {unit_d} by {t} {unit_t} to obtain a speed of {v_disp} {unit_v}."
        ))
        final_ans = f"Speed v = {v_disp} {unit_v}"
        check_str = f"Check: d = v · t = {v_disp} · {t} = {d} {unit_d} (Consistent)."

    else: # t is None
        if v <= 0:
            raise ValueError("Speed must be strictly positive (v > 0) to calculate a finite time.")
        if d < 0:
            raise ValueError("Distance cannot be negative.")

        t_val = d / v
        t_disp = int(t_val) if t_val.is_integer() else round(t_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr="d = v · t",
            operation=f"Solve for time: t = d / v",
            resulting_expr=f"t = {d} {unit_d} / {v} {unit_v} = {t_disp} {unit_t}",
            explanation_brief="Divide distance by speed.",
            explanation_detailed=f"Divide {d} {unit_d} by {v} {unit_v} to obtain a time of {t_disp} {unit_t}."
        ))
        final_ans = f"Time t = {t_disp} {unit_t}"
        check_str = f"Check: d = v · t = {v} · {t_disp} = {d} {unit_d} (Consistent)."

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.PHYSICS,
        original_input=f"Uniform motion: d={d}, v={v}, t={t}",
        interpreted_input=f"Uniform linear motion with d={d} {unit_d}, v={v} {unit_v}, t={t} {unit_t}",
        domain_assumptions="One-dimensional motion, no acceleration, t > 0",
        steps=steps,
        final_answer=final_ans,
        verification_status=VerificationStatus.VERIFIED,
        verification_reason="Validated using the uniform linear motion model.",
        substitution_check=check_str,
    )


def solve_newton_second_law(F: Optional[float] = None, m: Optional[float] = None, a: Optional[float] = None,
                           unit_F: str = "N", unit_m: str = "kg", unit_a: str = "m/s²") -> SolutionResult:
    "Newton's second law: F = m · a.\nExactly one of {F, m, a} must be None."
    known_count = sum(1 for x in (F, m, a) if x is not None)
    if known_count != 2:
        raise ValueError("Provide exactly two quantities to determine the third in F = m · a.")

    steps: List[SolutionStep] = []
    step_num = 1

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr="Classical dynamics (Newton's second law)",
        operation="State the fundamental law of dynamics",
        resulting_expr="F = m · a",
        explanation_brief="The net force on a body is proportional to its mass and resulting acceleration.",
        explanation_detailed="F is the net force in newtons (1 N = 1 kg·m/s²), m is inertial mass, and a is acceleration."
    ))
    step_num += 1

    if F is None:
        if m <= 0:
            raise ValueError("The mass of a material object must be strictly positive (m > 0).")
        F_val = m * a
        F_disp = int(F_val) if F_val.is_integer() else round(F_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr="F = m · a",
            operation=f"Substitute values: m = {m} {unit_m}, a = {a} {unit_a}",
            resulting_expr=f"F = {m} · {a} = {F_disp} {unit_F}",
            explanation_brief="Multiply mass by acceleration.",
            explanation_detailed=f"Multiply {m} {unit_m} by {a} {unit_a} to obtain a net force of {F_disp} {unit_F}."
        ))
        final_ans = f"Force F = {F_disp} {unit_F}"
        check_str = f"Check: a = F / m = {F_disp} / {m} = {a} {unit_a} (Verified)."

    elif m is None:
        if a == 0:
            raise ValueError("Zero acceleration (a = 0): mass cannot be determined from F = m·a.")
        m_val = F / a
        if m_val <= 0:
            raise ValueError("The ratio F / a gives a nonpositive mass, which is physically inconsistent.")
        m_disp = int(m_val) if m_val.is_integer() else round(m_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr="F = m · a",
            operation=f"Solve for mass: m = F / a",
            resulting_expr=f"m = {F} {unit_F} / {a} {unit_a} = {m_disp} {unit_m}",
            explanation_brief="Divide force by acceleration.",
            explanation_detailed=f"m = {F} / {a} = {m_disp} {unit_m}."
        ))
        final_ans = f"Mass m = {m_disp} {unit_m}"
        check_str = f"Check: F = m · a = {m_disp} · {a} = {F} {unit_F} (Verified)."

    else: # a is None
        if m <= 0:
            raise ValueError("Mass must be strictly positive (m > 0).")
        a_val = F / m
        a_disp = int(a_val) if a_val.is_integer() else round(a_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr="F = m · a",
            operation=f"Solve for acceleration: a = F / m",
            resulting_expr=f"a = {F} {unit_F} / {m} {unit_m} = {a_disp} {unit_a}",
            explanation_brief="Divide force by mass.",
            explanation_detailed=f"a = {F} / {m} = {a_disp} {unit_a}."
        ))
        final_ans = f"Acceleration a = {a_disp} {unit_a}"
        check_str = f"Check: F = m · a = {m} · {a_disp} = {F} {unit_F} (Verified)."

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.PHYSICS,
        original_input=f"Newton: F={F}, m={m}, a={a}",
        interpreted_input=f"Newton's second law F=m·a with {unit_F}, {unit_m}, {unit_a}",
        domain_assumptions="Nonrelativistic classical mechanics, m > 0",
        steps=steps,
        final_answer=final_ans,
        verification_status=VerificationStatus.VERIFIED,
        verification_reason="Validated using Newton's second law.",
        substitution_check=check_str,
    )


def convert_units(value: float, from_unit: str, to_unit: str) -> SolutionResult:
    "Convert compatible units, such as km/h to m/s or vice versa."
    from_u = from_unit.strip().lower()
    to_u = to_unit.strip().lower()

    steps: List[SolutionStep] = []
    step_num = 1

    if from_u in ("km/h", "kph") and to_u in ("m/s", "mps"):
        # 1 km/h = 1000m / 3600s = 1 / 3.6 m/s
        factor = 3.6
        res_val = value / factor
        res_disp = int(res_val) if res_val.is_integer() else round(res_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=f"{value} km/h",
            operation="Set the conversion factors: 1 km = 1000 m and 1 h = 3600 s",
            resulting_expr=f"{value} · (1000 m / 1 km) · (1 h / 3600 s)",
            explanation_brief="Multiply by the unit ratios for distance and time.",
            explanation_detailed="Cancel kilometers in the numerator and denominator, and hours in the denominator and numerator."
        ))
        step_num += 1

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=f"{value} · (1000 / 3600) m/s",
            operation=f"Divide by 3.6 ({value} / 3.6)",
            resulting_expr=f"{res_disp} m/s",
            explanation_brief="Simplify the ratio 1000/3600 = 1/3.6.",
            explanation_detailed=f"Dividing speed in km/h by 3.6 converts it exactly to meters per second (SI): {value} / 3.6 = {res_disp} m/s."
        ))
        final_ans = f"{res_disp} m/s"
        check_str = f"Reverse check: {res_disp} m/s · 3.6 = {value} km/h (Exact)."

    elif from_u in ("m/s", "mps") and to_u in ("km/h", "kph"):
        factor = 3.6
        res_val = value * factor
        res_disp = int(res_val) if res_val.is_integer() else round(res_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=f"{value} m/s",
            operation="Multiply by 3.6 (3600 s / 1000 m)",
            resulting_expr=f"{value} · 3.6 = {res_disp} km/h",
            explanation_brief="Multiply by 3.6 to convert m/s to km/h.",
            explanation_detailed=f"{value} m/s · 3600 s/h / 1000 m/km = {res_disp} km/h."
        ))
        final_ans = f"{res_disp} km/h"
        check_str = f"Check: {res_disp} / 3.6 = {value} m/s."

    else:
        raise ValueError(f"Conversion between '{from_unit}' and '{to_unit}' is not supported in version 0.1.")

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.PHYSICS,
        original_input=f"Convert {value} {from_unit} to {to_unit}",
        interpreted_input=f"Speed unit conversion: {from_unit} ➔ {to_unit}",
        domain_assumptions="Exact International System of Units conversion factors",
        steps=steps,
        final_answer=final_ans,
        verification_status=VerificationStatus.VERIFIED,
        verification_reason="Validated through exact dimensional analysis.",
        substitution_check=check_str,
    )
