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

#include "codedFvOptionTemplate.H"
#include "addToRunTimeSelectionTable.H"
#include "fvPatchFieldMapper.H"
#include "volFields.H"
#include "surfaceFields.H"
#include "unitConversion.H"
#include "fvMatrix.H"

//{{{ begin codeInclude
#line 83 "/home/mathias110300/OpenFOAM/mathias110300-v2512/run/Membrane-Geometry-Optimization/v2512/run/P8_Model/system/controlDict/functions/S/fvOptions/reaction"
#include "fvCFD.H"
//}}} end codeInclude


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
namespace fv
{

// * * * * * * * * * * * * * * * Local Functions * * * * * * * * * * * * * * //

//{{{ begin localCode

//}}} end localCode


// * * * * * * * * * * * * * * * Global Functions  * * * * * * * * * * * * * //

// dynamicCode:
// SHA1 = 39d156564be1296777c4922581b9cdd237ab3e42
//
// unique function name that can be checked if the correct library version
// has been loaded
extern "C" void S_react_39d156564be1296777c4922581b9cdd237ab3e42(bool load)
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

defineTypeNameAndDebug(S_reactFvOptionscalarSource, 0);
addRemovableToRunTimeSelectionTable
(
    option,
    S_reactFvOptionscalarSource,
    dictionary
);

} // End namespace fv
} // End namespace Foam


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::fv::
S_reactFvOptionscalarSource::
S_reactFvOptionscalarSource
(
    const word& name,
    const word& modelType,
    const dictionary& dict,
    const fvMesh& mesh
)
:
    fv::cellSetOption(name, modelType, dict, mesh)
{
    if (false)
    {
        printMessage("Construct S_react fvOption from dictionary");
    }
}


// * * * * * * * * * * * * * * * * Destructor  * * * * * * * * * * * * * * * //

Foam::fv::
S_reactFvOptionscalarSource::
~S_reactFvOptionscalarSource()
{
    if (false)
    {
        printMessage("Destroy S_react");
    }
}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void
Foam::fv::
S_reactFvOptionscalarSource::correct
(
    GeometricField<scalar, fvPatchField, volMesh>& fld
)
{
    if (false)
    {
        Info<< "S_reactFvOptionscalarSource::correct()\n";
    }

//{{{ begin code
    
//}}} end code
}


void
Foam::fv::
S_reactFvOptionscalarSource::addSup
(
    fvMatrix<scalar>& eqn,
    const label fieldi
)
{
    if (false)
    {
        Info<< "S_reactFvOptionscalarSource::addSup()\n";
    }

//{{{ begin code - warn/fatal if not implemented?
    #line 88 "/home/mathias110300/OpenFOAM/mathias110300-v2512/run/Membrane-Geometry-Optimization/v2512/run/P8_Model/system/controlDict/functions/S/fvOptions/reaction"
const scalarField& V = mesh_.V();
                    const fvMesh& mesh = eqn.psi().mesh();
                    const volScalarField& k_rxn = mesh.lookupObject<volScalarField>("k_rxn");
                    const volScalarField& C_CO2  = mesh.lookupObject<volScalarField>("C_CO2");
                    const volScalarField& C_CO2_old = C_CO2.oldTime();                       

                    scalarField& Sp = eqn.diag();

                    forAll(Sp, cellI)
                    {
                        const scalar coeff = k_rxn[cellI] * C_CO2_old[cellI];
                        Sp[cellI] -= coeff * V[cellI];
                    }
//}}} end code
}


void
Foam::fv::
S_reactFvOptionscalarSource::addSup
(
    const volScalarField& rho,
    fvMatrix<scalar>& eqn,
    const label fieldi
)
{
    if (false)
    {
        Info<< "S_reactFvOptionscalarSource::addSup(rho)\n";
    }

//{{{ begin code - warn/fatal if not implemented?
    NotImplemented
//}}} end code
}


void
Foam::fv::
S_reactFvOptionscalarSource::constrain
(
    fvMatrix<scalar>& eqn,
    const label fieldi
)
{
    if (false)
    {
        Info<< "S_reactFvOptionscalarSource::constrain()\n";
    }

//{{{ begin code
    
//}}} end code
}


// ************************************************************************* //

