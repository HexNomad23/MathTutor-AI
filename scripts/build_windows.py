"""
Script de compilación portable para Windows usando PyInstaller.
Genera la carpeta portable dist/MathTutorAI/ con MathTutorAI.exe y sus dependencias.
"""

import sys
import subprocess
from pathlib import Path


def build():
    project_root = Path(__file__).resolve().parent.parent
    entry_point = project_root / "src" / "mathtutor" / "main.py"
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "MathTutorAI",
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "--add-data", f"{project_root / 'src' / 'mathtutor'};mathtutor",
        str(entry_point)
    ]

    print("Ejecutando PyInstaller:", " ".join(cmd))
    res = subprocess.run(cmd, cwd=project_root)
    if res.returncode == 0:
        print("\n[OK] Compilacion exitosa!")
        print(f"Carpeta portable generada en: {dist_dir / 'MathTutorAI'}")
        print(f"Ejecutable: {dist_dir / 'MathTutorAI' / 'MathTutorAI.exe'}")
    else:
        print("\n[ERROR] Error durante la compilacion de PyInstaller.")
        sys.exit(res.returncode)


if __name__ == "__main__":
    build()
