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

#include "functionObjectTemplate.H"
#define namespaceFoam  // Suppress <using namespace Foam;>
#include "fvCFD.H"
#include "unitConversion.H"
#include "addToRunTimeSelectionTable.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

defineTypeNameAndDebug(writeDataFunctionObject, 0);

addRemovableToRunTimeSelectionTable
(
    functionObject,
    writeDataFunctionObject,
    dictionary
);


// * * * * * * * * * * * * * * * Global Functions  * * * * * * * * * * * * * //

// dynamicCode:
// SHA1 = 7e32589dc775e0ef54ea474293006e3b01eaaa6c
//
// unique function name that can be checked if the correct library version
// has been loaded
extern "C" void writeData_7e32589dc775e0ef54ea474293006e3b01eaaa6c(bool load)
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


// * * * * * * * * * * * * * * * Local Functions * * * * * * * * * * * * * * //

//{{{ begin localCode

//}}} end localCode

} // End namespace Foam


// * * * * * * * * * * * * * Private Member Functions  * * * * * * * * * * * //

const Foam::fvMesh&
Foam::writeDataFunctionObject::mesh() const
{
    return refCast<const fvMesh>(obr_);
}


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::
writeDataFunctionObject::
writeDataFunctionObject
(
    const word& name,
    const Time& runTime,
    const dictionary& dict
)
:
    functionObjects::regionFunctionObject(name, runTime, dict)
{
    read(dict);
}


// * * * * * * * * * * * * * * * * Destructor  * * * * * * * * * * * * * * * //

Foam::
writeDataFunctionObject::
~writeDataFunctionObject()
{}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

bool
Foam::
writeDataFunctionObject::read(const dictionary& dict)
{
    if (false)
    {
        printMessage("read writeData");
    }

//{{{ begin code
    
//}}} end code

    return true;
}


bool
Foam::
writeDataFunctionObject::execute()
{
    if (false)
    {
        printMessage("execute writeData");
    }

//{{{ begin code
    
//}}} end code

    return true;
}


bool
Foam::
writeDataFunctionObject::write()
{
    if (false)
    {
        printMessage("write writeData");
    }

//{{{ begin code
    #line 16 "/home/mathias110300/OpenFOAM/mathias110300-v2512/run/Membrane-Geometry-Optimization/v2512/run/P8_Model/system/controlDict/functions/writeData"
const vectorField faceCentres = mesh().boundaryMesh()["surface"].faceCentres();
    boundBox bb(faceCentres);
    
    // Find dimension with maximum extent
    vector bbMax = bb.max();
    vector bbMin = bb.min();
    vector span = bbMax - bbMin;
    
    label maxDir = 0;
    if (mag(span[1]) > mag(span[0])) maxDir = 1;
    if (mag(span[2]) > mag(span[maxDir])) maxDir = 2;

    // Lookup fields
    const volScalarField& S = mesh().lookupObject<volScalarField>("C_S");
    const volScalarField& CO2 = mesh().lookupObject<volScalarField>("C_CO2");
    const vectorField& cellCentres = mesh().C();
    const scalarField& cellVolumes = mesh().V();

    //Create list of lists to gather data for each processor at their own index
    List<List<scalar>> gatheredCoords(Pstream::nProcs());
    List<List<scalar>> gatheredS(Pstream::nProcs());
    List<List<scalar>> gatheredCO2(Pstream::nProcs());
    List<List<scalar>> gatheredVol(Pstream::nProcs());
    List<List<scalar>> gatheredSurface(Pstream::nProcs());
    
    gatheredCoords[Pstream::myProcNo()] = cellCentres.component(maxDir);
    gatheredS[Pstream::myProcNo()] = S.primitiveField();
    gatheredCO2[Pstream::myProcNo()] = CO2.primitiveField();
    gatheredVol[Pstream::myProcNo()] = cellVolumes;
    gatheredSurface[Pstream::myProcNo()] = faceCentres.component(maxDir);

    //Info << gatheredSurface[Pstream::myProcNo()] << endl;

    Pstream::gatherList(gatheredCoords);
    Pstream::gatherList(gatheredS);
    Pstream::gatherList(gatheredCO2);
    Pstream::gatherList(gatheredVol);
    Pstream::gatherList(gatheredSurface);

    if (Pstream::master())
    {
        // Flatten gathered cell data to iterate over
        DynamicList<scalar> coords, sVals, co2Vals, vols, allSurfaceCoords;
        forAll(gatheredCoords, proci)
        {
            coords.append(gatheredCoords[proci]);
            sVals.append(gatheredS[proci]);
            co2Vals.append(gatheredCO2[proci]);
            vols.append(gatheredVol[proci]);
            allSurfaceCoords.append(gatheredSurface[proci]);
        }

        // Output files
        fileName outputFile_S = "S.csv";
        fileName outputFile_CO2 = "CO2.csv";
        std::ofstream outS(outputFile_S);
        std::ofstream outCO2(outputFile_CO2);
        outS.precision(12);
        outCO2.precision(12);
        outS << "#coord S" << std::endl;
        outCO2 << "#coord CO2" << std::endl;
        
        // For each surface coordinate along averaging direction, average cells at that position
        forAll(allSurfaceCoords, i)
        {
            scalar targetCoord = allSurfaceCoords[i];
            scalar sumS = 0.0, sumCO2 = 0.0, sumVol = 0.0;
            
            forAll(coords, cellI)
            {
                if (mag(coords[cellI] - targetCoord) < 1e-6)
                {
                    sumS += sVals[cellI] * vols[cellI];
                    sumCO2 += co2Vals[cellI] * vols[cellI];
                    sumVol += vols[cellI];
                }
            }
            
            outS << targetCoord << ", " << sumS/sumVol << std::endl;
            outCO2 << targetCoord << ", " << sumCO2/sumVol << std::endl;
        }
        
        outS.close();
        outCO2.close();
        Info << "Layer-averaged data written to " << outputFile_S << " and " << outputFile_CO2 << endl;
    }
//}}} end code

    return true;
}


bool
Foam::
writeDataFunctionObject::end()
{
    if (false)
    {
        printMessage("end writeData");
    }

//{{{ begin code
    
//}}} end code

    return true;
}


// ************************************************************************* //

