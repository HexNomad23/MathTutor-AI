@echo off
title Compilar MathTutor AI Portable
cd /d "%~dp0\.."
if not exist ".venv\Scripts\python.exe" (
    echo Error: No se encontro el entorno virtual en .venv
    pause
    exit /b 1
)
echo Compilando MathTutor AI para Windows (portable)...
".venv\Scripts\python.exe" scripts/build_windows.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Compilacion finalizada correctamente en dist\MathTutorAI\
) else (
    echo.
    echo Error durante la compilacion.
)
pause
