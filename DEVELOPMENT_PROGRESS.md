# Development Progress — MathTutor AI v0.1

Date: October 15, 2026. Target platform: Windows 11 / 10 x64.

## Original development record

This section translates the original milestone report. Its completed statuses describe that report's claims and should be read alongside the narrower validation notes below and the README's remaining improvements.

Original recorded technologies: Python 3.14, PySide6 6.12, SymPy 1.14, Matplotlib 3.11, SQLite3, and PyInstaller 6.22.

| Milestone | Recorded implementation | Original status and evidence |
| --- | --- | --- |
| 1 | End-to-end `2x + 3 = 11`, explained steps, verification, and persistence. | Completed and tested: algebra and UI-flow tests. |
| 2 | Linear/quadratic algebra, no/infinite solutions, hints, and line-by-line procedure review. | Completed and tested: 8 algebra tests. |
| 3 | Geometry, physics, and polynomial calculus forms and engines. | Completed and tested: 9 subject tests. |
| 4 | Seeded practice, three levels, five-attempt adaptive blocks, history, and progress. | Completed and tested: 5 practice tests. |
| 5 | Responsive interface, keyboard, restricted parser, integrated tests, and portable packaging. | Recorded as completed: 6 parser tests and 3 UI tests. Display scaling and clean-machine packaging need separate verification. |

### Recorded acceptance cases

| Case | Recorded result |
| --- | --- |
| `2x + 3 = 11` | `x = 4` with explanation and substitution. |
| `3(x - 2) = 12` | `x = 6`, applying distribution. |
| `x^2 - 5x + 6 = 0` | Roots 2 and 3; discriminant 1. |
| `x^2 + 1 = 0` over the reals | No real solutions; negative discriminant. |
| `2x + 3 = 2x + 3` | Infinitely many real solutions; identity 0 = 0. |
| `2x + 3 = 2x + 5` | No solution; contradiction 0 = 2. |
| Incorrect transition to `2x = 11 + 3` | Explain that 3 must be subtracted from both sides. |
| Alternative transition to `4x + 6 = 22` | Accept multiplication of both sides by 2. |
| Right triangle with legs 3 cm and 4 cm | Hypotenuse 5 cm. |
| Triangle with base 10 cm and height 6 cm | Area 30 cm²; check 2A = b·h. |
| Uniform motion: 150 m in 10 s | Speed 15 m/s. |
| Mass 2 kg and acceleration 3 m/s² | Net force 6 N. |
| 72 km/h | 20 m/s. |
| Derivative of `3x^2 + 2x - 5` | `6x + 2`. |
| Indefinite integral of `2x + 3` | `x^2 + 3x + C`; verify by differentiation. |

Original suite: 31 tests, all passing, split into parser (6), algebra (8), other subjects (9), practice (5), and UI flow (3). These are test counts, not a measured code-coverage percentage.

## Repository preparation

- Created a reproducible installation with runtime/development requirements and a Windows/Python 3.14 version snapshot.
- Declared NumPy explicitly because the graph widget imports it directly.
- Replaced machine-specific paths in the launcher and PyInstaller specification.
- Added `.gitignore`, `.gitattributes`, detailed documentation, screenshots, and requested credits.
- Re-ran the 31 original tests successfully; `pip check` reported no incompatible dependencies.
- Published the repository and changed its visibility to public at the owner's request.

## English update

- Translated navigation, forms, hints, feedback, solver explanations, errors, graph labels, comments, and docstrings.
- Translated the README, product specification, progress record, package description, and script messages.
- Renamed launch/build/capture entry points to `start_app.bat`, `scripts/build_exe.bat`, and `scripts/capture_screenshots.py`.
- Kept database subject/topic identifiers stable and added English display labels for existing records, including legacy verification statuses.
- Preserved historical explanations, student answers, and custom profile names instead of rewriting user data. Newly generated explanations and the initial profile are English.
- Updated test expectations to English. The 31 original tests passed after the translation.
- Regenerated and visually inspected the Home, Solve, and Practice screenshots in English.
- Added four legacy-status compatibility cases checking English labels, saved profile names, history, and topic progress across database reopening.
- Validation: **35 tests passed** on Windows with Python 3.14.7; `pip check` found no broken requirements. Screenshot inspection also prompted a graph layout adjustment to keep its title visible.

## Pending work and validation boundaries

The original product brief includes goals beyond the current implementation, such as cancellable computation workers, broader resource-limit testing, full accessibility review, and configuration of teaching heuristics. These remain improvement areas, not validated features.

Automated offscreen UI checks do not establish compatibility with every Windows version, 125%/150% scaling, or a clean-machine portable installation. No new executable is claimed until a build is explicitly performed. Existing history may still contain its originally recorded language.
