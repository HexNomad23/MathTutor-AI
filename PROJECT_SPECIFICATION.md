# MathTutor AI — Product Draft and Development Brief for Antigravity

Proposed version: 0.1 · Platform: Windows PC · Current interface language: English.

This is the English edition of the original product brief. Language requirements and file names have been updated for the English release. Requirements describe the intended product; they are not evidence that every item has been implemented. See [DEVELOPMENT_PROGRESS.md](DEVELOPMENT_PROGRESS.md) and the README for actual scope and validation.

## 1. Assignment and objective

Act as the lead developer of MathTutor AI. Build a working desktop application, rather than only screen designs, a website, or a generic chatbot.

Help students understand mathematics by solving exercises through justified transformations, reviewing their work, offering hints, and generating practice appropriate to their performance. The initial audience is secondary-school and early university students.

The full vision covers algebra, geometry, physics, and calculus. Version 0.1 should solve a small, clearly defined set of exercises across all four subjects. Do not claim universal coverage.

Prioritize mathematical correctness, understandable explanations, stable operation, and then visual polish. Continue from planning into implementation and testing within available permissions.

## 2. First student experience

The application should open without requiring registration, payment details, an internet connection, or AI credentials. Provide a local profile called “Student” whose name can be changed without requesting unnecessary personal information.

The main flow is: select a subject and exercise type; enter an expression or complete a form; check the interpretation; solve or request hints; study the steps; practice a similar exercise; review progress.

Include “Solve Step by Step,” “Give Me a Hint,” “Review My Work,” and “Practice Something Similar” where those actions are available. Disable unfinished features with an explanation rather than simulating functionality.

## 3. Required mathematical scope for version 0.1

| Subject | Initial content | Inputs and limits |
| --- | --- | --- |
| Algebra | Linear equations in one unknown with parentheses and rational coefficients; quadratic equations by factoring or the quadratic formula. | Typed expressions; real numbers by default; include no-solution and infinitely-many-solution cases. |
| Geometry | Rectangle and circle areas/perimeters, triangle areas, and the Pythagorean theorem. | Forms with measurements, units, and the unknown; do not infer measurements from images. |
| Physics | Uniform linear motion with d = v·t, Newton's second law with F = m·a, and necessary compatible-unit conversions. | Forms with known quantities and an unknown; explain the model without inventing missing data. |
| Calculus | Derivatives and indefinite integrals of single-variable polynomials. | Typed expressions; sum, constant, and power rules; include the integration constant. |

Equation systems, trigonometry, limits, differential equations, advanced physics, handwriting recognition, and general word-problem comprehension are not required at this stage. Document the scope and clearly reject unsupported exercises.

Geometric dimensions must be physically valid. In physics, distinguish quantities, units, and sign conventions; check denominators and insufficient data. An illustrative diagram is not evidence of a measurement.

## 4. Solve while teaching

Each solution should show the interpreted problem, input data, relevant domain assumptions, a step sequence, an exact result where appropriate, and a final check.

Each step contains the previous expression, operation, resulting expression, brief rule explanation, and necessary restrictions. Do not omit essential transformations or turn a final answer into a supposedly verified procedure without checking the steps.

Expected behavior for `2x + 3 = 11`:

1. Subtract 3 from both sides: `2x + 3 − 3 = 11 − 3`.
2. Simplify: `2x = 8`.
3. Divide both sides by 2: `x = 4`.
4. Substitute into the original equation: `2·4 + 3 = 11`.

Offer Brief and Detailed explanations with identical mathematics. Guided mode should reveal one hint at a time and allow students to attempt the next step before seeing the solution.

For supported topics, use programmed rules that produce both transformations and their explanations. Mathematical correctness must not depend on an unchecked free-text answer.

## 5. Review student errors

Start with line-by-line review of linear algebraic equations. For other subjects, initially verify final answers and units where appropriate. Do not advertise complete procedure review before it exists.

If a student writes `2x = 11 + 3` after `2x + 3 = 11`, identify that transition and explain: “To remove +3 from the left side, subtract 3 from both sides. The correct step is 2x = 11 − 3.” Allow a retry.

Identify the first unjustified transition, distinguish an incorrect transformation from one that could not be verified, and accept mathematically valid alternatives. A method is not incorrect merely because it differs from the suggested solution.

If only a final answer is supplied, report whether it matches without inventing the student's mistake. Use respectful feedback without ridicule or judgments about ability.

## 6. Adaptive practice and progress

Generate exercises from verified parameterized templates, not only fixed lists or unchecked generated text. Each template should record topic, difficulty, parameters, solution, rules, and a reproducible seed.

Begin with three levels per topic. For algebra, increase operation count, then introduce negative numbers and parentheses or fractions. Allow manual difficulty selection.

The initial heuristic evaluates blocks of five exercises on the same topic answered without hints: four or five correct raises the level, three keeps it unchanged, and zero to two lowers it within allowed bounds. Record assisted attempts separately and do not count them as independent solutions. Process each block once.

These rules are an initial product choice, not a validated measure of intelligence or academic mastery. Allow future configuration and testing.

Save correct answers, errors, hints used, attempts, and topic levels. With insufficient data, show “There are not enough exercises yet to assess your progress.” Do not invent learning percentages, rankings, or demonstration progress in a real profile.

## 7. Screens and design

Use a readable, modern English interface with a light theme, good contrast, keyboard navigation, and resizable windows. Dark mode is optional and should not delay the first release.

Sidebar navigation: Home, Solve, Practice, My Progress, History, and Settings.

Home should show subject shortcuts, recent activity, and a recommendation based only on available history. Solve should show input and interpretation above expandable steps and verification. Practice should show a question, answer field, hint, and feedback. History should support reopening and deleting activities with confirmation.

Provide a simple mathematical keyboard for powers, square roots, fractions, and parentheses. Interpret entries such as `2x`, `x^2`, and `(x+1)/2` through a restricted parser. Accept decimal commas in appropriate fields. For ambiguous notation, request clarification instead of silently changing it. Always show “Your exercise is interpreted as…” before solving.

Display formulas as readable mathematics and allow copying accessible text. Add polynomial graphs where useful, with visible axes and scales; do not present graphs as mathematical proofs.

Test a 1366×768 window and Windows scaling at 125% and 150%. Avoid clipped text, hidden buttons, and panels requiring maximization for essential actions.

## 8. Proposed technical architecture

Use Python with PySide6 for a desktop application. Separate UI, mathematical engines, tutoring, practice generation, and persistence. PySide6 provides Python bindings for Qt [T1].

Use SymPy for symbolic operations and checks within the implemented scope [T2]. Build an explicit educational rule engine: a symbolic solver does not replace implementing and verifying teaching steps.

Embed Matplotlib in Qt for graphs. Mathtext may render supported formulas without external LaTeX; verify symbol support [T3]. Use SQLite for local storage and pytest for tests.

Do not introduce servers, accounts, or remote services merely for convenience. Avoid Electron, Docker, remote databases, and unnecessary processes in this first version unless a concrete blocker justifies a change.

Suggested structure:

```text
MathTutor-AI/
  src/mathtutor/
    ui/
    math_engine/
    tutor/
    practice/
    storage/
  tests/
  docs/                 # Optional additional documentation
  scripts/
  pyproject.toml
  README.md
  DEVELOPMENT_PROGRESS.md
```

Define shared exercise/solution data: identifier, topic, original input, interpretation, domain, units, steps, result, verification status, and reason. Each step preserves its applied rule. Attempts should reference exercise versions for reproducibility.

Select compatible versions, consult official documentation, and pin tested dependencies. Use a project virtual environment rather than changing global installations.

## 9. Accuracy, safety, and AI integration

Separate verifiable computation from explanation. Check results against the original exercise, preserve domain restrictions, and distinguish exact answers from approximations. Agreement at a few numeric values does not prove a general identity.

Use clear states: Verified, Numerical check, Could not verify, and Out of scope. Explain what was checked. Do not present an unverified result as mathematically certified.

Never execute student input as code. Use a limited grammar that constructs allowed mathematical objects; reject attributes, imports, arbitrary calls, and commands. Do not use `eval` or `exec` on student text, or pass it to `sympify`/`parse_expr` without a safe design. SymPy documentation warns about evaluation of string inputs [T4].

Limit expression length, depth, exponent size, and complexity. Potentially expensive calculations should use a cancellable worker process with a timeout. Do not block the UI or mark expired calculations as solved.

The initial tutor must work through local rules. Label it Local Mode without implying a generative model is installed.

Plan a separate interface for a future optional generative AI provider. Only implement remote access with a real API and authorized credentials. Antigravity is the development tool; students must not depend on its session or credentials.

Do not invent keys, endpoints, or provider responses. Preserve local features without a connection and mark remote AI as pending. Future AI explanations or interpretations must pass mathematical verification before receiving a verification label.

Do not send exercises or history outside the device without notice and consent. Keep secrets out of code and logs. Version 0.1 must not include telemetry, advertising, or payments.

## 10. Persistence, performance, and distribution

Save profiles, attempts, history, and settings under a user-data location such as `LocalAppData/MathTutorAI`, never in an installation folder requiring elevated permissions. Use parameterized queries and identified schema migrations.

Restore data across restarts. Failures must not erase progress. Handle read/write errors and avoid logging unnecessary sensitive information.

Prioritize Windows 11 x64. Validate Windows 10 before claiming compatibility and document systems actually tested. Local mode must not require a dedicated GPU.

Deliver a portable folder with `MathTutorAI.exe` and its dependencies first. Use PyInstaller and build Windows executables on Windows; it is not a cross-compiler [T5]. A portable directory is not a single self-contained executable.

Provide source-launch and build scripts. If the environment cannot build or test on Windows, deliver the source/scripts and explicitly state that limitation. Do not claim tests that were not run.

## 11. Tests and acceptance criteria

Include automated tests in addition to visual checks. Minimum cases:

| Case | Expected result or behavior |
| --- | --- |
| `2x + 3 = 11` | `x = 4`, with steps and final substitution. |
| `3(x − 2) = 12` | `x = 6`, preserving parentheses. |
| `x² − 5x + 6 = 0` | `x = 2` and `x = 3`. |
| `x² + 1 = 0` over the reals | No real solutions; no silent domain change. |
| `2x + 3 = 2x + 3` | Infinitely many real solutions. |
| `2x + 3 = 2x + 5` | No solution. |
| Incorrect step `2x = 11 + 3` after `2x + 3 = 11` | Identify and explain the incorrect transition. |
| Alternative `4x + 6 = 22` after `2x + 3 = 11` | Accept the equivalent equation. |
| Hypotenuse with legs 3 cm and 4 cm | 5 cm. |
| Triangle with base 10 cm and height 6 cm | Area 30 cm². |
| Uniform motion: 150 m in 10 s | Speed 15 m/s. |
| `F = m·a`, m = 2 kg, a = 3 m/s² | 6 N. |
| Convert 72 km/h | 20 m/s. |
| Derivative of `3x² + 2x − 5` | `6x + 2`. |
| Indefinite integral of `2x + 3` | `x² + 3x + C`. |

Also test empty inputs, unmatched parentheses, division by zero, missing quantities, incompatible units, impossible geometry, unsupported expressions, code execution attempts, and resource-limit failures. None should freeze or terminate the application.

Check exercise templates with multiple seeds, difficulty thresholds, and single processing of each block. Test persistence with temporary databases without touching personal data.

Manually test the UI and portable Windows distribution: startup, solving, hints, review, practice, history, and restart. Record actual results and pending failures.

Acceptance requires opening the app, solving supported cases with explanations, reviewing linear errors, practicing with adjustable difficulty, and retaining history. Attractive screens alone do not satisfy the assignment.

## 12. Execution order and delivery

Inspect the selected folder first. Preserve existing files, stay within the project, and avoid destructive operations elsewhere. Do not publish code or purchase services without authorization.

Document the plan and tasks. Antigravity artifacts may help organize and review work [T6], but must not replace project files.

1. Build an end-to-end `2x + 3 = 11` flow with steps, verification, and persistence.
2. Complete algebra, hints, and linear procedure review with tests.
3. Implement the defined geometry, physics, and calculus forms and engines.
4. Add parameterized practice, topic adaptation, real progress, and history.
5. Review UI, safety, computation limits, persistence, and packaging; run acceptance tests.

After each milestone, update `DEVELOPMENT_PROGRESS.md` with implemented work, tests, failures, decisions, and the next task. On resuming, read it and continue from the last verified state.

Deliver organized source, pinned dependencies, scripts, tests, an English README, scope documentation, and a report distinguishing Implemented and tested, Implemented but untested, and Pending. Include a project ZIP and Windows distribution when they have actually been built; provide real file paths.

Defer photo/screenshot recognition with transcription confirmation, document reading, remote conversational AI, equation systems, trigonometry, limits, synchronization, and teacher features to a later version. Do not delay the working core by attempting everything at once.

Keep the application runnable between milestones. Do not declare completion while advertised features are only simulations.

## Technical references from the original brief

The original brief records these references as consulted on October 15, 2026. Their inclusion here preserves the source document; translating it does not represent a new documentation review.

- [T1: Qt for Python documentation](https://doc.qt.io/qtforpython-6/index.html)
- [T2: SymPy solving guidance](https://docs.sympy.org/latest/guides/solving/solving-guidance.html)
- [T3: Matplotlib Qt integration](https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html) and [Mathtext](https://matplotlib.org/stable/gallery/text_labels_and_annotations/mathtext_demo.html)
- [T4: SymPy parsing](https://docs.sympy.org/latest/modules/parsing.html) and [core/sympify](https://docs.sympy.org/latest/modules/core.html)
- [T5: PyInstaller documentation](https://www.pyinstaller.org/)
- [T6: Google Antigravity artifacts](https://antigravity.google/docs/artifacts/)
