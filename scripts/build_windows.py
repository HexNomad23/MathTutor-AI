"Build a portable Windows distribution with PyInstaller.\nCreates dist/MathTutorAI/ with MathTutorAI.exe and its dependencies."

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

    print("Running PyInstaller:", " ".join(cmd))
    res = subprocess.run(cmd, cwd=project_root)
    if res.returncode == 0:
        print("\n[OK] Build completed successfully!")
        print(f"Portable distribution created at: {dist_dir / 'MathTutorAI'}")
        print(f"Executable: {dist_dir / 'MathTutorAI' / 'MathTutorAI.exe'}")
    else:
        print("\n[ERROR] PyInstaller build failed.")
        sys.exit(res.returncode)


if __name__ == "__main__":
    build()
