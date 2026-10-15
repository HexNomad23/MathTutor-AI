"""
Generador de práctica parametrizada y verificada para MathTutor AI.
Cada ejercicio se genera con una semilla reproducible (seed) y validación matemática exacta.
Soporta tres niveles de dificultad (1 a 3) por tema.
"""

import random
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class GeneratedExercise:
    exercise_id: str
    topic: str
    difficulty_level: int
    seed: int
    statement: str
    correct_answer: str
    acceptable_answers: List[str]
    hints: List[str]
    explanation: str


class ExerciseGenerator:
    TOPICS = [
        "algebra_lineal",
        "algebra_cuadratica",
        "geometria",
        "fisica",
        "calculo"
    ]

    @staticmethod
    def generate(topic: str, difficulty_level: int = 1, seed: Optional[int] = None) -> GeneratedExercise:
        if seed is None:
            seed = random.randint(1000, 999999)
        rng = random.Random(seed)

        difficulty_level = max(1, min(3, difficulty_level))

        if topic == "algebra_lineal":
            return ExerciseGenerator._gen_algebra_lineal(difficulty_level, seed, rng)
        elif topic == "algebra_cuadratica":
            return ExerciseGenerator._gen_algebra_cuadratica(difficulty_level, seed, rng)
        elif topic == "geometria":
            return ExerciseGenerator._gen_geometria(difficulty_level, seed, rng)
        elif topic == "fisica":
            return ExerciseGenerator._gen_fisica(difficulty_level, seed, rng)
        elif topic == "calculo":
            return ExerciseGenerator._gen_calculo(difficulty_level, seed, rng)
        else:
            raise ValueError(f"Tema de práctica no reconocido: {topic}")

    @staticmethod
    def _gen_algebra_lineal(level: int, seed: int, rng: random.Random) -> GeneratedExercise:
        if level == 1:
            # 1 operación: x + a = b  o  ax = b
            if rng.choice([True, False]):
                a = rng.randint(2, 10)
                ans = rng.randint(1, 15)
                b = ans + a
                stmt = f"Resuelve para x: x + {a} = {b}"
                hints = [
                    f"Resta {a} en ambos miembros de la ecuación.",
                    f"El paso es x = {b} - {a}."
                ]
            else:
                a = rng.randint(2, 8)
                ans = rng.randint(1, 12)
                b = a * ans
                stmt = f"Resuelve para x: {a}x = {b}"
                hints = [
                    f"Divide ambos miembros entre el coeficiente {a}.",
                    f"El paso es x = {b} / {a}."
                ]
            expl = f"El valor de x es {ans}."
            return GeneratedExercise(
                exercise_id=f"alg_lin_L1_{seed}",
                topic="algebra_lineal",
                difficulty_level=1,
                seed=seed,
                statement=stmt,
                correct_answer=str(ans),
                acceptable_answers=[str(ans), f"x = {ans}", f"x={ans}"],
                hints=hints,
                explanation=expl
            )

        elif level == 2:
            # 2 operaciones con enteros y posibles negativos: ax + b = c
            a = rng.randint(2, 6)
            ans = rng.randint(-8, 8)
            b = rng.randint(-15, 15)
            c = a * ans + b
            b_str = f"+ {b}" if b >= 0 else f"- {abs(b)}"
            stmt = f"Resuelve para x: {a}x {b_str} = {c}"
            op_inv = f"restar {b}" if b >= 0 else f"sumar {abs(b)}"
            hints = [
                f"Primero aísla el término con x: debes {op_inv} en ambos miembros.",
                f"Luego divide el resultado obtenido entre {a} para despejar x."
            ]
            expl = f"Restando {b} obtenemos {a}x = {c - b}, y dividiendo entre {a} resulta x = {ans}."
            return GeneratedExercise(
                exercise_id=f"alg_lin_L2_{seed}",
                topic="algebra_lineal",
                difficulty_level=2,
                seed=seed,
                statement=stmt,
                correct_answer=str(ans),
                acceptable_answers=[str(ans), f"x = {ans}", f"x={ans}"],
                hints=hints,
                explanation=expl
            )

        else:
            # Con paréntesis: a(x - b) = c
            a = rng.randint(2, 5)
            b = rng.randint(1, 6)
            ans = rng.randint(1, 10)
            c = a * (ans - b)
            stmt = f"Resuelve para x: {a}(x - {b}) = {c}"
            hints = [
                f"Aplica la propiedad distributiva para eliminar el paréntesis ({a}·x - {a}·{b}) o divide ambos miembros entre {a}.",
                f"Si distribuyes, obtienes {a}x - {a*b} = {c}. Ahora despeja x."
            ]
            expl = f"Expandiendo: {a}x - {a*b} = {c} ➔ {a}x = {c + a*b} ➔ x = {ans}."
            return GeneratedExercise(
                exercise_id=f"alg_lin_L3_{seed}",
                topic="algebra_lineal",
                difficulty_level=3,
                seed=seed,
                statement=stmt,
                correct_answer=str(ans),
                acceptable_answers=[str(ans), f"x = {ans}", f"x={ans}"],
                hints=hints,
                explanation=expl
            )

    @staticmethod
    def _gen_algebra_cuadratica(level: int, seed: int, rng: random.Random) -> GeneratedExercise:
        r1 = rng.randint(1, 5)
        r2 = rng.randint(2, 6)
        if r1 > r2:
            r1, r2 = r2, r1
        # (x - r1)(x - r2) = x^2 - (r1+r2)x + r1*r2 = 0
        b = -(r1 + r2)
        c = r1 * r2
        stmt = f"Halla las raíces de: x² - {r1+r2}x + {c} = 0"
        hints = [
            f"Busca dos números que multiplicados den {c} y sumados den {-(r1+r2)}.",
            f"La ecuación se factoriza como (x - {r1})(x - {r2}) = 0."
        ]
        ans_str = f"{r1}, {r2}" if r1 != r2 else f"{r1}"
        acceptable = [
            ans_str,
            f"{r2}, {r1}",
            f"{r1},{r2}",
            f"{r2},{r1}",
            f"x={r1}, x={r2}",
            f"x={r1} y x={r2}",
        ]
        return GeneratedExercise(
            exercise_id=f"alg_cuad_L{level}_{seed}",
            topic="algebra_cuadratica",
            difficulty_level=level,
            seed=seed,
            statement=stmt,
            correct_answer=ans_str,
            acceptable_answers=acceptable,
            hints=hints,
            explanation=f"Las raíces son x = {r1} y x = {r2}."
        )

    @staticmethod
    def _gen_geometria(level: int, seed: int, rng: random.Random) -> GeneratedExercise:
        if level == 1:
            # Área de rectángulo o triángulo
            b = rng.randint(4, 12)
            h = rng.randint(3, 10)
            if rng.choice([True, False]):
                area = b * h
                stmt = f"Calcula el área de un rectángulo con base {b} cm y altura {h} cm."
                ans_str = f"{area}"
                hints = ["Recuerda la fórmula del rectángulo: Área = base · altura.", f"Calcula {b} · {h}."]
            else:
                area = (b * h) // 2
                h_adj = (area * 2) // b
                stmt = f"Calcula el área de un triángulo con base {b} cm y altura {h_adj} cm."
                ans_str = f"{area}"
                hints = ["La fórmula del área del triángulo es A = (base · altura) / 2.", f"Multiplica {b} · {h_adj} y divide entre 2."]
            return GeneratedExercise(
                exercise_id=f"geom_L1_{seed}",
                topic="geometria",
                difficulty_level=1,
                seed=seed,
                statement=stmt,
                correct_answer=ans_str,
                acceptable_answers=[ans_str, f"{ans_str} cm²", f"{ans_str}cm2"],
                hints=hints,
                explanation=f"El área resultante es {ans_str} cm²."
            )
        else:
            # Pitágoras clásico
            triplets = [(3, 4, 5), (6, 8, 10), (5, 12, 13)]
            a, b, c = rng.choice(triplets)
            stmt = f"En un triángulo rectángulo con catetos a = {a} cm y b = {b} cm, halla la hipotenusa c."
            hints = [
                "Usa el Teorema de Pitágoras: c² = a² + b².",
                f"Calcula ({a})² + ({b})² = {a**2} + {b**2} = {c**2}, y aplica la raíz cuadrada."
            ]
            return GeneratedExercise(
                exercise_id=f"geom_L2_{seed}",
                topic="geometria",
                difficulty_level=level,
                seed=seed,
                statement=stmt,
                correct_answer=str(c),
                acceptable_answers=[str(c), f"{c} cm", f"{c}cm", f"c={c}"],
                hints=hints,
                explanation=f"La hipotenusa mide c = {c} cm."
            )

    @staticmethod
    def _gen_fisica(level: int, seed: int, rng: random.Random) -> GeneratedExercise:
        if level == 1:
            # MRU directo: v = d / t
            v = rng.randint(5, 25)
            t = rng.randint(2, 10)
            d = v * t
            stmt = f"Un móvil recorre {d} m en {t} s con rapidez constante. ¿Cuál es su rapidez (en m/s)?"
            hints = [
                "En MRU la rapidez se calcula con v = d / t.",
                f"Divide {d} metros entre {t} segundos."
            ]
            return GeneratedExercise(
                exercise_id=f"fis_L1_{seed}",
                topic="fisica",
                difficulty_level=1,
                seed=seed,
                statement=stmt,
                correct_answer=str(v),
                acceptable_answers=[str(v), f"{v} m/s", f"{v}m/s"],
                hints=hints,
                explanation=f"v = {d} / {t} = {v} m/s."
            )
        else:
            # F = m · a
            m = rng.randint(2, 8)
            a = rng.randint(2, 6)
            F = m * a
            stmt = f"Calcula la fuerza neta (en Newtons) necesaria para acelerar una masa de {m} kg a {a} m/s²."
            hints = [
                "Aplica la Segunda Ley de Newton: F = m · a.",
                f"Multiplica la masa {m} kg por la aceleración {a} m/s²."
            ]
            return GeneratedExercise(
                exercise_id=f"fis_L2_{seed}",
                topic="fisica",
                difficulty_level=level,
                seed=seed,
                statement=stmt,
                correct_answer=str(F),
                acceptable_answers=[str(F), f"{F} N", f"{F}N"],
                hints=hints,
                explanation=f"F = {m} · {a} = {F} N."
            )

    @staticmethod
    def _gen_calculo(level: int, seed: int, rng: random.Random) -> GeneratedExercise:
        if level <= 2:
            # Derivada de trinomio cuadrático: a*x^2 + b*x + c -> 2a*x + b
            a = rng.randint(2, 5)
            b = rng.randint(2, 8)
            c = rng.randint(1, 9)
            stmt = f"Halla la derivada de: f(x) = {a}x² + {b}x - {c}"
            ans = f"{2*a}x + {b}"
            hints = [
                "Aplica la regla de la potencia: d/dx[x²] = 2x, d/dx[x] = 1, y la constante da 0.",
                f"Multiplica {a} · 2 = {2*a} para el término x, y la derivada de {b}x es {b}."
            ]
            return GeneratedExercise(
                exercise_id=f"calc_L{level}_{seed}",
                topic="calculo",
                difficulty_level=level,
                seed=seed,
                statement=stmt,
                correct_answer=ans,
                acceptable_answers=[ans, f"{2*a}*x + {b}", f"{2*a}x+{b}"],
                hints=hints,
                explanation=f"f'(x) = {ans}."
            )
        else:
            # Integral: a*x + b -> (a/2)x^2 + bx + C con a par
            a = rng.choice([2, 4, 6])
            b = rng.randint(1, 7)
            stmt = f"Calcula la integral indefinida: ∫ ({a}x + {b}) dx"
            coeff = a // 2
            coeff_str = f"{coeff}" if coeff != 1 else ""
            ans = f"{coeff_str}x^2 + {b}x + C"
            hints = [
                "Aplica la regla de la potencia para la integral: ∫ x dx = x²/2 y no olvides la constante + C.",
                f"La integral de {a}x es {coeff}x², y la de {b} es {b}x."
            ]
            return GeneratedExercise(
                exercise_id=f"calc_L3_{seed}",
                topic="calculo",
                difficulty_level=3,
                seed=seed,
                statement=stmt,
                correct_answer=ans,
                acceptable_answers=[
                    ans,
                    f"{coeff_str}x² + {b}x + C",
                    f"{coeff_str}x^2+{b}x+C",
                    f"{coeff}*x^2 + {b}*x + C"
                ],
                hints=hints,
                explanation=f"La integral es {ans}."
            )
