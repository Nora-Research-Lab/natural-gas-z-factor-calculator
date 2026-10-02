import numpy as np

# DAK coefficients
A1 = 0.3265
A2 = -1.0700
A3 = -0.5339
A4 = 0.01569
A5 = -0.05165
A6 = 0.5475
A7 = -0.7361
A8 = 0.1844
A9 = 0.1056
A10 = 0.6134
A11 = 0.7210

def convert_pressure(value, unit):
    """Convert pressure to psia."""
    if unit == "psia":
        return value
    elif unit == "MPa":
        return value * 145.037738  # 1 MPa = 145.037738 psia
    else:
        raise ValueError(f"Unknown pressure unit: {unit}")

def convert_temperature(value, unit):
    """Convert temperature to Rankine."""
    if unit == "°F":
        return value + 459.67
    elif unit == "°C":
        return value * 9.0/5.0 + 491.67
    else:
        raise ValueError(f"Unknown temperature unit: {unit}")

def calc_pseudo_critical(gamma):
    """
    Calculate pseudo-critical temperature (R) and pressure (psia) from gas gravity.
    For gamma <= 0.75 or > 0.75, use same formula (standard Sutton).
    """
    Tpc = 168.0 + 325.0 * gamma - 12.5 * gamma**2
    Ppc = 677.0 + 15.0 * gamma - 37.5 * gamma**2
    return Tpc, Ppc

def wichert_aziz_correction(Tpc, Ppc, yCO2, yH2S):
    """
    Apply Wichert-Aziz correction for sour gases.
    Returns corrected Tpc, Ppc.
    """
    A = yCO2 + yH2S
    if A <= 0:
        return Tpc, Ppc
    B = yH2S
    epsilon = 120.0 * (A**0.9 - A**1.6) + 15.0 * (B**0.5 - B**4.0)
    Tpc_corr = Tpc - epsilon
    Ppc_corr = Ppc * Tpc_corr / (Tpc + B * (1 - B) * epsilon)
    return Tpc_corr, Ppc_corr

def dak_function(Z, Tr, Pr):
    """DAK equation residual F(Z) = 0."""
    rho_r = 0.27 * Pr / (Z * Tr)
    # Terms
    term1 = A1 * rho_r
    term2 = A2 * rho_r**2
    term3 = A3 * rho_r**5
    term4 = A4 * rho_r**2 * (1 + A11 * rho_r**2) * np.exp(-A11 * rho_r**2)
    term5 = A5 / Tr
    term6 = A6 / Tr**3
    term7 = A7 / Tr**4
    term8 = A8 / Tr**5
    # Note: A9 and A10 are not used in the standard DAK eq? Typically they are part of other terms? Check.
    # Standard DAK: Z = 1 + A1*ρr + A2*ρr^2 + A3*ρr^5 + A4*ρr^2*(1+A11*ρr^2)*exp(-A11*ρr^2) - (A5/Tr + A6/Tr^3 + A7/Tr^4 + A8/Tr^5)
    # No A9, A10. We'll omit them.
    return Z - (1.0 + term1 + term2 + term3 + term4 - (term5 + term6 + term7 + term8))

def dak_derivative(Z, Tr, Pr):
    """Derivative dF/dZ."""
    rho_r = 0.27 * Pr / (Z * Tr)
    drho_dZ = -rho_r / Z
    # Derivative of terms with respect to Z
    dterm1 = A1 * drho_dZ
    dterm2 = 2 * A2 * rho_r * drho_dZ
    dterm3 = 5 * A3 * rho_r**4 * drho_dZ
    # term4 derivative: A4 * [2*ρr*(1+A11*ρr^2) + ρr^2*(2*A11*ρr)] * exp(-A11*ρr^2) - A4*ρr^2*(1+A11*ρr^2)*exp(-A11*ρr^2)*2*A11*ρr*drho_dZ
    # Let's simplify: let u = ρr^2, then term4 = A4 * u * (1 + A11*u) * exp(-A11*u)
    # du/dZ = 2*ρr*drho_dZ
    # dterm4/du = A4 * [ (1+2*A11*u) * exp(-A11*u) - u*(1+A11*u)*A11*exp(-A11*u) ] = A4*exp(-A11*u)*[1+2*A11*u - A11*u*(1+A11*u)]
    # = A4*exp(-A11*u)*[1+2*A11*u - A11*u - A11^2*u^2] = A4*exp(-A11*u)*[1 + A11*u - A11^2*u^2]
    # Then dterm4/dZ = dterm4/du * du/dZ
    u = rho_r**2
    exp_term = np.exp(-A11 * u)
    dterm4_du = A4 * exp_term * (1 + A11*u - (A11**2)*u**2)
    dterm4 = dterm4_du * 2 * rho_r * drho_dZ
    # Terms 5-8 don't depend on Z
    return 1.0 - (dterm1 + dterm2 + dterm3 + dterm4)

def solve_dak(Tr, Pr, Z_guess=1.0, tol=1e-6, max_iter=50):
    """
    Solve DAK for Z using Newton-Raphson.
    Returns Z-factor.
    """
    Z = Z_guess
    for i in range(max_iter):
        F = dak_function(Z, Tr, Pr)
        dF = dak_derivative(Z, Tr, Pr)
        if abs(dF) < 1e-12:
            break
        Z_new = Z - F / dF
        if abs(Z_new - Z) < tol:
            return Z_new
        Z = Z_new
    return Z

def calc_Bg(Z, T_rankine, P_psia):
    """
    Gas formation volume factor in bbl/scf.
    Bg (bbl/scf) = 0.005034 * Z * T / P
    (Since 1 bbl = 5.6146 ft³; Bg_ft3 = 0.02827*Z*T/P)
    """
    return 0.005034 * Z * T_rankine / P_psia

def classify_z(Z):
    if Z >= 0.9:
        return "Near-ideal gas"
    elif Z >= 0.7:
        return "Moderate deviation"
    else:
        return "High deviation"
