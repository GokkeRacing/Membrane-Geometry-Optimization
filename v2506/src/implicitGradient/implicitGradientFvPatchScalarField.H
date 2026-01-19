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
    Foam::implicitGradientFvPatchScalarField

Group
    grpGenericBoundaryConditions

Description
    This boundary condition provides a implicitGradient condition,
    calculated as:

        \f[
            Q = Q_{0} + Q_{p} + s*Q_{t}
        \f]

    where
    \vartable
        s      | single scalar value [units]
        Q_{0}  | single scalar value [units]
        Q_{p}  | scalar field across patch [units]
        Q_{t}  | scalar function of time [units]
    \endtable

Usage
    \table
        Property   | Description                  | Req'd | Default
        scalarData | single scalar value          | yes |
        data       | single scalar value          | yes |
        fieldData  | scalar field across patch    | yes |
        timeVsData | scalar function of time      | yes |
        wordData   | word, eg name of data object | no  | wordDefault
    \endtable

    Example of the boundary condition specification:
    \verbatim
    <patchName>
    {
        type       implicitGradient;
        scalarData -1;
        data       1;
        fieldData  uniform 3;
        timeVsData table (
                             (0 0)
                             (1 2)
                          );
        wordName   anotherName;
        value      uniform 4; // optional initial value
    }
    \endverbatim

SourceFiles
    implicitGradientFvPatchScalarField.C

\*---------------------------------------------------------------------------*/

#ifndef implicitGradientFvPatchScalarField_H
#define implicitGradientFvPatchScalarField_H

#include "mixedFvPatchFields.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

/*---------------------------------------------------------------------------*\
     Class implicitGradientFvPatchScalarField Declaration
\*---------------------------------------------------------------------------*/

class implicitGradientFvPatchScalarField
:
    public mixedFvPatchScalarField
{
    // Private Data
    
        //- Henry's constant [dimensionless]
        scalar H_cc_;
        
        //- CO2 diffusion coefficient in liquid [m^2/s]
        scalar D_CO2_l;
        
        //- CO2 concentration in gas phase [mol/m^3]
        scalar C_CO2_g;
        
        //- External mass transfer coefficient [m/s]
        scalar K_ext;


public:

    //- Runtime type information
    TypeName("implicitGradient");


    // Constructors

        //- Construct from patch and internal field
        implicitGradientFvPatchScalarField
        (
            const fvPatch&,
            const DimensionedField<scalar, volMesh>&
        );

        //- Construct from patch, internal field and dictionary
        implicitGradientFvPatchScalarField
        (
            const fvPatch&,
            const DimensionedField<scalar, volMesh>&,
            const dictionary&
        );

        //- Construct by mapping onto a new patch
        implicitGradientFvPatchScalarField
        (
            const implicitGradientFvPatchScalarField&,
            const fvPatch&,
            const DimensionedField<scalar, volMesh>&,
            const fvPatchFieldMapper&
        );

        //- Construct as copy
        implicitGradientFvPatchScalarField
        (
            const implicitGradientFvPatchScalarField&
        );

        //- Construct and return a clone
        virtual tmp<fvPatchScalarField> clone() const
        {
            return tmp<fvPatchScalarField>
            (
                new implicitGradientFvPatchScalarField(*this)
            );
        }

        //- Construct as copy setting internal field reference
        implicitGradientFvPatchScalarField
        (
            const implicitGradientFvPatchScalarField&,
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
                new implicitGradientFvPatchScalarField(*this, iF)
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
