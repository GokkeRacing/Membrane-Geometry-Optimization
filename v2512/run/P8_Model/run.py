import os
import subprocess
import sys
import shutil

VENV_DIR = ".venv"


def run(cmd, error_msg=None):
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        if error_msg:
            print(error_msg)
        raise


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
    run([sys.executable, "-m", "venv", VENV_DIR])

# ------------------------------------------------------------
# Determine venv python path
# ------------------------------------------------------------
if os.name == "nt":
    python_path = os.path.join(VENV_DIR, "Scripts", "python.exe")
else:
    python_path = os.path.join(VENV_DIR, "bin", "python")


# ------------------------------------------------------------
# Ensure pip exists in the venv (ROBUST VERSION)
# ------------------------------------------------------------
def ensure_pip():
    print("Ensuring pip is available...")

    # 1. Check if pip already works
    try:
        subprocess.check_call([python_path, "-m", "pip", "--version"])
        print("pip is already installed ✅")
        return
    except subprocess.CalledProcessError:
        print("pip not found ❌")

    # 2. Try ensurepip
    try:
        print("Trying ensurepip...")
        subprocess.check_call([python_path, "-m", "ensurepip", "--upgrade"])
    except subprocess.CalledProcessError:
        print("ensurepip not available ❌")

    # 3. Check again
    try:
        subprocess.check_call([python_path, "-m", "pip", "--version"])
        print("pip successfully installed ✅")
        return
    except subprocess.CalledProcessError:
        print("pip still missing...")

    # 4. Fallback: get-pip.py
    print("Falling back to manual pip installation...")

    get_pip_script = "get-pip.py"

    try:
        run([
            "curl",
            "-sS",
            "https://bootstrap.pypa.io/get-pip.py",
            "-o",
            get_pip_script
        ], "ERROR: curl is not installed. Run: sudo apt install curl")

        run([python_path, get_pip_script])
        os.remove(get_pip_script)

        print("pip installed via get-pip.py ✅")
    except Exception:
        print(
            "\nERROR: Could not install pip.\n\n"
            "Fix manually with:\n"
            "  sudo apt install python3-venv python3-pip\n"
        )
        sys.exit(1)


# ------------------------------------------------------------
# Ensure pip / recover broken venv
# ------------------------------------------------------------
try:
    ensure_pip()
except Exception:
    print("Virtual environment is broken. Recreating it...")

    shutil.rmtree(VENV_DIR)

    run([sys.executable, "-m", "venv", VENV_DIR])

    if os.name == "nt":
        python_path = os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        python_path = os.path.join(VENV_DIR, "bin", "python")

    ensure_pip()

# ------------------------------------------------------------
# Install/update requirements
# ------------------------------------------------------------
print("Installing requirements...")

run([python_path, "-m", "pip", "install", "--upgrade", "pip"])
run([python_path, "-m", "pip", "install", "-r", "requirements.txt"])

# ------------------------------------------------------------
# Run main script
# ------------------------------------------------------------
print("Running main script...")

subprocess.check_call([
    python_path,
    "Optimization_Algorithm.py"
])