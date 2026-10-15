@echo off
setlocal
cd /d "%~dp0"
echo ========================================================
echo         Starting MathTutor AI (Development Mode)
echo ========================================================
echo.
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] The virtual environment was not found in .venv
    pause
    exit /b 1
)
start "" ".venv\Scripts\python.exe" -m mathtutor.main
exit /b 0
