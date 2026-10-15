"Parameterized practice generator for MathTutor AI.\nGenerates exercises with reproducible seeds and exact mathematical answers.\nSupports three difficulty levels (1–3) per topic."

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
            raise ValueError(f"Unknown practice topic: {topic}")

    @staticmethod
    def _gen_algebra_lineal(level: int, seed: int, rng: random.Random) -> GeneratedExercise:
        if level == 1:
            # One operation: x + a = b or ax = b
            if rng.choice([True, False]):
                a = rng.randint(2, 10)
                ans = rng.randint(1, 15)
                b = ans + a
                stmt = f"Solve for x: x + {a} = {b}"
                hints = [
                    f"Subtract {a} from both sides of the equation.",
                    f"The step is x = {b} - {a}."
                ]
            else:
                a = rng.randint(2, 8)
                ans = rng.randint(1, 12)
                b = a * ans
                stmt = f"Solve for x: {a}x = {b}"
                hints = [
                    f"Divide both sides by the coefficient {a}.",
                    f"The step is x = {b} / {a}."
                ]
            expl = f"The value of x is {ans}."
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
            # Two operations with integers, including negatives: ax + b = c
            a = rng.randint(2, 6)
            ans = rng.randint(-8, 8)
            b = rng.randint(-15, 15)
            c = a * ans + b
            b_str = f"+ {b}" if b >= 0 else f"- {abs(b)}"
            stmt = f"Solve for x: {a}x {b_str} = {c}"
            op_inv = f"subtract {b}" if b >= 0 else f"add {abs(b)}"
            hints = [
                f"First isolate the term containing x: {op_inv} on both sides.",
                f"Then divide the result by {a} to isolate x."
            ]
            expl = f"Subtracting {b} gives {a}x = {c - b}, and dividing by {a} gives x = {ans}."
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
            # Parentheses: a(x - b) = c
            a = rng.randint(2, 5)
            b = rng.randint(1, 6)
            ans = rng.randint(1, 10)
            c = a * (ans - b)
            stmt = f"Solve for x: {a}(x - {b}) = {c}"
            hints = [
                f"Apply the distributive property to expand the parentheses ({a}·x - {a}·{b}) or divide both sides by {a}.",
                f"Expanding gives {a}x - {a*b} = {c}. Now isolate x."
            ]
            expl = f"Expanding: {a}x - {a*b} = {c} ➔ {a}x = {c + a*b} ➔ x = {ans}."
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
        stmt = f"Find the roots of: x² - {r1+r2}x + {c} = 0"
        hints = [
            f"Find two numbers whose product is {c} and whose sum is {-(r1+r2)}.",
            f"The equation factors as (x - {r1})(x - {r2}) = 0."
        ]
        ans_str = f"{r1}, {r2}" if r1 != r2 else f"{r1}"
        acceptable = [
            ans_str,
            f"{r2}, {r1}",
            f"{r1},{r2}",
            f"{r2},{r1}",
            f"x={r1}, x={r2}",
            f"x={r1} and x={r2}",
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
            explanation=f"The roots are x = {r1} and x = {r2}."
        )

    @staticmethod
    def _gen_geometria(level: int, seed: int, rng: random.Random) -> GeneratedExercise:
        if level == 1:
            # Area of a rectangle or triangle
            b = rng.randint(4, 12)
            h = rng.randint(3, 10)
            if rng.choice([True, False]):
                area = b * h
                stmt = f"Calculate the area of a rectangle with base {b} cm and height {h} cm."
                ans_str = f"{area}"
                hints = ["Recall the rectangle formula: Area = base · height.", f"Calculate {b} · {h}."]
            else:
                area = (b * h) // 2
                h_adj = (area * 2) // b
                stmt = f"Calculate the area of a triangle with base {b} cm and height {h_adj} cm."
                ans_str = f"{area}"
                hints = ["The triangle area formula is A = (base · height) / 2.", f"Multiply {b} · {h_adj} and divide by 2."]
            return GeneratedExercise(
                exercise_id=f"geom_L1_{seed}",
                topic="geometria",
                difficulty_level=1,
                seed=seed,
                statement=stmt,
                correct_answer=ans_str,
                acceptable_answers=[ans_str, f"{ans_str} cm²", f"{ans_str}cm2"],
                hints=hints,
                explanation=f"The resulting area is {ans_str} cm²."
            )
        else:
            # Standard Pythagorean theorem
            triplets = [(3, 4, 5), (6, 8, 10), (5, 12, 13)]
            a, b, c = rng.choice(triplets)
            stmt = f"In a right triangle with legs a = {a} cm and b = {b} cm, find the hypotenuse c."
            hints = [
                "Use the Pythagorean theorem: c² = a² + b².",
                f"Calculate ({a})² + ({b})² = {a**2} + {b**2} = {c**2}, then take the square root."
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
                explanation=f"The hypotenuse is c = {c} cm."
            )

    @staticmethod
    def _gen_fisica(level: int, seed: int, rng: random.Random) -> GeneratedExercise:
        if level == 1:
            # Direct uniform motion calculation: v = d / t
            v = rng.randint(5, 25)
            t = rng.randint(2, 10)
            d = v * t
            stmt = f"An object travels {d} m in {t} s at a constant speed. What is its speed (in m/s)?"
            hints = [
                "For uniform motion, speed is v = d / t.",
                f"Divide {d} meters by {t} seconds."
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
            stmt = f"Calculate the net force (in newtons) required to accelerate a mass of {m} kg at {a} m/s²."
            hints = [
                "Apply Newton's second law: F = m · a.",
                f"Multiply the mass {m} kg by the acceleration {a} m/s²."
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
            # Derivative of a quadratic trinomial: a*x^2 + b*x + c -> 2a*x + b
            a = rng.randint(2, 5)
            b = rng.randint(2, 8)
            c = rng.randint(1, 9)
            stmt = f"Find the derivative of: f(x) = {a}x² + {b}x - {c}"
            ans = f"{2*a}x + {b}"
            hints = [
                "Apply the power rule: d/dx[x²] = 2x, d/dx[x] = 1, and a constant has derivative 0.",
                f"Multiply {a} · 2 = {2*a} for the x term; the derivative of {b}x is {b}."
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
            # Integral: a*x + b -> (a/2)x^2 + bx + C, with even a
            a = rng.choice([2, 4, 6])
            b = rng.randint(1, 7)
            stmt = f"Calculate the indefinite integral: ∫ ({a}x + {b}) dx"
            coeff = a // 2
            coeff_str = f"{coeff}" if coeff != 1 else ""
            ans = f"{coeff_str}x^2 + {b}x + C"
            hints = [
                "Apply the integration power rule: ∫ x dx = x²/2, and remember the constant + C.",
                f"The integral of {a}x is {coeff}x², and the integral of {b} is {b}x."
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
                explanation=f"The integral is {ans}."
            )
