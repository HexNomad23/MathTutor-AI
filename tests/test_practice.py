"Tests for the parameterized generator and adaptive practice engine."

import pytest
from mathtutor.practice.generator import ExerciseGenerator
from mathtutor.practice.adaptive import AdaptiveController
from mathtutor.storage.database import StorageManager
from mathtutor.core.models import StudentAttempt


def test_generator_determinism():
    ex1 = ExerciseGenerator.generate("algebra_lineal", difficulty_level=2, seed=42)
    ex2 = ExerciseGenerator.generate("algebra_lineal", difficulty_level=2, seed=42)
    assert ex1.statement == ex2.statement
    assert ex1.correct_answer == ex2.correct_answer


def test_generator_all_topics():
    for topic in ExerciseGenerator.TOPICS:
        for lvl in [1, 2, 3]:
            ex = ExerciseGenerator.generate(topic, difficulty_level=lvl, seed=123)
            assert ex.statement
            assert ex.correct_answer
            assert len(ex.hints) >= 1


def test_adaptive_insufficient_data():
    storage = StorageManager(":memory:")
    controller = AdaptiveController(storage)
    summary = controller.get_progress_summary("algebra_lineal")
    assert not summary["has_enough_data"]
    assert "There are not enough exercises" in summary["message"]


def test_adaptive_promotion_block():
    storage = StorageManager(":memory:")
    controller = AdaptiveController(storage)

    # Initial level: 1
    prog = storage.get_topic_progress("algebra_lineal")
    assert prog["current_level"] == 1

    # Four correct answers without hints
    for i in range(4):
        res = controller.process_attempt(StudentAttempt(
            topic="algebra_lineal",
            difficulty_level=1,
            user_answer="correct",
            is_correct=True,
            hints_used=0
        ))
        assert not res["level_changed"]

    # Fifth unassisted correct answer completes a 5/5 block and raises the level to 2
    res = controller.process_attempt(StudentAttempt(
        topic="algebra_lineal",
        difficulty_level=1,
        user_answer="correct",
        is_correct=True,
        hints_used=0
    ))
    assert res["level_changed"]
    assert res["new_level"] == 2
    assert "moved up to level 2" in res["action_message"]


def test_adaptive_assisted_attempts_ignored_for_block():
    storage = StorageManager(":memory:")
    controller = AdaptiveController(storage)

    # Five attempts using hints
    for i in range(5):
        res = controller.process_attempt(StudentAttempt(
            topic="algebra_lineal",
            difficulty_level=1,
            user_answer="correct",
            is_correct=True,
            hints_used=1  # Assisted
        ))
        assert not res["level_changed"]

    # The level should remain unchanged
    prog = storage.get_topic_progress("algebra_lineal")
    assert prog["current_level"] == 1
    assert prog["consecutive_unassisted"] == 0
