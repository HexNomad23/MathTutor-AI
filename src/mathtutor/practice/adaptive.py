"Adaptive practice controller for MathTutor AI.\nEvaluates blocks of five unassisted exercises: 4–5 correct raises the level, 3 keeps it, and 0–2 lowers it (levels 1–3).\nAssisted attempts are recorded but excluded from the adjustment window."

from typing import Dict, Any, List, Tuple
from ..storage.database import StorageManager
from ..core.models import StudentAttempt


class AdaptiveController:
    BLOCK_SIZE = 5

    def __init__(self, storage: StorageManager):
        self.storage = storage

    def process_attempt(self, attempt: StudentAttempt) -> Dict[str, Any]:
        "Record an attempt in SQLite and adjust the topic's difficulty after a block of five unassisted exercises."
        self.storage.record_attempt(attempt)
        topic = attempt.topic

        progress = self.storage.get_topic_progress(topic)
        current_level = progress["current_level"]
        total_attempts = progress["total_attempts"] + 1
        total_correct = progress["total_correct"] + (1 if attempt.is_correct else 0)
        history_window: List[bool] = list(progress["history_window"])

        level_changed = False
        old_level = current_level
        action_message = ""

        # Only unassisted attempts (no hints) count toward adaptation
        if attempt.hints_used == 0:
            history_window.append(attempt.is_correct)

            # Check whether a block of five is complete
            if len(history_window) >= self.BLOCK_SIZE:
                block = history_window[:self.BLOCK_SIZE]
                history_window = history_window[self.BLOCK_SIZE:]  # Clear the evaluated block

                correct_count = sum(1 for x in block if x)

                if correct_count >= 4:
                    if current_level < 3:
                        current_level += 1
                        level_changed = True
                        action_message = f"Great work! You answered {correct_count}/5 unassisted exercises correctly. You moved up to level {current_level}."
                    else:
                        action_message = f"Excellent work! {correct_count}/5 correct. You are already at the highest level ({current_level})."
                elif correct_count == 3:
                    action_message = f"Good work ({correct_count}/5 correct). Stay at level {current_level} to reinforce these concepts."
                else:
                    if current_level > 1:
                        current_level -= 1
                        level_changed = True
                        action_message = f"Some difficulty detected ({correct_count}/5 correct). The difficulty has been adjusted to level {current_level} to strengthen the fundamentals."
                    else:
                        action_message = f"You answered {correct_count}/5 correctly. Continue practicing the fundamentals at level 1."

        # Save updated progress
        self.storage.save_topic_progress(
            topic=topic,
            current_level=current_level,
            total_attempts=total_attempts,
            total_correct=total_correct,
            consecutive_unassisted=len(history_window),
            history_window=history_window
        )

        return {
            "level_changed": level_changed,
            "old_level": old_level,
            "new_level": current_level,
            "action_message": action_message,
            "unassisted_in_current_block": len(history_window),
            "block_size": self.BLOCK_SIZE
        }

    def get_progress_summary(self, topic: str) -> Dict[str, Any]:
        "Return a learning summary for the topic, or an insufficient-data message."
        progress = self.storage.get_topic_progress(topic)
        total = progress["total_attempts"]
        if total < 3:
            return {
                "has_enough_data": False,
                "message": "There are not enough exercises yet to assess your progress in this topic.",
                "current_level": progress["current_level"],
                "total_attempts": total,
                "total_correct": progress["total_correct"]
            }

        pct = (progress["total_correct"] / total) * 100
        return {
            "has_enough_data": True,
            "current_level": progress["current_level"],
            "total_attempts": total,
            "total_correct": progress["total_correct"],
            "percentage": round(pct, 1),
            "unassisted_progress": f"{progress['consecutive_unassisted']}/{self.BLOCK_SIZE} in the current block"
        }
