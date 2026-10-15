# Registro de Progreso — MathTutor AI v0.1

Fecha: 15 de octubre de 2026  
Plataforma: Windows 11 / 10 x64  
Tecnologías: Python 3.14, PySide6 6.12 (Qt), SymPy 1.14, Matplotlib 3.11, SQLite3, PyInstaller 6.22

---

## Estado de Cumplimiento de Hitos

| Hito | Descripción | Estado | Pruebas |
|---|---|---|---|
| **Hito 1** | App base funcional de extremo a extremo para $2x + 3 = 11$, pasos pedagógicos, comprobación y guardado. | **Completado y Probado** | `tests/test_algebra.py`, `tests/test_ui_flow.py` |
| **Hito 2** | Alcance de álgebra (lineales con paréntesis/fracciones, cuadráticas, sin/infinitas soluciones, pistas y revisión línea a línea de procedimientos). | **Completado y Probado** | `tests/test_algebra.py` (8 pruebas pasando) |
| **Hito 3** | Formularios y motores de Geometría (rectángulo, círculo, triángulo, Pitágoras), Física (MRU, Newton, conversiones) y Cálculo (derivadas e integrales polinómicas). | **Completado y Probado** | `tests/test_other_subjects.py` (9 pruebas pasando) |
| **Hito 4** | Práctica adaptativa parametrizada (3 niveles, bloques de 5 sin pistas, semillas reproducibles), historial real y estadísticas de progreso. | **Completado y Probado** | `tests/test_practice.py` (5 pruebas pasando) |
| **Hito 5** | Interfaz responsive (1366×768, escalas 125%/150%), teclado matemático, seguridad/parser seguro, pruebas integradas y empaquetado portable PyInstaller. | **Completado y Probado** | `tests/test_safe_parser.py` (6 pruebas), `tests/test_ui_flow.py` (3 pruebas) |

---

## Matriz de Casos de Aceptación Obligatorios (Tabla 11)

| Caso de Prueba | Resultado Obtenido | Estado |
|---|---|---|
| $2x + 3 = 11$ | $x = 4$, 4 pasos explicados y sustitución $2\cdot 4 + 3 = 11$. | Verificado |
| $3(x - 2) = 12$ | $x = 6$, aplicando propiedad distributiva para eliminar paréntesis. | Verificado |
| $x^2 - 5x + 6 = 0$ | $x = 2$ y $x = 3$, con discriminante $\Delta = 1$ y fórmula cuadrática. | Verificado |
| $x^2 + 1 = 0$ en $\mathbb{R}$ | Sin soluciones reales ($\Delta = -4 < 0$). Mantiene dominio real. | Verificado |
| $2x + 3 = 2x + 3$ | Infinitas soluciones reales (reducción a identidad $0 = 0$). | Verificado |
| $2x + 3 = 2x + 5$ | Sin solución (reducción a contradicción $0 = 2$). | Verificado |
| Paso erróneo: $2x = 11 + 3$ tras $2x + 3 = 11$ | Detecta y explica: "Para eliminar el término +3 debes restar 3 en ambos lados". | Verificado |
| Paso alternativo: $4x + 6 = 22$ tras $2x + 3 = 11$ | Aceptado como equivalente válido (multiplicado por 2 en ambos lados). | Verificado |
| Hipotenusa con catetos de 3 cm y 4 cm | $c = 5\text{ cm}$, con pasos de Pitágoras y comprobación. | Verificado |
| Triángulo base 10 cm y altura 6 cm | Área de $30\text{ cm}^2$, con comprobación $2A = b \cdot h$. | Verificado |
| MRU: 150 m en 10 s | Rapidez $v = 15\text{ m/s}$ ($v = d/t$). | Verificado |
| $F = m \cdot a$ ($m = 2\text{ kg}$, $a = 3\text{ m/s}^2$) | Fuerza neta $F = 6\text{ N}$. | Verificado |
| Conversión de $72\text{ km/h}$ | $20\text{ m/s}$ (con factores dimensionales $1000/3600$). | Verificado |
| Derivada de $3x^2 + 2x - 5$ | $6x + 2$, término a término por regla de potencias. | Verificado |
| Integral indefinida de $2x + 3$ | $x^2 + 3x + C$, con constante de integración y comprobación por derivación. | Verificado |

---

## Resumen de la Suite de Pruebas

- **Total de pruebas automatizadas**: 31 pruebas en pytest.
- **Resultado**: 31 pasadas, 0 fallidas (100% de éxito).
- **Cobertura**:
  - `tests/test_safe_parser.py`: 6 pruebas (inyecciones, límites de exponentes, sintaxis, comas decimales).
  - `tests/test_algebra.py`: 8 pruebas (casos lineales, cuadráticos, sin solución, infinitas soluciones, diagnóstico de errores y pasos equivalentes).
  - `tests/test_other_subjects.py`: 9 pruebas (geometría, física, cálculo, validaciones de datos imposibles o negativos).
  - `tests/test_practice.py`: 5 pruebas (semillas deterministas, adaptación de dificultad por bloques de 5 sin pistas, datos insuficientes).
  - `tests/test_ui_flow.py`: 3 pruebas (inicialización de ventana, navegación entre las 6 vistas, resolución de $2x + 3 = 11$ de extremo a extremo y guardado en SQLite).
