"""
Pruebas para el solucionador algebraico y el revisor de pasos de MathTutor AI.
Verifica los casos requeridos por la tabla 11 del mandato.
"""

import pytest
from mathtutor.math_engine.algebra_solver import (
    solve_linear_equation,
    solve_quadratic_equation,
)
from mathtutor.tutor.step_reviewer import (
    check_linear_step_transition,
    review_student_procedure,
)


def test_algebra_2x_plus_3_equals_11():
    sol = solve_linear_equation("2x + 3 = 11")
    assert sol.final_answer == "x = 4"
    assert len(sol.steps) >= 3
    assert sol.substitution_check is not None
    assert "11 = 11" in sol.substitution_check


def test_algebra_parentheses():
    sol = solve_linear_equation("3(x - 2) = 12")
    assert sol.final_answer == "x = 6"


def test_algebra_quadratic_factoring():
    sol = solve_quadratic_equation("x^2 - 5x + 6 = 0")
    assert "x = 2" in sol.final_answer
    assert "x = 3" in sol.final_answer
    assert sol.substitution_check is not None


def test_algebra_quadratic_no_real_solutions():
    sol = solve_quadratic_equation("x^2 + 1 = 0")
    assert "Sin soluciones reales" in sol.final_answer


def test_algebra_infinite_solutions():
    sol = solve_linear_equation("2x + 3 = 2x + 3")
    assert "Infinitas soluciones reales" in sol.final_answer


def test_algebra_no_solution():
    sol = solve_linear_equation("2x + 3 = 2x + 5")
    assert "Sin solución" in sol.final_answer


def test_step_reviewer_erroneous_step():
    # 2x + 3 = 11 seguido de 2x = 11 + 3
    res = check_linear_step_transition("2x + 3 = 11", "2x = 11 + 3")
    assert not res.is_valid
    assert "restar 3" in res.message or "debes restar 3" in res.message


def test_step_reviewer_alternative_step():
    # 2x + 3 = 11 seguido de 4x + 6 = 22 (multiplicado por 2)
    res = check_linear_step_transition("2x + 3 = 11", "4x + 6 = 22")
    assert res.is_valid
    assert res.is_alternative_valid
