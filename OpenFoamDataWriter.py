# -*- coding: utf-8 -*-

import os
import os.path

class OpenFoamDataWriter(object):
    '''
    Create an OpenFOAM file with the information given in the data array.
    '''
    def __init__(self, project_path, location, the_object, openfoam_data, the_class="dictionary"):
        '''
        Create an OpenFOAM file with the information given in the data array.

        Keyword arguments:
        project_path -- path to the new OpenFOAM project
        location -- entry for FoamFile dict and directory in the project_path
        the_object -- entry for FoamFile dict
        openfoam_data -- array with lines to append to the file
        the_class -- usually a dictionary for OpenFOAM, but for U p.e. "volVectorField", for p "volScalarField"
        '''
        self._project_path = project_path
        self._location = location
        self._the_object = the_object
        self._the_class = the_class
        self._openfoam_data = openfoam_data

        self._foamfile_lines = []

        self._create_header()
        self._create_foamfile_part()
        self._create_data_part()
        self._write()

    def _create_header(self):
        """Create the header for the OpenFOAM file and append to the foamfile_lines array."""
        self._foamfile_lines.append(r"/*--------------------------------*- C++ -*----------------------------------*\\")
        self._foamfile_lines.append(r"| =========                 |                                                 |")
        self._foamfile_lines.append(r"| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |")
        self._foamfile_lines.append(r"|  \\    /   O peration     | Version:  v2512                                 |")
        self._foamfile_lines.append(r"|   \\  /    A nd           | Website:  www.openfoam.com                      |")
        self._foamfile_lines.append(r"|    \\/     M anipulation  |                                                 |")
        self._foamfile_lines.append(r"\*---------------------------------------------------------------------------*/")

    def _create_foamfile_part(self):
        '''Write the FoamFile part of the file.'''
        self._foamfile_lines.append("FoamFile")
        self._foamfile_lines.append("{")
        self._foamfile_lines.append("    version     2.0;")
        self._foamfile_lines.append("    format      ascii;")
        self._foamfile_lines.append("    class       " + self._the_class + ";")
        self._foamfile_lines.append("    object      " + self._the_object + ";")
        self._foamfile_lines.append("}")
        self._foamfile_lines.append("// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //")
        self._foamfile_lines.append("")

    def _create_data_part(self):
        '''Append the data part to the OpenFOAM file.'''
        self._foamfile_lines = self._foamfile_lines + self._openfoam_data

    def _write(self):
        '''Write the OpenFOAM file.'''
        path_name = os.path.join(self._project_path, self._location)
        if not os.path.exists(path_name):
            os.makedirs(path_name)
        fobj = open(os.path.join(path_name, self._the_object), "w")
        for line in self._foamfile_lines:
            fobj.write(line + "\n")
        fobj.close()
