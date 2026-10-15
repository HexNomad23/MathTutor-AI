@echo off
setlocal
cd /d "%~dp0"
echo ========================================================
echo         Iniciando MathTutor AI (Modo Desarrollo)
echo ========================================================
echo.
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No se encontro el entorno virtual en .venv
    pause
    exit /b 1
)
start "" ".venv\Scripts\python.exe" -m mathtutor.main
exit /b 0
