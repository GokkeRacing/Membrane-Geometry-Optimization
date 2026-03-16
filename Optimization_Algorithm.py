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
EXEC_MODE = "cfd"   # <-- SWITCH HERE

CASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Absolute path of this script
ALLRUN_PATH = os.path.join(CASE_DIR, "Allrun")
ALLCLEAN_PATH = os.path.join(CASE_DIR, "Allclean")
system_dir = os.path.join(CASE_DIR, "system")

PLOT_SURFACES = True  # Set to True to create surface plots

# Results directory (absolute path)
RESULT_DIR = os.path.join(CASE_DIR, "optimization_results")
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
    import subprocess
    
    A, P, M = params
    M = int(M)  # ensure integer
    
    with open(os.path.join(CASE_DIR, "inputParameters.txt"), "w") as f:
        f.write(f"A {A:.4f}\nP {P:.4f}\nM {M}\n")



    # Run geometry generator → produces blockMeshDict
    subprocess.run(
        ["python3", "createCorrugatedTube.py", f"{A:.4f}", f"{P:.4f}", str(M)],
        cwd=system_dir,
        check=True
    )


def run_openfoam():

    import subprocess, os

    # Clean previous case data
    proc1 = subprocess.run(
            ["bash", ALLCLEAN_PATH],
            cwd=CASE_DIR
        )

    # Run the OpenFOAM case
    proc2 = subprocess.run(
        ["bash", ALLRUN_PATH],
        cwd=CASE_DIR
    )
    #except subprocess.CalledProcessError as e:
        #raise RuntimeError(f"OpenFOAM pipeline failed: {e}")

    return proc2.returncode


def read_cfd_result():
    fpath = os.path.join(
        CASE_DIR, 
        "postProcessing/concentration/0/surfaceFieldValue.dat"
    )
    print("🔍 Reading CFD result file:", fpath)

    if not os.path.isfile(fpath):
        raise RuntimeError(f"CFD result file missing: {fpath}")

    data = np.loadtxt(fpath, comments="#")
    return float(data[-1,1])


# ============================================================
# OBJECTIVE FUNCTION
# ============================================================
PENALTY = 1e9  # big penalty so DE avoids bad area

def objective(params):
    global iteration
    iteration += 1
    start = time.time()

    # Raw values from DE
    A_raw = float(params[0])
    P_raw = float(params[1])
    M_raw = float(params[2])

    # Force 4-decimal accuracy
    A = float(f"{A_raw:.4f}")
    P = float(f"{P_raw:.4f}")
    M = int(round(M_raw))  # integer-weighted variable

    params_int = np.array([A, P, M], float)

    
    try:
        # -------------------------------
        # MOCK OR CFD EXECUTION
        # -------------------------------
        if EXEC_MODE == "mock":
            value = mock_run(A, P, M, iteration)
            print(f"[mock] value = {value:.12f}")
        else:
            # Generate geometry + run CFD
            write_params(params_int)  # must call your generator with A,P,M
            ret = run_openfoam() # Test
            
            if ret != 0:
                print(f"⚠ Warning: Allrun returned code {ret}, attempting to read results anyway...")

            try:
                value = read_cfd_result()
            except Exception as e:
                print(f"⚠ Read failed → assigning penalty: {e}")
                value = PENALTY


            #run_openfoam()            # may raise on blockMesh/checkMesh/solver failure
            #value = read_cfd_result() # may raise if file missing or shape unexpected

    except Exception as e:
        # Assign penalty and continue optimization
        value = PENALTY
        print(
            f"⚠️  CFD failed on iter {iteration} "
            f"(A={A:.4f}, P={P:.4f}, M={M}). "
            f"Penalty={PENALTY:.3e}. Details: {e}"
        )


    # ----------------------------------------
    # Log
    # ----------------------------------------
    history_params.append(params_int)
    history_obj.append(value)
    history_time.append(time.time() - start)

    print(f"[{iteration:04d}] Params tested: {params_int} → Objective: {value:.12f}")

    return value

import matplotlib.tri as mtri

def _plot_2d_tricontour(A_plot, P_plot, O_plot, Mfix, out_dir,
                        levels=30, cmap="viridis", title_prefix="Objective"):
    """
    Create a 2D triangulation-based filled contour plot from scattered (A,P)->Objective samples.
    Saves to objective_2d_tricontour_M{M}.png in out_dir.
    """
    # Triangulate scattered points
    tri = mtri.Triangulation(A_plot, P_plot)

    fig, ax = plt.subplots(figsize=(6.5, 5.0))
    # Filled contours of objective
    cntr = ax.tricontourf(tri, O_plot, levels=levels, cmap=cmap)
    # Optional black line contours for readability
    ax.tricontour(tri, O_plot, levels=max(6, levels // 4), colors="k", linewidths=0.5, alpha=0.5)

    # Show the actual samples (white dots with thin black edge)
    ax.scatter(A_plot, P_plot, c="white", s=10, edgecolors="k", linewidths=0.3, alpha=0.9, label="samples")
    ax.legend(loc="best", frameon=True, fontsize=8)

    ax.set_xlabel("A")
    ax.set_ylabel("P")
    ax.set_title(f"{title_prefix} (M = {int(Mfix)})")

    cbar = fig.colorbar(cntr, ax=ax, shrink=0.9)
    cbar.set_label("Objective")

    fn = os.path.join(out_dir, f"objective_2d_tricontour_M{int(Mfix)}.png")
    plt.tight_layout()
    plt.savefig(fn, dpi=180)
    plt.show()
    print(f"Saved 2D contour: {fn}")


# ============================================================
# OPTIMIZATION SETUP
# ============================================================

bounds = [
    (0, 1),     # A
    (0, 3),    # P
    (1, 1),     # M (rounded)
]

result = differential_evolution(
    objective,
    bounds,
    maxiter=3, # number of generations (iterations)
    popsize=3, # number of candidates per generation = popsize * len(params)
    tol=1e-8, # relative tolerance for convergence
    workers=1 #-1 means use all available CPU cores, otherwise specify number of parallel workers
)

A_opt, P_opt, M_opt_raw = result.x
M_opt = int(round(M_opt_raw))


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n============================")
print(f"🎯 Optimal parameters (raw):          {result.x}")
print(f"🎯 Optimal parameters (rounded M):    [{A_opt:.4f}, {P_opt:.4f}, {M_opt}]")
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

    # ===== Extra 2D contour plot (keeps your 3D scatter untouched) =====
    # If you have duplicate (A,P), average objectives to prevent artefacts
    AP = np.round(np.column_stack([A_plot, P_plot]), 6)
    uniq, idx, inv = np.unique(AP, axis=0, return_index=True, return_inverse=True)

    O_agg = np.zeros(len(uniq), dtype=float)
    cnt = np.zeros(len(uniq), dtype=int)
    for i, k in enumerate(inv):
        O_agg[k] += O_plot[i]
        cnt[k] += 1
    O_agg /= np.maximum(cnt, 1)

    # Make the 2D triangulated contour (no SciPy required)
    _plot_2d_tricontour(
        A_plot=uniq[:, 0],
        P_plot=uniq[:, 1],
        O_plot=O_agg,
        Mfix=Mfix,
        out_dir=RESULT_DIR,
        levels=30,
        cmap="viridis",
        title_prefix="Objective"
    )
else:
    print("Surface plotting skipped.")