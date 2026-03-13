import numpy as np
from scipy.optimize import differential_evolution
import subprocess
import matplotlib.pyplot as plt
import time
import os
import re

#Python optimizer
#        ↓
#generate geometry
#        ↓
#blockMesh
#        ↓
#solver (simpleFoam)
#        ↓
#OpenFOAM functionObject writes result
#        ↓
#Python reads single number
#        ↓
#compute objective
#        ↓
#optimizer continues


# ============================================================
# CONFIGURATION
# ============================================================

# Choose: "mock" or "cfd"
EXEC_MODE = "mock"   # <-- SWITCH HERE

PLOT_SURFACES = True  # Set to True to create surface plots
RESULT_DIR = "optimization_results"
os.makedirs(RESULT_DIR, exist_ok=True)

history_params = []
history_obj = []
history_time = []
iteration = 0


# ============================================================
# ADVANCED MOCK BLOCKMESH MODE
# Runs corrugatedTube/createCorrugatedTube.py
# Saves blockMeshDict for first SAVE_N_BLOCKMESHES iterations
# ============================================================

SAVE_N_BLOCKMESHES = 5   # <-- CHANGE THIS NUMBER

def mock_run(A, P, M, iteration):
    """
    Runs the real geometry-generating script in corrugatedTube/
    but still returns a mock objective value.

    Steps:
      1. cd corrugatedTube
      2. run createCorrugatedTube.py A P M
      3. copy generated blockMeshDict to optimization_results/
    """
    tube_dir = "corrugatedTube"
    script = "createCorrugatedTube.py"
    script_path = os.path.join(tube_dir, script)

    # --- 1) Run the geometry generator ---
    cmd = ["python3", script_path, str(A), str(P), str(M)]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        raise RuntimeError(
            f"Geometry script failed.\n"
            f"CMD: {' '.join(cmd)}\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}"
        )

    # --- 2) Save generated blockMeshDict (only first N) ---
    source_dict = "blockMeshDict"

    if os.path.exists(source_dict) and iteration <= SAVE_N_BLOCKMESHES:
        dest_dict = os.path.join(
            RESULT_DIR, f"blockMeshDict_{iteration}"
        )
        subprocess.run(["cp", source_dict, dest_dict])

    # --- 3) Compute the mock objective value ---
    import math
    value = (A - 0.4)**2 + 0.1 * math.sin(P) + 0.05 * M

    # print nice status line
    #print(f"blockMesh successful, value = {value:.6f}")

    return value

# ============================================================
# CFD MODE: Your real pipeline
# ============================================================

def write_params(params):
    A, P, M = params
    with open("inputParameters.txt", "w") as f:
        f.write(f"A {A}\nP {P}\nM {M}\n")

    # Your geometry generator:
    subprocess.run(["python3", "yourBlockMeshScript.py"], check=True)


def run_openfoam():

    import subprocess

    try:
        # 1) Run geometry generator inside the system folder
        subprocess.run(
            ["python3", "createCorrugatedTube.py"],
            cwd="system",
            check=True
        )

        # 2) Run the OpenFOAM case
        subprocess.run(
            ["bash", "Allrunparallel"],
            check=True
        )

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"OpenFOAM pipeline failed: {e}")


def read_cfd_result():

    file = "postProcessing/areaAverage/0/surfaceFieldValue.dat"

    data = np.loadtxt(file, comments="#")

    if data.size == 0:
        raise RuntimeError("No data found in result file")

    value = data[-1, 1]

    return float(value)


# ============================================================
# OBJECTIVE FUNCTION
# ============================================================

def objective(params):
    global iteration
    iteration += 1
    start = time.time()

    A = float(params[0])
    P = float(params[1])
    M = int(round(params[2]))   # enforce integer

    params_int = np.array([A, P, M], float)

    # ----------------------------------------
    # MOCK OR CFD EXECUTION
    # ----------------------------------------
    if EXEC_MODE == "mock":
        value = mock_run(A, P, M, iteration)
        print(f"blockMesh successful, value = {value:.6f}")
    else:
        write_params(params_int)
        run_openfoam()
        value = read_cfd_result()

    # ----------------------------------------
    # Log
    # ----------------------------------------
    history_params.append(params_int)
    history_obj.append(value)
    history_time.append(time.time() - start)

    print(f"[{iteration:04d}] Params tested: {params_int} → Objective: {value:.6f}")

    return value


# ============================================================
# OPTIMIZATION SETUP
# ============================================================

bounds = [
    (0, 1),     # A
    (0, 20),    # P
    (1, 1),     # M (rounded)
]

result = differential_evolution(
    objective,
    bounds,
    maxiter=20,
    popsize=6,
    tol=0.01,
    workers=1 #-1 means use all available CPU cores, otherwise specify number of parallel workers
)

A_opt, P_opt, M_opt_raw = result.x
M_opt = int(round(M_opt_raw))


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n============================")
print(f"🎯 Optimal parameters (raw):          {result.x}")
print(f"🎯 Optimal parameters (rounded M):    [{A_opt:.6f}, {P_opt:.6f}, {M_opt}]")
print(f"🎯 Optimal objective:                 {result.fun}")
print(f"📈 Total evaluations:                 {iteration}")
print("============================")


# ============================================================
# SAVE RESULTS
# ============================================================

np.savetxt(f"{RESULT_DIR}/optimal_params_raw.txt", result.x)
np.savetxt(f"{RESULT_DIR}/optimal_params_integerM.txt",
           np.array([A_opt, P_opt, M_opt]))
np.savetxt(f"{RESULT_DIR}/optimal_objective.txt", [result.fun])
np.savetxt(f"{RESULT_DIR}/num_iterations.txt", [iteration])
np.savetxt(f"{RESULT_DIR}/history_params.txt", np.array(history_params))
np.savetxt(f"{RESULT_DIR}/history_objective.txt", np.array(history_obj))
np.savetxt(f"{RESULT_DIR}/history_time.txt", np.array(history_time))

# ============================================================
# THEORETICAL OPTIMUM FOR MOCK OBJECTIVE (REFERENCE)
# ============================================================

if EXEC_MODE == "mock":
    # True global minimum of:
    # f(A,P,M) = (A - 0.4)^2 + 0.1*sin(P) + 0.05*M

    # Analytic solution:
    A_true = 0.4
    M_true = 0      # smallest integer in allowed domain

    # All sine minima within P ∈ [0,20]
    P_minima = [
        1.5 * np.pi,               # 3π/2 ≈ 4.712389
        1.5 * np.pi + 2*np.pi,     # +2π ≈ 10.995574
        1.5 * np.pi + 4*np.pi      # +4π ≈ 17.278760
    ]

    # All have sin(P) = -1 → term = -0.1
    f_true = -0.1

    print("\n============================")
    print("📌 THEORETICAL OPTIMUM (MOCK FUNCTION)")
    print(f"  True minimum objective      : {f_true:.6f}")
    print(f"  True optimal A              : {A_true}")
    print(f"  True optimal M              : {M_true}")
    print("  True optimal P values       :")
    for p in P_minima:
        print(f"     P ≈ {p:.6f}")
    print("============================\n")
else:
    print("\n(Analytic minimum not shown — EXEC_MODE != 'mock')\n")

# ============================================================
# CONVERGENCE PLOT
# ============================================================

plt.figure()
plt.plot(history_obj, marker='o', ms=3, lw=1)
plt.xlabel("Evaluation #")
plt.ylabel("Objective value")
plt.title("Convergence history")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{RESULT_DIR}/convergence_plot.png", dpi=180)
plt.show()


# ============================================================
# SURFACE PLOTS (CFD-safe, uses only history)
# ============================================================

from mpl_toolkits.mplot3d import Axes3D  # needed for projection

if PLOT_SURFACES:
    params_arr = np.array(history_params)
    objs_arr = np.array(history_obj)

    A_vals = params_arr[:, 0]
    P_vals = params_arr[:, 1]
    M_vals = params_arr[:, 2]

    unique_M = np.unique(M_vals)

    for Mfix in unique_M:
        mask = (M_vals == Mfix)
        if np.sum(mask) < 3:
            continue

        A_plot = A_vals[mask]
        P_plot = P_vals[mask]
        O_plot = objs_arr[mask]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        sc = ax.scatter(A_plot, P_plot, O_plot, c=O_plot, cmap='viridis')

        ax.set_xlabel("A", labelpad=10)
        ax.set_ylabel("P", labelpad=10)
        ax.set_zlabel("Objective", labelpad=10)
        ax.set_title(f"Objective Surface (M = {int(Mfix)})")
        fig.colorbar(sc, shrink=0.6)

        plt.savefig(f"{RESULT_DIR}/surface_M{int(Mfix)}.png", dpi=180)
        plt.show()

    print("Surface plots created for M =", [int(m) for m in unique_M])
else:
    print("Surface plotting skipped.")