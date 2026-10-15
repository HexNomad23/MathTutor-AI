"""
Pruebas para los motores de Geometría, Física y Cálculo según la tabla 11 del mandato.
"""

import pytest
from mathtutor.math_engine.geometry_solver import (
    solve_pythagoras,
    solve_triangle_area,
    solve_rectangle,
    solve_circle,
)
from mathtutor.math_engine.physics_solver import (
    solve_mru,
    solve_newton_second_law,
    convert_units,
)
from mathtutor.math_engine.calculus_solver import (
    solve_polynomial_derivative,
    solve_polynomial_integral,
)


def test_geometry_pythagoras_3_4_5():
    sol = solve_pythagoras(a=3, b=4, c=None, unit="cm")
    assert "5" in sol.final_answer
    assert "Hipotenusa" in sol.final_answer


def test_geometry_triangle_area():
    sol = solve_triangle_area(base=10, height=6, unit="cm")
    assert "30" in sol.final_answer
    assert "cm²" in sol.final_answer


def test_geometry_invalid_dimensions():
    with pytest.raises(ValueError):
        solve_triangle_area(base=-5, height=10)

    with pytest.raises(ValueError):
        # Hipotenusa menor que el cateto
        solve_pythagoras(a=10, b=None, c=5)


def test_physics_mru_150m_10s():
    sol = solve_mru(d=150, v=None, t=10)
    assert "15" in sol.final_answer
    assert "m/s" in sol.final_answer


def test_physics_newton_2kg_3mps2():
    sol = solve_newton_second_law(F=None, m=2, a=3)
    assert "6" in sol.final_answer
    assert "N" in sol.final_answer


def test_physics_conversion_72_kmh():
    sol = convert_units(72, "km/h", "m/s")
    assert "20" in sol.final_answer
    assert "m/s" in sol.final_answer


def test_physics_invalid_data():
    with pytest.raises(ValueError):
        solve_mru(d=100, v=None, t=0)  # División entre cero


def test_calculus_derivative_3x2_plus_2x_minus_5():
    sol = solve_polynomial_derivative("3x^2 + 2x - 5")
    # 6x + 2
    assert "6x + 2" in sol.final_answer or "6*x + 2" in sol.final_answer


def test_calculus_integral_2x_plus_3():
    sol = solve_polynomial_integral("2x + 3")
    # x^2 + 3x + C
    assert "x^2 + 3x + C" in sol.final_answer or "x^2 + 3*x + C" in sol.final_answer
