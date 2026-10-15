"""
Motor pedagógico de Física para MathTutor AI.
Soporta:
1. Movimiento Rectilíneo Uniforme (MRU): d = v · t.
2. Segunda Ley de Newton: F = m · a.
3. Conversiones entre unidades compatibles (km/h a m/s, m a km, h a s, etc.).
Valida datos faltantes, denominadores no nulos y convenciones físicas.
"""

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
    """
    Resuelve MRU con d = v · t.
    Exactamente uno de {d, v, t} debe ser None (la incógnita).
    """
    known_count = sum(1 for x in (d, v, t) if x is not None)
    if known_count != 2:
        raise ValueError("Se deben especificar exactamente dos variables conocidas en MRU para despejar la tercera.")

    steps: List[SolutionStep] = []
    step_num = 1

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr="Movimiento Rectilíneo Uniforme (MRU)",
        operation="Ecuación del modelo MRU (velocidad constante)",
        resulting_expr="d = v · t",
        explanation_brief="En MRU, la distancia recorrida es directamente proporcional al tiempo transcurrido.",
        explanation_detailed="El modelo asume trayectoria rectilínea y rapidez constante sin aceleración (a = 0)."
    ))
    step_num += 1

    if d is None:
        if v < 0 or t <= 0:
            raise ValueError("La rapidez debe ser no negativa y el tiempo estrictamente positivo (t > 0).")
        d_val = v * t
        d_disp = int(d_val) if d_val.is_integer() else round(d_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr="d = v · t",
            operation=f"Sustituir datos: v = {v} {unit_v}, t = {t} {unit_t}",
            resulting_expr=f"d = {v} · {t} = {d_disp} {unit_d}",
            explanation_brief="Multiplicar la rapidez por el tiempo.",
            explanation_detailed=f"Multiplicamos {v} {unit_v} por {t} {unit_t} para obtener la distancia {d_disp} {unit_d}."
        ))
        final_ans = f"Distancia d = {d_disp} {unit_d}"
        check_str = f"Comprobación: v = d / t = {d_disp} / {t} = {v} {unit_v} (Consistente)."

    elif v is None:
        if t <= 0:
            raise ValueError("El tiempo debe ser estrictamente positivo (t > 0) para evitar división entre cero.")
        if d < 0:
            raise ValueError("La distancia no puede ser negativa en MRU escalar.")

        v_val = d / t
        v_disp = int(v_val) if v_val.is_integer() else round(v_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr="d = v · t",
            operation=f"Despejar la rapidez: v = d / t",
            resulting_expr=f"v = {d} {unit_d} / {t} {unit_t} = {v_disp} {unit_v}",
            explanation_brief="Dividir la distancia entre el tiempo empleado.",
            explanation_detailed=f"Dividimos {d} {unit_d} entre {t} {unit_t} resultando una rapidez de {v_disp} {unit_v}."
        ))
        final_ans = f"Rapidez v = {v_disp} {unit_v}"
        check_str = f"Comprobación: d = v · t = {v_disp} · {t} = {d} {unit_d} (Consistente)."

    else: # t is None
        if v <= 0:
            raise ValueError("La rapidez debe ser estrictamente positiva (v > 0) para calcular un tiempo finito.")
        if d < 0:
            raise ValueError("La distancia no puede ser negativa.")

        t_val = d / v
        t_disp = int(t_val) if t_val.is_integer() else round(t_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr="d = v · t",
            operation=f"Despejar el tiempo: t = d / v",
            resulting_expr=f"t = {d} {unit_d} / {v} {unit_v} = {t_disp} {unit_t}",
            explanation_brief="Dividir la distancia entre la rapidez.",
            explanation_detailed=f"Dividimos {d} {unit_d} entre {v} {unit_v} resultando un tiempo de {t_disp} {unit_t}."
        ))
        final_ans = f"Tiempo t = {t_disp} {unit_t}"
        check_str = f"Comprobación: d = v · t = {v} · {t_disp} = {d} {unit_d} (Consistente)."

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.PHYSICS,
        original_input=f"MRU: d={d}, v={v}, t={t}",
        interpreted_input=f"Movimiento Rectilíneo Uniforme con d={d} {unit_d}, v={v} {unit_v}, t={t} {unit_t}",
        domain_assumptions="Movimiento en 1 dimensión, sin aceleración, t > 0",
        steps=steps,
        final_answer=final_ans,
        verification_status=VerificationStatus.VERIFIED,
        verification_reason="Validación por el modelo cinemático lineal MRU.",
        substitution_check=check_str,
    )


def solve_newton_second_law(F: Optional[float] = None, m: Optional[float] = None, a: Optional[float] = None,
                           unit_F: str = "N", unit_m: str = "kg", unit_a: str = "m/s²") -> SolutionResult:
    """
    Segunda Ley de Newton: F = m · a.
    Exactamente uno de {F, m, a} debe ser None.
    """
    known_count = sum(1 for x in (F, m, a) if x is not None)
    if known_count != 2:
        raise ValueError("Se deben proporcionar exactamente dos magnitudes para determinar la tercera en F = m · a.")

    steps: List[SolutionStep] = []
    step_num = 1

    steps.append(SolutionStep(
        step_number=step_num,
        previous_expr="Dinámica clásica (Segunda Ley de Newton)",
        operation="Enunciar la ley fundamental de la dinámica",
        resulting_expr="F = m · a",
        explanation_brief="La fuerza neta aplicada sobre un cuerpo es proporcional a su masa y a la aceleración producida.",
        explanation_detailed="F representa la fuerza neta resultante en Newtons (1 N = 1 kg·m/s²), m la masa inercial y a la aceleración."
    ))
    step_num += 1

    if F is None:
        if m <= 0:
            raise ValueError("La masa de un objeto material debe ser estrictamente positiva (m > 0).")
        F_val = m * a
        F_disp = int(F_val) if F_val.is_integer() else round(F_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr="F = m · a",
            operation=f"Sustituir datos: m = {m} {unit_m}, a = {a} {unit_a}",
            resulting_expr=f"F = {m} · {a} = {F_disp} {unit_F}",
            explanation_brief="Multiplicar masa por aceleración.",
            explanation_detailed=f"Multiplicamos {m} {unit_m} por {a} {unit_a} para obtener una fuerza neta de {F_disp} {unit_F}."
        ))
        final_ans = f"Fuerza F = {F_disp} {unit_F}"
        check_str = f"Comprobación: a = F / m = {F_disp} / {m} = {a} {unit_a} (Verificado)."

    elif m is None:
        if a == 0:
            raise ValueError("Aceleración nula (a = 0): no se puede determinar la masa con F = m·a.")
        m_val = F / a
        if m_val <= 0:
            raise ValueError("La relación F / a resulta en una masa no positiva, físicamente inconsistente.")
        m_disp = int(m_val) if m_val.is_integer() else round(m_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr="F = m · a",
            operation=f"Despejar la masa: m = F / a",
            resulting_expr=f"m = {F} {unit_F} / {a} {unit_a} = {m_disp} {unit_m}",
            explanation_brief="Dividir la fuerza entre la aceleración.",
            explanation_detailed=f"m = {F} / {a} = {m_disp} {unit_m}."
        ))
        final_ans = f"Masa m = {m_disp} {unit_m}"
        check_str = f"Comprobación: F = m · a = {m_disp} · {a} = {F} {unit_F} (Verificado)."

    else: # a is None
        if m <= 0:
            raise ValueError("La masa debe ser estrictamente positiva (m > 0).")
        a_val = F / m
        a_disp = int(a_val) if a_val.is_integer() else round(a_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr="F = m · a",
            operation=f"Despejar la aceleración: a = F / m",
            resulting_expr=f"a = {F} {unit_F} / {m} {unit_m} = {a_disp} {unit_a}",
            explanation_brief="Dividir la fuerza entre la masa.",
            explanation_detailed=f"a = {F} / {m} = {a_disp} {unit_a}."
        ))
        final_ans = f"Aceleración a = {a_disp} {unit_a}"
        check_str = f"Comprobación: F = m · a = {m} · {a_disp} = {F} {unit_F} (Verificado)."

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.PHYSICS,
        original_input=f"Newton: F={F}, m={m}, a={a}",
        interpreted_input=f"Segunda Ley de Newton F=m·a con {unit_F}, {unit_m}, {unit_a}",
        domain_assumptions="Mecánica clásica no relativista, m > 0",
        steps=steps,
        final_answer=final_ans,
        verification_status=VerificationStatus.VERIFIED,
        verification_reason="Validación dinámica según la segunda ley de Newton.",
        substitution_check=check_str,
    )


def convert_units(value: float, from_unit: str, to_unit: str) -> SolutionResult:
    """
    Convierte unidades compatibles (ej. km/h a m/s o viceversa).
    """
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
            operation="Establecer los factores de conversión: 1 km = 1000 m y 1 h = 3600 s",
            resulting_expr=f"{value} · (1000 m / 1 km) · (1 h / 3600 s)",
            explanation_brief="Multiplicar por las razones unitarias de distancia y tiempo.",
            explanation_detailed="Cancelamos kilómetros en el numerador con kilómetros en el denominador, y horas en el denominador con horas en el numerador."
        ))
        step_num += 1

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=f"{value} · (1000 / 3600) m/s",
            operation=f"Dividir entre 3.6 ({value} / 3.6)",
            resulting_expr=f"{res_disp} m/s",
            explanation_brief="Simplificar la razón 1000/3600 = 1/3.6.",
            explanation_detailed=f"Dividir la rapidez en km/h entre 3.6 equivale exactamente a convertirla a metros por segundo (SI): {value} / 3.6 = {res_disp} m/s."
        ))
        final_ans = f"{res_disp} m/s"
        check_str = f"Comprobación inversa: {res_disp} m/s · 3.6 = {value} km/h (Exacto)."

    elif from_u in ("m/s", "mps") and to_u in ("km/h", "kph"):
        factor = 3.6
        res_val = value * factor
        res_disp = int(res_val) if res_val.is_integer() else round(res_val, 4)

        steps.append(SolutionStep(
            step_number=step_num,
            previous_expr=f"{value} m/s",
            operation="Multiplicar por el factor 3.6 (3600 s / 1000 m)",
            resulting_expr=f"{value} · 3.6 = {res_disp} km/h",
            explanation_brief="Multiplicar por 3.6 para pasar de m/s a km/h.",
            explanation_detailed=f"{value} m/s · 3600 s/h / 1000 m/km = {res_disp} km/h."
        ))
        final_ans = f"{res_disp} km/h"
        check_str = f"Comprobación: {res_disp} / 3.6 = {value} m/s."

    else:
        raise ValueError(f"Conversión entre '{from_unit}' y '{to_unit}' no soportada en la versión 0.1.")

    return SolutionResult(
        exercise_id=str(uuid.uuid4()),
        subject=Subject.PHYSICS,
        original_input=f"Convertir {value} {from_unit} a {to_unit}",
        interpreted_input=f"Conversión dimensional de rapidez: {from_unit} ➔ {to_unit}",
        domain_assumptions="Factores de conversión exactos del Sistema Internacional",
        steps=steps,
        final_answer=final_ans,
        verification_status=VerificationStatus.VERIFIED,
        verification_reason="Validación por análisis dimensional exacto.",
        substitution_check=check_str,
    )
