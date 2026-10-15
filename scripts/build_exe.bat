@echo off
title Build MathTutor AI Portable
cd /d "%~dp0\.."
if not exist ".venv\Scripts\python.exe" (
    echo Error: The virtual environment was not found in .venv
    pause
    exit /b 1
)
echo Building MathTutor AI for Windows (portable)...
".venv\Scripts\python.exe" scripts/build_windows.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build completed successfully in dist\MathTutorAI\
) else (
    echo.
    echo Build failed.
)
pause
