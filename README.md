# MathTutor AI

**A desktop mathematics and science tutor with step-by-step explanations, symbolic verification, and adaptive practice.** Package version: `0.1.0`.

MathTutor AI helps secondary-school and early university students understand how to solve problems. It uses Python, PySide6, SymPy, NumPy, Matplotlib, and SQLite. Once its dependencies are installed, it works locally without an account, API keys, or an external AI service. This version uses educational rules and symbolic computation; it does not include a language model.

## Screenshot

![MathTutor AI solving 2x + 3 = 11 with English explanations, verification, and a graph](screenshot_solver.png)

An actual screenshot of the English application. Additional views: [Home](screenshot_home.png) and [Practice](screenshot_practice.png).

## Features

| Area | Version 0.1 scope |
| --- | --- |
| Algebra | Linear and quadratic equations in one unknown, including no-solution and infinitely-many-solution cases; substitution checks. |
| Geometry | Pythagorean theorem, triangle areas, rectangle areas and perimeters, and circle areas and circumferences; dimension validation. |
| Physics | Uniform linear motion, Newton's second law, and implemented speed conversions between km/h and m/s. |
| Calculus | Derivatives and indefinite integrals of single-variable polynomials. |
| Tutoring | Brief or detailed step explanations, progressive hints, and review of linear-equation procedures. |
| Practice | Seed-based reproducible exercises, five topics, and three difficulty levels. |
| Progress | Solution history, attempts, correct answers, and topic levels stored in SQLite. |
| Interface | Home, Solve, Practice, My Progress, History, and Settings; mathematical keyboard and graphs. |

Adaptive practice evaluates blocks of five exercises answered without hints. Four or five correct answers raise the level, three keep it unchanged, and up to two lower it, within levels 1–3. Assisted attempts are recorded but do not count toward the adjustment block.

## Requirements

- Windows 10/11, 64-bit, as the target platform.
- Python 3.10 or newer, 64-bit. The publication environment uses Python 3.14.7.
- Internet access to download dependencies during initial installation.
- Git to clone the repository, or download and extract its ZIP instead.

Create a separate `.venv` on each computer. A copied virtual environment may still reference another user's Python installation.

## Install from source

In PowerShell:

```powershell
git clone https://github.com/HexNomad23/MathTutor-AI.git
cd MathTutor-AI
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m mathtutor.main
```

If you downloaded the ZIP, open PowerShell in the extracted folder containing `pyproject.toml` and run the last three commands. This repository is public; viewing or downloading its source does not require signing in.

After installation, you can also double-click `start_app.bat`. The launcher uses its own directory and supports paths containing spaces. You do not need to activate the virtual environment or change PowerShell's execution policy.

### Development and tests

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
```

The development requirements install the project in editable mode and add pytest and PyInstaller. Tests cover the parser, algebra, geometry, physics, calculus, reproducible exercise generation, adaptive levels, navigation, and solving with history persistence. UI tests use Qt's `offscreen` platform and isolated databases.

The original suite contains 31 tests. See [DEVELOPMENT_PROGRESS.md](DEVELOPMENT_PROGRESS.md) for the English update's validation and compatibility checks. Automated UI tests do not substitute for testing a portable executable on a clean Windows installation.

### Dependencies

[`pyproject.toml`](pyproject.toml) is the source of dependency declarations. The `requirements*.txt` entry points install the project without duplicating its direct dependency list.

| Dependency | Declared minimum | Purpose |
| --- | --- | --- |
| PySide6 | 6.5.0 | Qt desktop interface. |
| SymPy | 1.12 | Symbolic computation and verification. |
| Matplotlib | 3.8.0 | Embedded graphs. |
| NumPy | 1.23.2 | Numerical graph evaluation. |
| pytest | 7.0.0 | Tests; `dev` extra. |
| PyInstaller | 6.0.0 | Portable builds; `dev` extra. |
| setuptools | 61.0 | Package build backend. |

SQLite, `ast`, `json`, and the other standard-library utilities come with Python. Pip resolves transitive dependencies.

[`requirements-lock-windows-py314.txt`](requirements-lock-windows-py314.txt) records the exact installed versions from the Windows/Python 3.14.7 validation environment. It is an environment-specific snapshot without hashes, not a cross-platform lock file.

To reproduce that environment after creating `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-lock-windows-py314.txt
.\.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e ".[dev]"
```

## Quick walkthrough

1. Open **Solve → Algebra**, enter `2x + 3 = 11`, and select **Solve Step by Step**. The answer is `x = 4`, with explanations and a substitution check.
2. Select **Give Me a Hint** for guidance or **Review My Work** to review intermediate equations.
3. Switch to Geometry, Physics, or Calculus to use their subject-specific forms.
4. Choose a topic in **Practice**, answer exercises, and review **My Progress** and **History**.
5. Change your local profile name in **Settings**.

| Example | Expected result |
| --- | --- |
| `3(x - 2) = 12` | `x = 6` |
| `x^2 - 5x + 6 = 0` | `x = 2` and `x = 3` |
| `x^2 + 1 = 0` | No real solutions |
| Right triangle with legs 3 and 4 | Hypotenuse 5 |
| Uniform motion: 150 m in 10 s | 15 m/s |
| Convert 72 km/h to m/s | 20 m/s |
| Derivative of `3x^2 + 2x - 5` | `6x + 2` |
| Indefinite integral of `2x + 3` | `x^2 + 3x + C` |

## Data, storage, and backups

The code includes the exercise generator and SQLite schema creation. No dataset download or database server is required. On first launch, it creates the `Student` profile and database at:

```text
%LOCALAPPDATA%\MathTutorAI\mathtutor.db
```

If `LOCALAPPDATA` is unset, the fallback is `~/.mathtutor_ai/mathtutor.db`.

| Table | Contents |
| --- | --- |
| `schema_version` | Schema version and application timestamp. |
| `profiles` | Local profile name and preferences. |
| `history` | Inputs, solutions, steps, and verification details. |
| `attempts` | Answers, seeds, difficulty, hints, and correctness. |
| `topic_progress` | Topic levels, counters, and adaptive blocks. |

The schema and operations are in [`src/mathtutor/storage/database.py`](src/mathtutor/storage/database.py). To back up or transfer history, close the application and copy `mathtutor.db` to a backup location. To restore it, close the application and place the backup at the same path, preserving any existing database you still need.

The English update preserves existing profile names, saved answers, historical explanations, and progress. Existing history retains the language in which it was recorded; newly generated content is English. Stable internal subject/topic identifiers retain their original values for database compatibility, while their display labels are English. Legacy verification statuses are displayed in English without rewriting stored records.

SQLite is not encrypted by the application. `.gitignore` excludes local databases, credentials, virtual environments, caches, logs, machine-specific shortcuts, and generated `build/` and `dist/` folders. Source, tests, scripts, documentation, and screenshots are versioned; dependencies and distributions are recreated using this guide.

## Project structure

```text
MathTutor-AI/
├── src/mathtutor/
│   ├── core/                # Shared models and verification states
│   ├── math_engine/         # Restricted AST parser and mathematical engines
│   ├── practice/            # Exercise generation and adaptive difficulty
│   ├── storage/             # SQLite schema and persistence
│   ├── tutor/               # Student procedure review
│   ├── ui/
│   │   ├── views/           # Six application views
│   │   ├── widgets/         # Keyboard, step cards, and graphs
│   │   ├── labels.py        # English labels for stable storage identifiers
│   │   └── main_window.py
│   ├── __init__.py
│   └── main.py
├── tests/
├── scripts/
│   ├── build_windows.py
│   ├── build_exe.bat
│   └── capture_screenshots.py
├── .gitattributes
├── .gitignore
├── start_app.bat
├── MathTutorAI.spec
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── requirements-lock-windows-py314.txt
├── screenshot_home.png
├── screenshot_practice.png
├── screenshot_solver.png
├── PROJECT_SPECIFICATION.md
├── DEVELOPMENT_PROGRESS.md
└── README.md
```

## Build the Windows portable application

Install the development requirements, then run:

```powershell
.\.venv\Scripts\python.exe scripts\build_windows.py
```

Alternatively, double-click `scripts\build_exe.bat`. The output executable is `dist\MathTutorAI\MathTutorAI.exe`. Distribute **the entire `dist\MathTutorAI` directory**, including its accompanying libraries.

The portable `.spec` configuration provides another build entry point:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm MathTutorAI.spec
```

Build the English source again to obtain an English executable; an older downloaded executable does not update itself.

## Refresh screenshots

From the repository root, with dependencies installed:

```powershell
.\.venv\Scripts\python.exe scripts\capture_screenshots.py
```

The script opens the English interface with an in-memory demonstration database and overwrites the three PNG files. It does not use your personal exercise history.

## Troubleshooting

- **Python not found:** install 64-bit Python and check `python --version` in a new terminal.
- **Virtual environment references another user:** create a new `.venv` on this computer instead of copying one.
- **Missing `mathtutor` or a library:** install from the repository root using the `.venv` Python shown above.
- **Copied executable does not start:** include its complete distribution folder and libraries.
- **Expression rejected:** check the supported scope. This version is not a universal problem solver or free-text parser.

## Limitations and improvement areas

These are proposed improvements, not implemented features:

| Priority | Area | Proposed improvement |
| --- | --- | --- |
| High | Parser and performance | Broaden nested-expression and computation-cost tests beyond current length, depth, and exponent limits. |
| High | Automated verification | Add CI, coverage measurement, and a Python/Windows version matrix. |
| High | Persistence | Expand migration and restore tests; add import/export through the interface. |
| Medium | Mathematics | Add equation systems, inequalities, trigonometry, and nonpolynomial calculus with explicit verification. |
| Medium | Teaching | Improve error diagnosis and exercise variety; evaluate adaptation with students. |
| Medium | Accessibility | Review keyboard access, screen readers, contrast, display scaling, and clipped content. |
| Medium | Distribution | Automate builds/releases, test on clean Windows systems, and define executable signing. |
| Medium | Maintenance | Add formatting, static analysis, and stronger error handling. |
| Pending | Licensing | Choose an explicit code license and document dependency redistribution conditions. |

The parser uses an AST operation allowlist; this is not a complete security audit. Tests cover specific cases rather than guaranteeing correctness for every expression. The original milestone report in [DEVELOPMENT_PROGRESS.md](DEVELOPMENT_PROGRESS.md) is distinguished from later validation.

## Contributing

Set up the development environment, describe problems with reproducible inputs, and run tests before proposing changes. Mathematical engine extensions should include expected results and verification. Keep personal data, credentials, and generated files out of commits. See [PROJECT_SPECIFICATION.md](PROJECT_SPECIFICATION.md) for product requirements.

## Credits

- **Antigravity, with Flash 3.8 as the agent**, for helping develop MathTutor AI.
- **GPT 6 Astra**, for helping develop MathTutor AI.
- The Python, Qt/PySide6, SymPy, NumPy, Matplotlib, pytest, and PyInstaller communities for the tools used.

Assistant names are credited as requested by the project owner. The project's own code does not yet have an explicit license; dependencies retain their respective licenses.
