import os
import subprocess
import sys

VENV_DIR = ".venv"


def ensure_venv_available():
    try:
        import venv
    except ImportError:
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
        print(
            "ERROR: Python 'venv' module is not available.\n\n"
            "On Debian/Ubuntu, install it with:\n"
            f"  sudo apt install python{py_ver}-venv\n"
        )
        sys.exit(1)

# ------------------------------------------------------------
# Ensure venv module exists
# ------------------------------------------------------------
ensure_venv_available()

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