"""
Controlador pedagógico adaptativo de práctica para MathTutor AI.
Implementa la heurística de bloques de 5 ejercicios no asistidos (sin pistas):
- 4 o 5 aciertos: sube un nivel (máximo 3).
- 3 aciertos: mantiene el nivel.
- 0, 1 o 2 aciertos: baja un nivel (mínimo 1).
Los intentos asistidos (con pistas) se registran pero no computan para la ventana de ajuste.
"""

from typing import Dict, Any, List, Tuple
from ..storage.database import StorageManager
from ..core.models import StudentAttempt


class AdaptiveController:
    BLOCK_SIZE = 5

    def __init__(self, storage: StorageManager):
        self.storage = storage

    def process_attempt(self, attempt: StudentAttempt) -> Dict[str, Any]:
        """
        Registra el intento en SQLite y evalúa si se completó un bloque de 5
        ejercicios sin asistencia para ajustar el nivel de dificultad del tema.
        """
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

        # Solo ejercicios no asistidos (0 pistas usadas) cuentan para la adaptación
        if attempt.hints_used == 0:
            history_window.append(attempt.is_correct)

            # Verificar si se completó un bloque de 5
            if len(history_window) >= self.BLOCK_SIZE:
                block = history_window[:self.BLOCK_SIZE]
                history_window = history_window[self.BLOCK_SIZE:]  # Vaciar el bloque evaluado

                correct_count = sum(1 for x in block if x)

                if correct_count >= 4:
                    if current_level < 3:
                        current_level += 1
                        level_changed = True
                        action_message = f"¡Gran trabajo! Has acertado {correct_count}/5 ejercicios independientes. Has subido al nivel {current_level}."
                    else:
                        action_message = f"¡Excelente desempeño! {correct_count}/5 aciertos. Ya estás en el nivel máximo ({current_level})."
                elif correct_count == 3:
                    action_message = f"Buen desempeño ({correct_count}/5 aciertos). Mantienes el nivel {current_level} para afianzar conceptos."
                else:
                    if current_level > 1:
                        current_level -= 1
                        level_changed = True
                        action_message = f"Se detectaron dificultades ({correct_count}/5 aciertos). Ajustamos la dificultad al nivel {current_level} para reforzar la base."
                    else:
                        action_message = f"Se registraron {correct_count}/5 aciertos. Sigues en el nivel 1 practicando los fundamentos."

        # Guardar progreso actualizado
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
        """Retorna el resumen pedagógico del tema o mensaje si los datos son insuficientes."""
        progress = self.storage.get_topic_progress(topic)
        total = progress["total_attempts"]
        if total < 3:
            return {
                "has_enough_data": False,
                "message": "Aún no hay suficientes ejercicios para valorar tu progreso en este tema.",
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
            "unassisted_progress": f"{progress['consecutive_unassisted']}/{self.BLOCK_SIZE} del bloque actual"
        }
