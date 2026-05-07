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


OPTIMIZATION_MODE = "single"
# Options:
#   "single"
#   "multi"

OBJECTIVE_MODE = "length_independent"
# Options:
#   "concentration"
#   "length_independent"

SEARCH_FIELD_MODE = "a_p_relation"
# Options:
#   "square_region"
#   "a_p_relation"


# Data from base case (straight fibre) for normalization/reference
L = 0.02   # axial length [m]
# Weighted average values 
#DC_DZ_REF = (0.987610075258 - 1) / L  # (C_out - C_in) / L, with C_in = 1.0 # area-weighted average base case
DC_DZ_REF = (0.986744661804 - 1) / L # velocity-weighted average base case
#DS_DZ_REF = 2 * 250e-6 * np.pi # (surface area per unit length for straight tube with diameter 250µm)
DS_DZ_REF = 3.128689353606000094e-5 / L # updated reference from actual base case surface area measurement

# Area average values


# ============================================================
# CONFIGURATION
# ============================================================

CASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Absolute path of this script
ALLRUN_PATH = os.path.join(CASE_DIR, "Allrun")
#ALLRUNPARALLEL_PATH = os.path.join(CASE_DIR, "Allrunparallel")
ALLMESH_PATH = os.path.join(CASE_DIR, "Allmesh")
ALLCLEAN_PATH = os.path.join(CASE_DIR, "Allclean")
system_dir = os.path.join(CASE_DIR, "system")

PLOT_SURFACES = True  # Set to True to create surface plots

# Results directory (absolute path)
RESULT_DIR = os.path.join(CASE_DIR, "optimization_results")
os.makedirs(RESULT_DIR, exist_ok=True)

# History storage for diagnostics and plotting
history_params = []
history_obj = []
history_time = []
history_iterations = []
history_returncodes = []
history_concentration = []
history_pressureavg = []
history_surface_area = []
iteration = 0

if SEARCH_FIELD_MODE == "square_region":
    # Parameter bounds (must match order in objective function)
    A_min, A_max = 0, 0.5
    P_min, P_max = 3, 6
    M_min, M_max = 1, 1

    A_bounds = (A_min, A_max)
    P_bounds = (P_min, P_max)
    P_plot_bounds = P_bounds
    M_bounds = (M_min, M_max)

    # setting up initial population search
    A_1 = A_min + 0.2 * (A_max - A_min)
    A_2 = A_min + 0.4 * (A_max - A_min)
    A_3 = A_min + 0.6 * (A_max - A_min)
    A_4 = A_min + 0.8 * (A_max - A_min)
    P_mid = 0.5 * (P_min + P_max)

    init = np.array([
        [A_1,  P_min,  M_min],
        [A_3,  P_min,  M_min],
        [A_max, P_min,  M_min],

        [A_min, P_mid, M_min],   # base case (A = 0)
        [A_2,  P_mid, M_min],
        [A_4,  P_mid, M_min],

        [A_1,  P_max,  M_min],
        [A_3,  P_max,  M_min],
        [A_max,  P_max,  M_min],
    ])
        
elif SEARCH_FIELD_MODE == "a_p_relation":
    # --- Independent optimization variables ---
    A_min, A_max = 0.0, 2.0          # physical A
    p_hat_min, p_hat_max = 1e-12, 1.0  # normalized P-scaler
    M_min, M_max = 1, 1

    A_bounds = (A_min, A_max)
    p_hat_bounds = (p_hat_min, p_hat_max)
    P_plot_bounds = (6 * A_min, 6.0 * A_max)
    M_bounds = (M_min, M_max)


    init = np.array([
        # Base-case
        [0 , 1.0, M_min], 

        # Interior points
        [A_min + 0.15*(A_max - A_min), 0.10, M_min],
        [A_min + 0.30*(A_max - A_min), 0.30, M_min],
        [A_min + 0.50*(A_max - A_min), 0.50, M_min],
        [A_min + 0.70*(A_max - A_min), 0.70, M_min],
        [A_min + 0.90*(A_max - A_min), 0.90, M_min],

        # Upper corner
        [A_max , 1.0, M_min],
    ])


else:
    raise ValueError(f"Unknown SEARCH_FIELD_MODE: {SEARCH_FIELD_MODE}")


def compute_objective(concentration_out, surface_area):
    """
    Compute objective value based on selected OBJECTIVE_MODE.
    """
    if OPTIMIZATION_MODE == "single":
        if OBJECTIVE_MODE == "concentration":
            return concentration_out

        elif OBJECTIVE_MODE == "length_independent":
            # axial gradients
            dC_dz = (concentration_out - 1.0) / L   # C_in = 1.0, C_out = concentration
            dS_dz = surface_area / L

            # normalized objective
            f = (DC_DZ_REF / dC_dz) * (dS_dz / DS_DZ_REF)
            return f
    elif OPTIMIZATION_MODE == "multi":
        dC_dz = -abs((concentration_out - 1.0) / L) # / abs(DC_DZ_REF)
        dS_dz = surface_area / L # / DS_DZ_REF
        return [dC_dz, dS_dz]

    else:
        raise ValueError(f"Unknown OBJECTIVE_MODE: {OBJECTIVE_MODE}")



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
    import subprocess, os, re

    # --- CLEAN CASE ---
    subprocess.run(["bash", ALLCLEAN_PATH], cwd=CASE_DIR)

    # =====================================================
    # 1) RUN MESHING
    # =====================================================
    proc_mesh = subprocess.run(
        ["bash", ALLMESH_PATH],
        cwd=CASE_DIR
    )

    # --- CHECK log.checkMesh ---
    checkmesh_log = os.path.join(CASE_DIR, "log.checkMesh")

    mesh_failed = False

    if os.path.isfile(checkmesh_log):
        try:
            with open(checkmesh_log, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    m = re.search(r"Failed\s+([0-9]+)\s+mesh checks", line)
                    if m and int(m.group(1)) > 0:
                        mesh_failed = True
                        break
        except:
            mesh_failed = True
    else:
        # No log = something went wrong
        mesh_failed = True

    if mesh_failed:
        # Mesh failure: do NOT run solver
        return_code = 10   # distinct code for mesh failure
        iterations = None
        return return_code, iterations

    # =====================================================
    # 2) RUN SOLVER (only if mesh OK)
    # =====================================================
    proc_solver = subprocess.run(
        ["bash", ALLRUN_PATH], #ALLRUN_PATH or ALLRUNPARALLEL_PATH
        cwd=CASE_DIR
    )
    return_code = proc_solver.returncode

    # =====================================================
    # 3) PARSE iteration count from log.simpleFoam
    # =====================================================
    log_path = os.path.join(CASE_DIR, "log.simpleFoam")
    iterations = None

    if os.path.isfile(log_path):
        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    # Matches: "Time = 5000"
                    m = re.match(r"^\s*Time\s*=\s*([0-9eE\.\+\-]+)", line)
                    if m:
                        iterations = float(m.group(1))
        except:
            iterations = None

    return return_code, iterations




def read_cfd_result():
    fpath = os.path.join(
        CASE_DIR,
        "postProcessing/concentration/0/surfaceFieldValue.dat"
    )
    print("🔍 Reading CFD result file:", fpath)

    if not os.path.isfile(fpath):
        raise RuntimeError(f"CFD result file missing: {fpath}")

    data = np.genfromtxt(fpath, comments="#", dtype=float)

    # handle case where file has only one row of data
    if data.ndim == 1:
        return float(data[1])

    return float(data[-1, 1])


def read_pressure_avg():
    fpath = os.path.join(
        CASE_DIR,
        "postProcessing/FO_pressureAvg/0/surfaceFieldValue.dat"
    )
    print("📄 Reading pressureAvg file:", fpath)

    if not os.path.isfile(fpath):
        raise RuntimeError(f"pressureAvg result file missing: {fpath}")

    data = np.genfromtxt(fpath, comments="#", dtype=float)

    if data.ndim == 1:
        return float(data[1])

    return float(data[-1, 1])

def read_surface_area():
    fpath = os.path.join(
        CASE_DIR,
        "postProcessing/FO_surfaceArea/0/surfaceFieldValue.dat"
    )
    print("🧮 Reading membrane surface area:", fpath)

    if not os.path.isfile(fpath):
        raise RuntimeError(f"Surface area file missing: {fpath}")

    with open(fpath, "r") as f:
        for line in f:
            if line.startswith("# Area"):
                return float(line.split(":")[1].strip())

    raise RuntimeError("Surface area not found in FO_surfaceArea output")


# ============================================================
# OBJECTIVE FUNCTION
# ============================================================
PENALTY = 5e2  # Potentially change to a value based on failure type

def objective(params):
    global iteration
    iteration += 1
    start = time.time()

    # Initize diagnostics
    iterations = None
    return_code = None
    concentration = None
    pressure_avg = None
    surface_area = None

    if SEARCH_FIELD_MODE == "square_region":
        # Raw values from DE
        A_raw = float(params[0])
        P_raw = float(params[1])
        M_raw = float(params[2])

        # Force 6-decimal accuracy
        A = float(f"{A_raw:.6f}")
        P = float(f"{P_raw:.6f}")
        M = int(round(M_raw))  # integer-weighted variable

        params_int = np.array([A, P, M], float)
    elif SEARCH_FIELD_MODE == "a_p_relation":
        A_raw     = float(params[0])
        p_hat_raw = float(params[1])
        M_raw     = float(params[2])

        A     = float(f"{A_raw:.6f}")
        p_hat = float(f"{p_hat_raw:.6f}")

        # dependent bound: P ∈ [0, 6A]
        P = 6*A + 6*(A_max - A)*p_hat

        #assert P >= 6.0 * A - 1e-12, "P violated triangular constraint" # debug check

        M = int(round(M_raw))

        params_int = np.array([A, P, M], float)
    
    try:    
        # -------------------------------------------------
        # Generate geometry + run CFD
        # -------------------------------------------------
        write_params(params_int)

        return_code, iterations = run_openfoam()

        # -------------------------------------------------
        # Handle mesh failure (solver never ran)
        # -------------------------------------------------
        if return_code == 10:
            # Mesh failed → no results possible
            if OPTIMIZATION_MODE == "single":
                value = PENALTY
            else:
                value = [PENALTY, PENALTY]
            concentration = None
            pressure_avg = None

        # -------------------------------------------------
        # Handle solver execution
        # -------------------------------------------------
        elif return_code != 0:
            # Solver attempted but failed/diverged
            #value = PENALTY
            #concentration = None
            #pressure_avg = None
            pass # test

        # -------------------------------------------------
        # Solver ran successfully → read results
        # -------------------------------------------------
        else:
            try:
                concentration = read_cfd_result()
            except Exception as e:
                print(f"⚠ Concentration read failed → {e}")
                concentration = None

            try:
                pressure_avg = read_pressure_avg()
            except Exception as e:
                print(f"⚠ PressureAvg read failed → {e}")
                pressure_avg = None

            try:
                surface_area = read_surface_area()
            except Exception as e:
                print(f"⚠ Surface area read failed → {e}")
                surface_area = None

            if concentration is None or pressure_avg is None or surface_area is None:
                if OPTIMIZATION_MODE == "single":
                    value = PENALTY
                else:
                    value = [PENALTY, PENALTY]
            else: 
                value = compute_objective(concentration, surface_area)

    
    except Exception as e:
        if OPTIMIZATION_MODE == "single":
            value = PENALTY
        else:
            value = [PENALTY, PENALTY]
        print(
            f"⚠️ CFD failed on iter {iteration} "
            f"(A={A:.4f}, P={P:.4f}, M={M}). "
            f"Penalty={PENALTY:.3e}. Details: {e}"
        )

    # ----------------------------------------
    # Log
    # ----------------------------------------

    # Normalize None → np.nan for history storage
    if concentration is None:
        concentration = np.nan
    if pressure_avg is None:
        pressure_avg = np.nan
    if iterations is None:
        iterations = np.nan
    if return_code is None:
        return_code = np.nan
    if surface_area is None:
        surface_area = np.nan


    history_params.append(params_int)
    history_obj.append(value)
    history_time.append(time.time() - start)
    # Store extra diagnostics
    history_iterations.append(iterations)
    history_returncodes.append(return_code)
    history_concentration.append(concentration)
    history_pressureavg.append(pressure_avg)
    history_surface_area.append(surface_area)

    if OPTIMIZATION_MODE == "single":
        print(f"[{iteration:04d}] Params tested: {params_int} → Objective: {value:.12e}")
    else:
        print(f"[{iteration:04d}] Params tested: {params_int} → Objectives: {value}")

    return value

import matplotlib.tri as mtri

def _plot_2d_tricontour(A_plot, P_plot, O_plot, Mfix, out_dir,
                        levels=30, cmap="viridis", title_prefix="Objective"):
    """
    Create a 2D triangulation-based filled contour plot from scattered (A,P)->Objective samples.
    Saves to objective_2d_tricontour_M{M}.svg in out_dir.
    """
    tri = mtri.Triangulation(A_plot, P_plot)

    fig, ax = plt.subplots(figsize=(6.5, 5.0))

    cntr = ax.tricontourf(tri, O_plot, levels=levels, cmap=cmap)
    ax.tricontour(tri, O_plot, levels=max(6, levels // 4),
                  colors="k", linewidths=0.5, alpha=0.5)

    ax.scatter(A_plot, P_plot, c="white", s=10,
               edgecolors="k", linewidths=0.3,
               alpha=0.9, label="Samples")

    ax.set_xlim(A_bounds)
    ax.set_ylim(P_plot_bounds)
    ax.set_xlabel("A")
    ax.set_ylabel("P")
    ax.set_title(f"{title_prefix} (M = {int(Mfix)})")

    # -------------------------------------------------
    # Plot triangular constraint: P = 6A
    # -------------------------------------------------
    if SEARCH_FIELD_MODE == "a_p_relation":
        A_line = np.linspace(A_bounds[0], A_bounds[1], 200)
        P_line = 6.0 * A_line

        ax.plot(
            A_line,
            P_line,
            color="red",
            linestyle="--",
            linewidth=2.0,
            label="P = 6A (constraint)"
        )

        # Shade infeasible region
        ax.fill_between(
            A_line,
            0.0,
            P_line,
            color="green",
            alpha=0.12,
            label="Infeasible region (P < 6A)"
        )

    ax.legend(loc="best", frameon=True, fontsize=8)

    cbar = fig.colorbar(cntr, ax=ax, shrink=0.9)
    cbar.set_label("Objective")

    fn = os.path.join(out_dir, f"objective_2d_tricontour_M{int(Mfix)}.svg")
    plt.tight_layout()
    plt.savefig(fn)
    plt.show()
    print(f"Saved 2D contour: {fn}")


# ============================================================
# OPTIMIZATION SETUP
# ============================================================
if SEARCH_FIELD_MODE == "square_region":
    bounds = [
        A_bounds,
        P_bounds,
        M_bounds,
    ]
elif SEARCH_FIELD_MODE == "a_p_relation": 
    bounds = [
        A_bounds,
        p_hat_bounds,
        M_bounds,
    ]


result = None

try:
    if OPTIMIZATION_MODE == "single":
        result = differential_evolution( #https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html
            objective, # the function to minimize
            bounds, # list of (min, max) pairs for each parameter
            maxiter=3, # number of generations (iterations)
            popsize=3, # number of candidates per generation = popsize * len(params)
            init=init, # initial population - custom set in the top
            tol=1e-8, # relative tolerance for convergence
            workers=1 #-1 means use all available CPU cores, otherwise specify number of parallel workers
        )
        # Single-objective outputs
        A_opt, P_opt, M_opt_raw = result.x
        M_opt = int(round(M_opt_raw))

    # ============================================================
    # MULTI-OBJECTIVE OPTIMIZATION (NSGA-II)
    # ============================================================

    elif OPTIMIZATION_MODE == "multi":

        # --- Imports required only for multi-objective mode ---
        from pymoo.core.problem import ElementwiseProblem
        from pymoo.algorithms.moo.nsga2 import NSGA2
        from pymoo.optimize import minimize
        from pymoo.termination import get_termination
        from pymoo.core.variable import Real, Integer
        #from pymoo.core.mixed import MixedVariableGA
        

        termination = get_termination("n_gen", 30) # generations
        #termination = get_termination("n_eval", 3) # total evaluations
        
        # --------------------------------------------------------
        # Define the CFD optimization problem
        # --------------------------------------------------------

        if SEARCH_FIELD_MODE == "square_region":
            xl=np.array([A_min, P_min, M_min]),
            xu=np.array([A_max, P_max, M_max]),
        elif SEARCH_FIELD_MODE == "a_p_relation":
            xl=np.array([A_min, p_hat_min, M_min]),
            xu=np.array([A_max, p_hat_max, M_max]),

        class CFDProblem(ElementwiseProblem):
            def __init__(self):
                super().__init__(
                n_var=3,
                n_obj=2,
                xl=xl,
                xu=xu,
            )

            
            def _evaluate(self, x, out, *args, **kwargs):
                """
                X: array of candidate solutions, shape (n_pop, n_var)
                out["F"]: objective array, shape (n_pop, n_obj)
                """
                if SEARCH_FIELD_MODE == "square_region":
                    A = float(f"{x[0]:.4f}")
                    P = float(f"{x[1]:.4f}")
                    M = int(round(x[2]))   # ✅ no rounding anymore
                elif SEARCH_FIELD_MODE == "a_p_relation":
                    A = float(f"{x[0]:.4f}")
                    p_hat = float(f"{x[1]:.4f}")
                    M = int(round(x[2]))   # ✅ no rounding anymore
                    P = 6*A + 6*(A_max - A)*p_hat

                dC_dz, dS_dz = objective(np.array([A, P, M]))

                out["F"] = [dC_dz, dS_dz]

        # --------------------------------------------------------
        # Configure and run NSGA-II
        # --------------------------------------------------------
        algorithm = NSGA2(
            pop_size=12,        # increase cautiously (CFD cost!)
            eliminate_duplicates=True # True / False
        )

        result = minimize(
            CFDProblem(),
            algorithm,
            #n_gen=1,           # generations
            termination = termination,
            verbose=True
        )
    else:
        raise ValueError("Unknown OPTIMIZATION_MODE")

except KeyboardInterrupt:
    print("\n🛑 Optimization interrupted by user (Ctrl+C).")
    print("✅ Saving available results before exiting...")


# ============================================================
# PRINT RESULTS
# ============================================================
if OPTIMIZATION_MODE == "single":
    print("\n============================")
    print(f"🎯 Optimal parameters (raw):          {result.x}")
    print(f"🎯 Optimal parameters (rounded M):    [{A_opt:.4f}, {P_opt:.4f}, {M_opt}]")
    print(f"🎯 Optimal objective:                 {result.fun}")
    print(f"📈 Total evaluations:                 {iteration}")
    print("============================")
elif OPTIMIZATION_MODE == "multi":
    print("\n============================")
    print("🎯 Pareto-optimal solutions (A, P, M):")
    for i in range(len(result.X)):
        A_i = result.X[i][0]
        M_i = int(round(result.X[i][2]))

        if SEARCH_FIELD_MODE == "square_region":
            P_i = result.X[i][1]
        elif SEARCH_FIELD_MODE == "a_p_relation":
            p_hat_i = result.X[i][1]
            P_i = 6.0 * A_i / p_hat_i

        print(f"  - [{A_i:.4f}, {P_i:.4f}, {M_i}] → Objectives: {result.F[i]}")
    print(f"📈 Total evaluations:                 {iteration}")
    print("============================")


# ============================================================
# SAVE RESULTS
# ============================================================
# Save optimal parameters and objective values
if OPTIMIZATION_MODE == "single":
    np.savetxt(f"{RESULT_DIR}/optimal_params_raw.txt", result.x)
    np.savetxt(f"{RESULT_DIR}/optimal_params_integerM.txt",
            np.array([A_opt, P_opt, M_opt]))
    np.savetxt(f"{RESULT_DIR}/optimal_objective.txt", [result.fun])
elif OPTIMIZATION_MODE == "multi":
    np.savetxt(f"{RESULT_DIR}/pareto_params.txt", result.X)
    np.savetxt(f"{RESULT_DIR}/pareto_objectives.txt", result.F)

    F_all = np.array(history_obj)

    nds = NonDominatedSorting()
    front = nds.do(F_all, only_non_dominated_front=True)

    F_pareto_full = F_all[front]
    X_pareto_full = np.array(history_params)[front]     

    np.savetxt(f"{RESULT_DIR}/pareto_full_params.txt", X_pareto_full)
    np.savetxt(f"{RESULT_DIR}/pareto_full_objectives.txt", F_pareto_full)

# shared history logs (both modes)
np.savetxt(f"{RESULT_DIR}/num_iterations.txt", [iteration])
np.savetxt(f"{RESULT_DIR}/history_params.txt", np.array(history_params))
np.savetxt(f"{RESULT_DIR}/history_objective.txt", np.array(history_obj))
np.savetxt(f"{RESULT_DIR}/history_time.txt", np.array(history_time))
np.savetxt(f"{RESULT_DIR}/history_iterations.txt", np.array(history_iterations))
np.savetxt(f"{RESULT_DIR}/history_returncodes.txt", np.array(history_returncodes))
np.savetxt(f"{RESULT_DIR}/history_concentration.txt", np.array(history_concentration))
np.savetxt(f"{RESULT_DIR}/history_pressureavg.txt", np.array(history_pressureavg))
np.savetxt(f"{RESULT_DIR}/history_surface_area.txt", np.array(history_surface_area))


# ============================================================
# CONVERGENCE PLOT
# ============================================================
if OPTIMIZATION_MODE == "single":
    plt.figure()
    plt.plot(history_obj, marker='o', ms=3, lw=1)
    plt.xlabel("Evaluation #")
    plt.ylabel("Objective value")
    plt.title("Convergence history")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{RESULT_DIR}/convergence_plot.svg")
    plt.show()
elif OPTIMIZATION_MODE == "multi":
    plt.figure()

    # All evaluations
    plt.scatter(F_all[:, 0], F_all[:, 1], s=10, alpha=0.2, label="All evaluations")

    # Full Pareto (true best)
    plt.scatter(
        F_pareto_full[:, 0],
        F_pareto_full[:, 1],
        s=50,
        label="Pareto (all evals)"
    )

    # Final population (NSGA-II output)
    plt.scatter(
        result.F[:, 0],
        result.F[:, 1],
        s=70,
        marker="x",
        label="Final NSGA-II population"
    )

    plt.xlabel("dC/dz")
    plt.ylabel("dS/dz")
    plt.title("Pareto Front Comparison")
    plt.legend()
    plt.grid(True)

    plt.savefig(f"{RESULT_DIR}/pareto_comparison.svg")
    plt.show()

# ============================================================
# SURFACE PLOTS (CFD-safe, uses only history)
# ============================================================

from mpl_toolkits.mplot3d import Axes3D 

if PLOT_SURFACES and OPTIMIZATION_MODE == "single":
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

        plt.savefig(f"{RESULT_DIR}/surface_M{int(Mfix)}.svg")
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