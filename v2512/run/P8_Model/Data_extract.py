#!/usr/bin/env python3
import os
import numpy as np


# ============================================================
# Find latest time directory
# ============================================================
def find_latest_time_dir(case_dir="."):
    dirs = []
    for d in os.listdir(case_dir):
        p = os.path.join(case_dir, d)
        if os.path.isdir(p):
            token = d.replace(".", "", 1)
            if token.isdigit():
                dirs.append((float(d), d))
    if not dirs:
        raise RuntimeError("No time directories found.")
    dirs.sort()
    return dirs[-1][1]


# ============================================================
# Read volScalarField internalField safely
# ============================================================
def read_internal_field(field_file):
    vals = []
    inside = False
    started = False

    with open(field_file, "r") as f:
        for line in f:
            t = line.strip()

            if not inside and t.startswith("internalField"):
                inside = True
                continue

            if inside and not started:
                if t.startswith("("):
                    started = True
                continue

            if inside and started:
                if t.startswith(")"):
                    break
                try:
                    vals.append(float(t))
                except ValueError:
                    pass

    return np.array(vals, dtype=float)


# ============================================================
# Read mesh (points, faces, owner, neighbour)
# ============================================================
def read_points(points_file):
    pts = []
    inside = False
    with open(points_file, "r") as f:
        for line in f:
            t = line.strip()
            if not inside:
                if t.startswith("("):
                    inside = True
                continue
            if t.startswith(")"):
                break
            if t.startswith("(") and t.endswith(")"):
                xyz = t[1:-1].split()
                pts.append([float(xyz[0]), float(xyz[1]), float(xyz[2])])
    return np.array(pts, dtype=float)


def read_faces(faces_file):
    faces = []
    inside = False
    with open(faces_file, "r") as f:
        for line in f:
            t = line.strip()
            if not inside:
                if t.startswith("("):
                    inside = True
                continue
            if t.startswith(")"):
                break
            if "(" in t and ")" in t:
                inside_str = t[t.index("(")+1 : t.rindex(")")]
                faces.append([int(x) for x in inside_str.split()])
    return faces


def read_label_list(path):
    vals = []
    inside = False
    with open(path, "r") as f:
        for line in f:
            t = line.strip()
            if not inside:
                if t.startswith("("):
                    inside = True
                continue
            if t.startswith(")"):
                break
            try:
                vals.append(int(t))
            except ValueError:
                pass
    return np.array(vals, dtype=int)


# ============================================================
# Compute cell centers
# ============================================================
def compute_cell_centres(points, faces, owner, neighbour):

    nFaces = len(faces)
    nInternal = len(neighbour)

    nCells = max(owner.max(), neighbour.max()) + 1
    cell_points = [set() for _ in range(nCells)]

    for fId in range(nFaces):
        pts = faces[fId]
        c0 = owner[fId]
        cell_points[c0].update(pts)

        if fId < nInternal:
            c1 = neighbour[fId]
            cell_points[c1].update(pts)

    centers = np.zeros((nCells, 3))
    for c in range(nCells):
        idx = list(cell_points[c])
        centers[c] = points[idx].mean(axis=0)

    return centers


# ============================================================
# Compute cell volumes (geometric)
# ============================================================
def compute_cell_volumes(points, faces, owner, neighbour, centers):

    nFaces = len(faces)
    nInternal = len(neighbour)
    nCells = centers.shape[0]

    cell_vol = np.zeros(nCells)

    for fId in range(nFaces):
        face_pts = faces[fId]
        pts = points[face_pts]

        # triangulate the polygon face using fan method
        p0 = pts[0]

        # face area vector (unused in tetra method but shown for clarity)
        # Compute tetra volumes relative to cell center

        c0 = owner[fId]
        c0_pt = centers[c0]

        # Owner contribution
        for i in range(1, len(pts)-1):
            pa = pts[i]
            pb = pts[i+1]
            v = np.dot((pa - c0_pt), np.cross((pb - c0_pt), (p0 - c0_pt))) / 6.0
            cell_vol[c0] += abs(v)

        # Neighbour contribution (internal only)
        if fId < nInternal:
            c1 = neighbour[fId]
            c1_pt = centers[c1]
            for i in range(1, len(pts)-1):
                pa = pts[i]
                pb = pts[i+1]
                v = np.dot((pa - c1_pt), np.cross((pb - c1_pt), (p0 - c1_pt))) / 6.0
                cell_vol[c1] += abs(v)

    return cell_vol


# ============================================================
# Volume-weighted averaging per z-plane
# ============================================================
def volume_weighted_average_by_z(z, values, volumes, decimals=12):
    z_round = np.round(z, decimals)
    z_unique = np.unique(z_round)
    z_avg = np.zeros_like(z_unique)
    for i, zv in enumerate(z_unique):
        mask = (z_round == zv)
        z_avg[i] = np.sum(values[mask] * volumes[mask]) / np.sum(volumes[mask])
    return z_unique, z_avg


# ============================================================
# MAIN
# ============================================================
def main():
    print("Finding latest time folder...")
    latest = find_latest_time_dir(".")
    print(f"Using time directory: {latest}")

    field_name = "C_S"

    # file paths
    field_file = f"./{latest}/{field_name}"
    points_file = "./constant/polyMesh/points"
    faces_file = "./constant/polyMesh/faces"
    owner_file = "./constant/polyMesh/owner"
    neigh_file = "./constant/polyMesh/neighbour"

    # read geometry
    print("Reading points...")
    points = read_points(points_file)

    print("Reading faces...")
    faces = read_faces(faces_file)

    print("Reading owner/neighbour...")
    owner = read_label_list(owner_file)
    neighbour = read_label_list(neigh_file)

    # read field
    print("Reading scalar field...")
    data = read_internal_field(field_file)
    print("Field values:", data.size)

    # compute centers
    print("Computing cell centers...")
    centers = compute_cell_centres(points, faces, owner, neighbour)

    # compute volumes (geometric)
    print("Computing cell volumes (geometrically)...")
    volumes = compute_cell_volumes(points, faces, owner, neighbour, centers)

    if volumes.size != data.size:
        raise RuntimeError("Mismatch: volumes and data sizes differ!")

    # z-direction averages
    print("Computing volume-weighted z-averages...")
    z = centers[:, 2]
    z_unique, z_avg = volume_weighted_average_by_z(z, data, volumes)

    # save output
    out = "z_plane_averages_volumeWeighted.csv"
    np.savetxt(out,
               np.column_stack((z_unique, z_avg)),
               delimiter=",",
               header="z,volumeWeightedAvg",
               comments="")

    print("✓ Done!")
    print("Saved:", out)
    print("Number of z-slices:", z_unique.size)


if __name__ == "__main__":
    main()