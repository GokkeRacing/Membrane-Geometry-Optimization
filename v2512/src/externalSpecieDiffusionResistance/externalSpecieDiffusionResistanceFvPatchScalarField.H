/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
    Copyright (C) 2026 AUTHOR,AFFILIATION
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

Class
    Foam::externalSpecieDiffusionResistanceFvPatchScalarField

Group
    grpGenericBoundaryConditions

Description
    This boundary condition provides a externalSpecieDiffusionResistance condition

Usage
    Example of the boundary condition specification:
    \verbatim
    <patchName>
    {
        type       externalSpecieDiffusionResistance;
        H_cc       3.25;
        D_CO2_l    2e-10;
        C_CO2_g    1.6e-5;
        K_ext      1.3e-3;
    }
    \endverbatim

SourceFiles
    externalSpecieDiffusionResistanceFvPatchScalarField.C

\*---------------------------------------------------------------------------*/

#ifndef externalSpecieDiffusionResistanceFvPatchScalarField_H
#define externalSpecieDiffusionResistanceFvPatchScalarField_H

#include "mixedFvPatchFields.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

/*---------------------------------------------------------------------------*\
     Class externalSpecieDiffusionResistanceFvPatchScalarField Declaration
\*---------------------------------------------------------------------------*/

class externalSpecieDiffusionResistanceFvPatchScalarField
:
    public mixedFvPatchScalarField
{
    // Private Data
    
        //- Henry's constant [dimensionless]
        scalar H_cc;
        
        //- CO2 diffusion coefficient in liquid [m^2/s]
        scalar D_CO2;
        
        //- CO2 concentration in gas phase [mol/m^3]
        scalar C_CO2_g;
        
        //- External mass transfer coefficient [m/s]
        scalar K_ext;


public:

    //- Runtime type information
    TypeName("externalSpecieDiffusionResistance");


    // Constructors

        //- Construct from patch and internal field
        externalSpecieDiffusionResistanceFvPatchScalarField
        (
            const fvPatch&,
            const DimensionedField<scalar, volMesh>&
        );

        //- Construct from patch, internal field and dictionary
        externalSpecieDiffusionResistanceFvPatchScalarField
        (
            const fvPatch&,
            const DimensionedField<scalar, volMesh>&,
            const dictionary&
        );

        //- Construct by mapping onto a new patch
        externalSpecieDiffusionResistanceFvPatchScalarField
        (
            const externalSpecieDiffusionResistanceFvPatchScalarField&,
            const fvPatch&,
            const DimensionedField<scalar, volMesh>&,
            const fvPatchFieldMapper&
        );

        //- Construct as copy
        externalSpecieDiffusionResistanceFvPatchScalarField
        (
            const externalSpecieDiffusionResistanceFvPatchScalarField&
        );

        //- Construct and return a clone
        virtual tmp<fvPatchScalarField> clone() const
        {
            return tmp<fvPatchScalarField>
            (
                new externalSpecieDiffusionResistanceFvPatchScalarField(*this)
            );
        }

        //- Construct as copy setting internal field reference
        externalSpecieDiffusionResistanceFvPatchScalarField
        (
            const externalSpecieDiffusionResistanceFvPatchScalarField&,
            const DimensionedField<scalar, volMesh>&
        );

        //- Construct and return a clone setting internal field reference
        virtual tmp<fvPatchScalarField> clone
        (
            const DimensionedField<scalar, volMesh>& iF
        ) const
        {
            return tmp<fvPatchScalarField>
            (
                new externalSpecieDiffusionResistanceFvPatchScalarField(*this, iF)
            );
        }


    // Member Functions

        //- Update the coefficients associated with the patch field
        virtual void updateCoeffs();

        //- Write
        virtual void write(Ostream&) const;
};


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //


#endif

// ************************************************************************* //
