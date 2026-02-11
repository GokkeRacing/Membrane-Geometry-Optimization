import numpy as np
from OpenFoamDataWriter import OpenFoamDataWriter
import os


class pyPipe(object):
    def __init__(self,*args):

        PI1 = 1.0 #pitch distance p/D (-)
        PI2 = 0.05 #corrugation height h/D (-)
        n_periods = 3 #number of repeating sections (-)
        mesh_density = 30 #charactersistic mesh density 
        D = 0.04 #diameter (m)
        rho = 1.0 #density (kg/m^3)
        mu = 2e-5 #dynamic viscosity (kg/(m*s))
        U = 5 #bulk velocity (m/s)

        self._r = D/2
        self._l = D*PI1
        self._h = D*PI2
        self._mesh_density = mesh_density
        self._n_cell = 3*mesh_density*2
        yPlus = 1
        Re = U * D * rho / mu
        Cf = 0.079 * Re ** (-0.25)
        tau_w = 0.5 * Cf * rho * U ** 2
        U_tau = (tau_w / rho) ** 0.5
        delta_y = yPlus * mu / (rho * U_tau)
        grading = ((D/2-D/2*0.6) * 2 / mesh_density - delta_y) / delta_y
        self._grading = grading
        self._n_periods = n_periods

    def _create_one_level_data(self, pos):
        reduc = 0.7
        return [
            (pos[0] + np.cos(0) * self._r, pos[1] + np.sin(0) * self._r, pos[2] + 0),
            (pos[0] + np.cos(1.0 / 2.0 * np.pi) * self._r, pos[1] + np.sin(1.0 / 2.0 * np.pi) * self._r,
             pos[2] + 0),
            (pos[0] + np.cos(np.pi) * self._r, pos[1] + np.sin(np.pi) * self._r, pos[2] + 0),
            (pos[0] + np.cos(3.0 / 2.0 * np.pi) * self._r, pos[1] + np.sin(3.0 / 2.0 * np.pi) * self._r,
             pos[2] + 0),

            (pos[0] + np.cos(0) * self._r * reduc, pos[1] + np.sin(0) * self._r * reduc, pos[2] + 0),
            (pos[0] + np.cos(1.0 / 2.0 * np.pi) * self._r * reduc,
             pos[1] + np.sin(1.0 / 2.0 * np.pi) * self._r * reduc, pos[2] + 0),
            (pos[0] + np.cos(np.pi) * self._r * reduc, pos[1] + np.sin(np.pi) * self._r * reduc, pos[2] + 0),
            (pos[0] + np.cos(3.0 / 2.0 * np.pi) * self._r * reduc,
             pos[1] + np.sin(3.0 / 2.0 * np.pi) * self._r * reduc, pos[2] + 0)

        ]

    def _create_points_data(self):
        points_array = []

        t_vec = np.linspace(0, self._n_periods, self._n_cell)

        for i in range(len(t_vec)):
            pos = [self._h * np.sin(2 * np.pi * t_vec[i]), self._h * np.cos(2 * np.pi * t_vec[i]),
                   self._l * t_vec[i]]
            points_array = points_array + self._create_one_level_data(pos)
        return points_array

    def _create_one_level_edge_data(self, pos, layer):
        reduc = 0.6
        return [
            "arc %i %i (%e %e %e) " % (
                (layer * 8) + 0, (layer * 8) + 1, pos[0] + np.cos((1.0 / 4.0) * np.pi) * self._r,
                pos[1] + np.sin((1.0 / 4.0) * np.pi) * self._r, pos[2] + 0),
            "arc %i %i (%e %e %e) " % (
                (layer * 8) + 1, (layer * 8) + 2, pos[0] + np.cos((3.0 / 4.0) * np.pi) * self._r,
                pos[1] + np.sin((3.0 / 4.0) * np.pi) * self._r, pos[2] + 0),
            "arc %i %i (%e %e %e) " % (
                (layer * 8) + 2, (layer * 8) + 3, pos[0] + np.cos((5.0 / 4.0) * np.pi) * self._r,
                pos[1] + np.sin((5.0 / 4.0) * np.pi) * self._r, pos[2] + 0),
            "arc %i %i (%e %e %e) " % (
                (layer * 8) + 3, (layer * 8) + 0, pos[0] + np.cos((7.0 / 4.0) * np.pi) * self._r,
                pos[1] + np.sin((7.0 / 4.0) * np.pi) * self._r, pos[2] + 0),

            "arc %i %i (%e %e %e) " % (
                (layer * 8) + 4, (layer * 8) + 5, pos[0] + np.cos((1.0 / 4.0) * np.pi) * self._r * reduc,
                pos[1] + np.sin((1.0 / 4.0) * np.pi) * self._r * reduc, pos[2] + 0),
            "arc %i %i (%e %e %e) " % (
                (layer * 8) + 5, (layer * 8) + 6, pos[0] + np.cos((3.0 / 4.0) * np.pi) * self._r * reduc,
                pos[1] + np.sin((3.0 / 4.0) * np.pi) * self._r * reduc, pos[2] + 0),
            "arc %i %i (%e %e %e) " % (
                (layer * 8) + 6, (layer * 8) + 7, pos[0] + np.cos((5.0 / 4.0) * np.pi) * self._r * reduc,
                pos[1] + np.sin((5.0 / 4.0) * np.pi) * self._r * reduc, pos[2] + 0),
            "arc %i %i (%e %e %e) " % (
                (layer * 8) + 7, (layer * 8) + 4, pos[0] + np.cos((7.0 / 4.0) * np.pi) * self._r * reduc,
                pos[1] + np.sin((7.0 / 4.0) * np.pi) * self._r * reduc, pos[2] + 0)
        ]

    def _create_edges_data(self):
        edges_array = []
        layer = 0

        t_vec = np.linspace(0, self._n_periods, self._n_cell)

        for i in range(len(t_vec)):
            pos = [self._h * np.sin(2 * np.pi * t_vec[i]), self._h * np.cos(2 * np.pi * t_vec[i]),
                   self._l * t_vec[i]]
            edges_array = edges_array + self._create_one_level_edge_data(pos, layer)
            layer = layer + 1
        return edges_array

    def _create_one_level_block_data(self, layer):
        d = self._mesh_density
        d2 = d
        z_level_1 = 1

        return [
            "hex (%i %i %i %i %i %i %i %i) pipe (%i %i %i) " % (
                layer * 8 + 0, layer * 8 + 1, layer * 8 + 5, layer * 8 + 4, layer * 8 + 8, layer * 8 + 9, layer * 8 + 13,
                layer * 8 + 12, d, d2, z_level_1) + " edgeGrading (%f %f %f %f %f %f %f %f %f %f %f %f)" % (
                1, 1, 1, 1, self._grading, self._grading, self._grading, self._grading, 1, 1, 1, 1),
            "hex (%i %i %i %i %i %i %i %i) pipe (%i %i %i) " % (
                layer * 8 + 1, layer * 8 + 2, layer * 8 + 6, layer * 8 + 5, layer * 8 + 9, layer * 8 + 10, layer * 8 + 14,
                layer * 8 + 13, d, d2, z_level_1) + " edgeGrading (%f %f %f %f %f %f %f %f %f %f %f %f)" % (
                1, 1, 1, 1, self._grading, self._grading, self._grading, self._grading, 1, 1, 1, 1),
            "hex (%i %i %i %i %i %i %i %i) pipe (%i %i %i) " % (
                layer * 8 + 2, layer * 8 + 3, layer * 8 + 7, layer * 8 + 6, layer * 8 + 10, layer * 8 + 11, layer * 8 + 15,
                layer * 8 + 14, d, d2, z_level_1) + " edgeGrading (%f %f %f %f %f %f %f %f %f %f %f %f)" % (
                1, 1, 1, 1, self._grading, self._grading, self._grading, self._grading, 1, 1, 1, 1),
            "hex (%i %i %i %i %i %i %i %i) pipe (%i %i %i) " % (
                layer * 8 + 3, layer * 8 + 0, layer * 8 + 4, layer * 8 + 7, layer * 8 + 11, layer * 8 + 8, layer * 8 + 12,
                layer * 8 + 15, d, d2, z_level_1) + " edgeGrading (%f %f %f %f %f %f %f %f %f %f %f %f)" % (
                1, 1, 1, 1, self._grading, self._grading, self._grading, self._grading, 1, 1, 1, 1),

            "hex (%i %i %i %i %i %i %i %i) pipe (%i %i %i) " % (
                layer * 8 + 4, layer * 8 + 5, layer * 8 + 6, layer * 8 + 7, layer * 8 + 12, layer * 8 + 13, layer * 8 + 14,
                layer * 8 + 15, d, d2, z_level_1) + " edgeGrading (%f %f %f %f %f %f %f %f %f %f %f %f)" % (
                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
        ]

    def _create_block_data(self):
        blocks_array = []
        layer = 0

        t_vec = np.linspace(0, self._n_periods, self._n_cell)

        for i in range(len(t_vec) - 1):
            blocks_array = blocks_array + self._create_one_level_block_data(layer)
            layer = layer + 1
        return blocks_array

    def _create_one_level_patches_data(self, layer):
        return [
            "    (%i %i %i %i)" % (layer * 8 + 0, layer * 8 + 1, layer * 8 + 9, layer * 8 + 8),
            "    (%i %i %i %i)" % (layer * 8 + 1, layer * 8 + 2, layer * 8 + 10, layer * 8 + 9),
            "    (%i %i %i %i)" % (layer * 8 + 2, layer * 8 + 3, layer * 8 + 11, layer * 8 + 10),
            "    (%i %i %i %i)" % (layer * 8 + 3, layer * 8 + 0, layer * 8 + 8, layer * 8 + 11),
        ]

    def _create_patches_data(self):
        patches_array = [
            "inlet",
            "{",
            "type patch;",
            "(",
            "    (0 1 5 4)",
            "    (1 2 6 5)",
            "    (2 3 7 6)",
            "    (3 0 4 7)",
            "    (4 5 6 7)",
            ");",
            "}",
            "outlet",
            "{",
            "type patch;",
            "(",
            "    (%i %i %i %i)" % (
                self._n_cell * 8 - 8 + 0, self._n_cell * 8 - 8 + 1, self._n_cell * 8 - 8 + 5, self._n_cell * 8 - 8 + 4),
            "    (%i %i %i %i)" % (
                self._n_cell * 8 - 8 + 1, self._n_cell * 8 - 8 + 2, self._n_cell * 8 - 8 + 6, self._n_cell * 8 - 8 + 5),
            "    (%i %i %i %i)" % (
                self._n_cell * 8 - 8 + 2, self._n_cell * 8 - 8 + 3, self._n_cell * 8 - 8 + 7, self._n_cell * 8 - 8 + 6),
            "    (%i %i %i %i)" % (
                self._n_cell * 8 - 8 + 3, self._n_cell * 8 - 8 + 0, self._n_cell * 8 - 8 + 4, self._n_cell * 8 - 8 + 7),
            "    (%i %i %i %i)" % (
                self._n_cell * 8 - 8 + 4, self._n_cell * 8 - 8 + 5, self._n_cell * 8 - 8 + 6, self._n_cell * 8 - 8 + 7),
            ");",
            "}",
            "walls",
            "{",
            "type patch;",
            "(",
        ]

        layer = 0

        t_vec = np.linspace(0, self._n_periods, self._n_cell)

        for i in range(len(t_vec) - 1):
            pos = [self._h * np.sin(2 * np.pi * t_vec[i]), self._h * np.cos(2 * np.pi * t_vec[i]),
                   self._l * t_vec[i]]
            patches_array = patches_array + self._create_one_level_patches_data(layer)
            layer = layer + 1
        patches_array = patches_array + [");", "}"]
        return patches_array

    def write_block_mesh_dict(self, filename="blockMeshDict"):
        points_data = self._create_points_data()
        entries = []
        entries.append('scale 1;\n')
        entries.append('vertices')
        entries.append('(')
        for index, one_point in enumerate(points_data):
            entries.append("    (%e %e %e) " % one_point + "// %i" % index)
        entries.append(");\n")

        entries.append("blocks")
        entries.append("(")
        for each_entry in self._create_block_data():
            entries.append(each_entry)
        entries.append(");\n")

        entries.append("edges")
        entries.append("(")
        for each_entry in self._create_edges_data():
            entries.append(each_entry)
        entries.append(");\n")

        entries.append("boundary")
        entries.append("(")
        for each_entry in self._create_patches_data():
            entries.append(each_entry)
        entries.append(");\n")

        entries.append("mergePatchPairs")
        entries.append("(")
        entries.append(");\n")

        dirName = os.getcwd()# + "/constant/polyMesh"
        writer = OpenFoamDataWriter(dirName, "", filename, entries)


if __name__ == '__main__':
    pipe = pyPipe()    
    pipe.write_block_mesh_dict()
