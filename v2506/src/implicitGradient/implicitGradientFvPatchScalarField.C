#include "implicitGradientFvPatchScalarField.H"
#include "addToRunTimeSelectionTable.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

implicitGradientFvPatchScalarField::implicitGradientFvPatchScalarField
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF
)
:
    mixedFvPatchScalarField(p, iF),
    H_cc_(0.0),
    D_CO2_l(0.0),
    C_CO2_g(0.0),
    K_ext(0.0)
{
    valueFraction() = 0.0;
    refValue() = 0.0;
    refGrad() = 0.0;
}

implicitGradientFvPatchScalarField::implicitGradientFvPatchScalarField
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const dictionary& dict
)
:
    mixedFvPatchScalarField(p, iF),
    H_cc_(dict.get<scalar>("H_cc")),
    D_CO2_l(dict.get<scalar>("D_CO2_l")),
    C_CO2_g(dict.get<scalar>("C_CO2_g")),
    K_ext(dict.get<scalar>("K_ext"))
{
    fvPatchScalarField::operator=(patchInternalField());
}

implicitGradientFvPatchScalarField::implicitGradientFvPatchScalarField
(
    const implicitGradientFvPatchScalarField& ptf,
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const fvPatchFieldMapper& mapper
)
:
    mixedFvPatchScalarField(ptf, p, iF, mapper),
    H_cc_(ptf.H_cc_),
    D_CO2_l(ptf.D_CO2_l),
    C_CO2_g(ptf.C_CO2_g),
    K_ext(ptf.K_ext)
{}

implicitGradientFvPatchScalarField::implicitGradientFvPatchScalarField
(
    const implicitGradientFvPatchScalarField& ptf
)
:
    mixedFvPatchScalarField(ptf),
    H_cc_(ptf.H_cc_),
    D_CO2_l(ptf.D_CO2_l),
    C_CO2_g(ptf.C_CO2_g),
    K_ext(ptf.K_ext)
{}

implicitGradientFvPatchScalarField::implicitGradientFvPatchScalarField
(
    const implicitGradientFvPatchScalarField& ptf,
    const DimensionedField<scalar, volMesh>& iF
)
:
    mixedFvPatchScalarField(ptf, iF),
    H_cc_(ptf.H_cc_),
    D_CO2_l(ptf.D_CO2_l),
    C_CO2_g(ptf.C_CO2_g),
    K_ext(ptf.K_ext)
{}

// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void implicitGradientFvPatchScalarField::updateCoeffs()
{
    if (updated()) return;

    const scalarField& delta = patch().deltaCoeffs();

    // Implementing: gradient * D_CO2_l = -K_ext*(C_CO2_g - phi/H_cc)
    // Rearranged: D_CO2_l * grad(phi) + (K_ext/H_cc) * phi = K_ext * C_CO2_g
    //
    // mixedFvPatchField uses:
    //   snGrad = valueFraction*(refValue - patchInternalField) - (1-valueFraction)*refGrad
    //   Which gives boundary flux: -D*snGrad
    //   And we need: D_CO2_l*grad(phi) = -K_ext*(C_CO2_g - phi/H_cc)
    //
    // The mixed BC is: (1-vf)*grad(phi) + vf*delta*(phi - refValue) = (1-vf)*refGrad
    // Setting refGrad = 0 and rearranging:
    //   grad(phi) + vf/(1-vf)*delta*(phi - refValue) = 0
    //
    // Comparing with: grad(phi) + (K_ext/(D_CO2_l*H_cc))*phi = (K_ext*C_CO2_g)/D_CO2_l
    //
    // We get:
    //   alpha = K_ext/(D_CO2_l*H_cc)
    //   vf/(1-vf)*delta = alpha
    //   refValue = C_CO2_g*H_cc

    scalar alpha = K_ext / (D_CO2_l * H_cc_);

    valueFraction() = alpha / (alpha + delta);
    refValue()      = C_CO2_g * H_cc_;
    refGrad()       = 0.0;

    mixedFvPatchScalarField::updateCoeffs();
}

void implicitGradientFvPatchScalarField::write(Ostream& os) const
{
    fvPatchScalarField::write(os);
    os.writeEntry("H_cc", H_cc_);
    os.writeEntry("D_CO2_l", D_CO2_l);
    os.writeEntry("C_CO2_g", C_CO2_g);
    os.writeEntry("K_ext", K_ext);
    fvPatchScalarField::writeValueEntry(os);
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

makePatchTypeField
(
    fvPatchScalarField,
    implicitGradientFvPatchScalarField
);

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// ************************************************************************* //
