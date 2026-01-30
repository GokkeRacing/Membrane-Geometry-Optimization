#include "externalSpecieDiffusionResistanceFvPatchScalarField.H"
#include "addToRunTimeSelectionTable.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

externalSpecieDiffusionResistanceFvPatchScalarField::externalSpecieDiffusionResistanceFvPatchScalarField
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF
)
:
    mixedFvPatchScalarField(p, iF),
    H_cc(0.0),
    D_CO2_l(0.0),
    C_CO2_g(0.0),
    K_ext(0.0)
{
    valueFraction() = 0.0;
    refValue() = 0.0;
    refGrad() = 0.0;
}

externalSpecieDiffusionResistanceFvPatchScalarField::externalSpecieDiffusionResistanceFvPatchScalarField
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const dictionary& dict
)
:
    mixedFvPatchScalarField(p, iF),
    H_cc(dict.get<scalar>("H_cc")),
    D_CO2_l(dict.get<scalar>("D_CO2_l")),
    C_CO2_g(dict.get<scalar>("C_CO2_g")),
    K_ext(dict.get<scalar>("K_ext"))
{
    fvPatchScalarField::operator=(patchInternalField());
}

externalSpecieDiffusionResistanceFvPatchScalarField::externalSpecieDiffusionResistanceFvPatchScalarField
(
    const externalSpecieDiffusionResistanceFvPatchScalarField& ptf,
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const fvPatchFieldMapper& mapper
)
:
    mixedFvPatchScalarField(ptf, p, iF, mapper),
    H_cc(ptf.H_cc),
    D_CO2_l(ptf.D_CO2_l),
    C_CO2_g(ptf.C_CO2_g),
    K_ext(ptf.K_ext)
{}

externalSpecieDiffusionResistanceFvPatchScalarField::externalSpecieDiffusionResistanceFvPatchScalarField
(
    const externalSpecieDiffusionResistanceFvPatchScalarField& ptf
)
:
    mixedFvPatchScalarField(ptf),
    H_cc(ptf.H_cc),
    D_CO2_l(ptf.D_CO2_l),
    C_CO2_g(ptf.C_CO2_g),
    K_ext(ptf.K_ext)
{}

externalSpecieDiffusionResistanceFvPatchScalarField::externalSpecieDiffusionResistanceFvPatchScalarField
(
    const externalSpecieDiffusionResistanceFvPatchScalarField& ptf,
    const DimensionedField<scalar, volMesh>& iF
)
:
    mixedFvPatchScalarField(ptf, iF),
    H_cc(ptf.H_cc),
    D_CO2_l(ptf.D_CO2_l),
    C_CO2_g(ptf.C_CO2_g),
    K_ext(ptf.K_ext)
{}

// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void externalSpecieDiffusionResistanceFvPatchScalarField::updateCoeffs()
{
    if (updated()) return;

    // --- Compute the patch-based boundary fraction for the Robin BC ---
    // Physical quantities:
    // K_ext  : Mass transfer coefficient
    // H_cc_  : Henry's constant
    // D_CO2_l: Diffusion coefficient in liquid
    // C_CO2_g: Gas-phase concentration

    const scalarField& deltaCoeff = patch().deltaCoeffs();

    // Compute valueFraction using explicit resistance balance:
    // boundary resistance = H_cc_ / K_ext
    // diffusion resistance = 1 / deltaCoeff / D_CO2_l
    valueFraction() = K_ext / (K_ext + D_CO2_l * H_cc * deltaCoeff);

    // Reference (Dirichlet) value: Henry's law
    refValue() = C_CO2_g * H_cc;

    // Gradient along patch normal is zero
    refGrad() = 0.0;

    mixedFvPatchScalarField::updateCoeffs();
}

void externalSpecieDiffusionResistanceFvPatchScalarField::write(Ostream& os) const
{
    fvPatchScalarField::write(os);
    os.writeEntry("H_cc", H_cc);
    os.writeEntry("D_CO2_l", D_CO2_l);
    os.writeEntry("C_CO2_g", C_CO2_g);
    os.writeEntry("K_ext", K_ext);
    fvPatchScalarField::writeValueEntry(os);
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

makePatchTypeField
(
    fvPatchScalarField,
    externalSpecieDiffusionResistanceFvPatchScalarField
);

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// ************************************************************************* //
