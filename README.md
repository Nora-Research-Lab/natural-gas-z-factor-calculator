![NORA logo](https://i.ibb.co/0VJCC9Gf/IMG-20260114-WA0008.jpg)
 
# Natural Gas Z-Factor Calculator
 
*For petroleum engineers and gas reservoir analysts: enter pressure, temperature, and gas gravity to instantly compute the compressibility factor (Z) using the Dranchuk-Abou-Kassem correlation.*
 
[![GitHub](https://img.shields.io/badge/GitHub-Nora--Research--Lab-181717?logo=github)](https://github.com/Nora-Research-Lab) [![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-NoraResearchLab-yellow)](https://huggingface.co/NoraResearchLab) [![LinkedIn](https://img.shields.io/badge/LinkedIn-NORA%20Research%20Lab-0A66C2?logo=linkedin)](https://www.linkedin.com/company/nora-research-lab) [![X](https://img.shields.io/badge/X-@noraresearchlab-000000?logo=x)](https://x.com/noraresearchlab) [![NORA Research Lab](https://img.shields.io/badge/Website-noraresearchlab.site-2ea44f)](https://noraresearchlab.site) [![NORA Earth Intelligence](https://img.shields.io/badge/Platform-noraearth.xyz-2ea44f)](https://noraearth.xyz)
 

## Overview
 
**Industry:** Petroleum & Oil/Gas
 
The tool calculates the natural gas compressibility factor (Z) using the Dranchuk-Abou-Kassem (DAK) correlation, which is a standard empirical EOS-based method for hydrocarbon gases.

Inputs:
- Pressure (psia or MPa) — numeric input with unit toggle.
- Temperature (°F or °C) — numeric input with unit toggle.
- Gas gravity (dimensionless, typically 0.55–1.2) — slider or number input.
- Optional: Gas composition (mole fractions of CO2, N2, H2S) if known, else defaults to 0. This is used to compute pseudo-critical properties via the Wichert-Aziz correction.

Core Logic:
1. If no composition given, pseudo-critical temperature (Tpc) and pseudo-critical pressure (Ppc) are estimated from gas gravity using standard correlations: Tpc = 168 + 325*γ - 12.5*γ²; Ppc = 677 + 15.0*γ - 37.5*γ² (for γ ≥ 0.75, use alternative equations).
2. Apply Wichert-Aziz correction if CO2+H2S mole fraction > 0.
3. Compute pseudo-reduced temperature (Tpr = T/Tpc) and pseudo-reduced pressure (Ppr = P/Ppc).
4. Solve the DAK equation for Z using the Newton-Raphson method. The equation is a modified Benedict-Webb-Rubin type with 11 coefficients (A1..A11). Iterate until convergence (|Z_new - Z_old| < 1e-6).
5. Return Z-factor and optionally gas formation volume factor (Bg = 0.02827*Z*T/P in bbl/scf).

Gradio UI Layout:
- Top: Title and brief description.
- First row: two columns. Left: Pressure input (number + unit dropdown). Right: Temperature input (number + unit dropdown).
- Second row: Gas gravity slider (0.55 to 1.2, step 0.01). Optional expandable section for gas composition (mole fractions CO2, N2, H2S each 0–1).
- Compute button.
- Output section: Z-factor (numeric, 4 decimals), gas Bg if selected, and a classification (e.g., Z > 0.9: 'Near-ideal', Z 0.7–0.9: 'Moderate deviation', Z < 0.7: 'High deviation'). Optionally a small plot of Z vs pressure over a range (user can input pressure range steps).

No AI/ML component; purely deterministic correlation with iterative solver.
 
## Run it
 
```bash
docker build -t natural-gas-z-factor-calculator .
docker run -p 7860:7860 natural-gas-z-factor-calculator
```
 
Then open http://localhost:7860 in your browser.
 
## About
 
This tool was generated and published automatically by the **NORA Earth Intelligence**
tool factory, an autonomous pipeline maintained by **NORA Research Lab** that turns
one idea per run into a small, working geoscience tool — end to end, with an
LLM writing and Docker-testing the code, and another model generating the
banner above.
 
- Platform: [https://noraearth.xyz](https://noraearth.xyz)
- Parent lab: [https://noraresearchlab.site](https://noraresearchlab.site)
 
Built 2026-10-02.
 
---
 
### Maintainer
 
**NORA Research Lab**
[![GitHub](https://img.shields.io/badge/GitHub-Nora--Research--Lab-181717?logo=github)](https://github.com/Nora-Research-Lab) [![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-NoraResearchLab-yellow)](https://huggingface.co/NoraResearchLab) [![LinkedIn](https://img.shields.io/badge/LinkedIn-NORA%20Research%20Lab-0A66C2?logo=linkedin)](https://www.linkedin.com/company/nora-research-lab) [![X](https://img.shields.io/badge/X-@noraresearchlab-000000?logo=x)](https://x.com/noraresearchlab) [![NORA Research Lab](https://img.shields.io/badge/Website-noraresearchlab.site-2ea44f)](https://noraresearchlab.site) [![NORA Earth Intelligence](https://img.shields.io/badge/Platform-noraearth.xyz-2ea44f)](https://noraearth.xyz)
