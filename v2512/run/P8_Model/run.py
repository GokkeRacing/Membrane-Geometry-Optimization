import os
import subprocess
import sys

VENV_DIR = ".venv"

# ------------------------------------------------------------
# Create virtual environment if missing
# ------------------------------------------------------------

if not os.path.exists(VENV_DIR):
    print("Creating virtual environment...")

    subprocess.check_call([
        sys.executable,
        "-m",
        "venv",
        VENV_DIR
    ])

# ------------------------------------------------------------
# Determine venv python path
# ------------------------------------------------------------

if os.name == "nt":
    python_path = os.path.join(VENV_DIR, "Scripts", "python.exe")
else:
    python_path = os.path.join(VENV_DIR, "bin", "python")

# ------------------------------------------------------------
# Install/update requirements
# ------------------------------------------------------------

print("Installing requirements...")

subprocess.check_call([
    python_path,
    "-m",
    "pip",
    "install",
    "-r",
    "requirements.txt"
])

# ------------------------------------------------------------
# Run main script
# ------------------------------------------------------------

subprocess.check_call([
    python_path,
    "Optimization_Algorithm.py"
])