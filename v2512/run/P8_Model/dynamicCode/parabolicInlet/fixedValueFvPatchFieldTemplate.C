/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
    Copyright (C) 2019-2021 OpenCFD Ltd.
    Copyright (C) YEAR AUTHOR, AFFILIATION
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

\*---------------------------------------------------------------------------*/

#include "fixedValueFvPatchFieldTemplate.H"
#include "addToRunTimeSelectionTable.H"
#include "fvPatchFieldMapper.H"
#include "volFields.H"
#include "surfaceFields.H"
#include "unitConversion.H"
#include "PatchFunction1.H"

//{{{ begin codeInclude

//}}} end codeInclude


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * * Local Functions * * * * * * * * * * * * * * //

//{{{ begin localCode

//}}} end localCode


// * * * * * * * * * * * * * * * Global Functions  * * * * * * * * * * * * * //

// dynamicCode:
// SHA1 = 0c6bbb85af6feefe0924afe87b2b07306e83e13e
//
// unique function name that can be checked if the correct library version
// has been loaded
extern "C" void parabolicInlet_0c6bbb85af6feefe0924afe87b2b07306e83e13e(bool load)
{
    if (load)
    {
        // Code that can be explicitly executed after loading
    }
    else
    {
        // Code that can be explicitly executed before unloading
    }
}

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

makeRemovablePatchTypeField
(
    fvPatchVectorField,
    parabolicInletFixedValueFvPatchVectorField
);

} // End namespace Foam


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::
parabolicInletFixedValueFvPatchVectorField::
parabolicInletFixedValueFvPatchVectorField
(
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF
)
:
    parent_bctype(p, iF)
{
    if (false)
    {
        printMessage("Construct parabolicInlet : patch/DimensionedField");
    }
}


Foam::
parabolicInletFixedValueFvPatchVectorField::
parabolicInletFixedValueFvPatchVectorField
(
    const parabolicInletFixedValueFvPatchVectorField& rhs,
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF,
    const fvPatchFieldMapper& mapper
)
:
    parent_bctype(rhs, p, iF, mapper)
{
    if (false)
    {
        printMessage("Construct parabolicInlet : patch/DimensionedField/mapper");
    }
}


Foam::
parabolicInletFixedValueFvPatchVectorField::
parabolicInletFixedValueFvPatchVectorField
(
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF,
    const dictionary& dict
)
:
    parent_bctype(p, iF, dict)
{
    if (false)
    {
        printMessage("Construct parabolicInlet : patch/dictionary");
    }
}


Foam::
parabolicInletFixedValueFvPatchVectorField::
parabolicInletFixedValueFvPatchVectorField
(
    const parabolicInletFixedValueFvPatchVectorField& rhs
)
:
    parent_bctype(rhs),
    dictionaryContent(rhs)
{
    if (false)
    {
        printMessage("Copy construct parabolicInlet");
    }
}


Foam::
parabolicInletFixedValueFvPatchVectorField::
parabolicInletFixedValueFvPatchVectorField
(
    const parabolicInletFixedValueFvPatchVectorField& rhs,
    const DimensionedField<vector, volMesh>& iF
)
:
    parent_bctype(rhs, iF)
{
    if (false)
    {
        printMessage("Construct parabolicInlet : copy/DimensionedField");
    }
}


// * * * * * * * * * * * * * * * * Destructor  * * * * * * * * * * * * * * * //

Foam::
parabolicInletFixedValueFvPatchVectorField::
~parabolicInletFixedValueFvPatchVectorField()
{
    if (false)
    {
        printMessage("Destroy parabolicInlet");
    }
}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void
Foam::
parabolicInletFixedValueFvPatchVectorField::updateCoeffs()
{
    if (this->updated())
    {
        return;
    }

    if (false)
    {
        printMessage("updateCoeffs parabolicInlet");
    }

//{{{ begin code
    #line 31 "/home/mathias110300/OpenFOAM/mathias110300-v2512/run/Membrane-Geometry-Optimization/v2512/run/P8_Model/0/U/boundaryField/inlet"
const scalar Uavg = 3.84e-5;
            const vectorField& faceCentres = patch().Cf(); 
            static bool firstTime = true;
            static scalar R = -GREAT;

            vectorField& field = *this;

            if (firstTime)
            {  
                const pointField& points = patch().patch().points();

                forAll(points, i)
                {
                    R = max(R, points[i].x());
                }
                reduce(R, maxOp<scalar>());
                firstTime = false;
            }

            forAll(field, i)
            {
                scalar x = faceCentres[i].x();
                scalar y = faceCentres[i].y();
                scalar r = sqrt(x*x + y*y);
                scalar Uz = 2*Uavg * (1.0 - r*r/R/R);
                field[i] = vector(0, 0, Uz);
            }
//}}} end code

    this->parent_bctype::updateCoeffs();
}


// ************************************************************************* //

