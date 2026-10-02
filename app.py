import gradio as gr
from natural_gas_z_factor_calculator import (
    convert_pressure,
    convert_temperature,
    calc_pseudo_critical,
    wichert_aziz_correction,
    solve_dak,
    calc_Bg,
    classify_z
)
import numpy as np
import matplotlib.pyplot as plt

def compute(pressure_val, pressure_unit, temp_val, temp_unit, gas_gravity,
            yCO2, yN2, yH2S, plot_min, plot_max, plot_steps):
    # Convert inputs
    try:
        P_psia = convert_pressure(pressure_val, pressure_unit)
        T_rankine = convert_temperature(temp_val, temp_unit)
    except ValueError as e:
        return str(e), "", "", None

    # Calculate pseudo-critical properties
    Tpc, Ppc = calc_pseudo_critical(gas_gravity)
    Tpc_corr, Ppc_corr = wichert_aziz_correction(Tpc, Ppc, yCO2, yH2S)

    Tpr = T_rankine / Tpc_corr
    Ppr = P_psia / Ppc_corr

    # Solve DAK
    Z = solve_dak(Tpr, Ppr)

    # Bg
    Bg_bbl = calc_Bg(Z, T_rankine, P_psia)
    Bg_ft3 = 0.02827 * Z * T_rankine / P_psia

    # Classification
    classification = classify_z(Z)

    # Plot Z vs pressure range if requested
    plot_obj = None
    if plot_min > 0 and plot_max > plot_min and plot_steps > 1:
        pressures = np.linspace(plot_min, plot_max, int(plot_steps))
        Zs = []
        for p in pressures:
            Ppr_i = p / Ppc_corr
            Zs.append(solve_dak(Tpr, Ppr_i))
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(pressures, Zs, 'b-')
        ax.set_xlabel("Pressure (psia)")
        ax.set_ylabel("Z-factor")
        ax.set_title(f"Z vs Pressure (T = {temp_val:.1f} °F)")
        fig.tight_layout()
        plot_obj = fig

    result_text = (
        f"Z-factor = {Z:.4f}\n"
        f"Bg = {Bg_bbl:.6f} bbl/scf  ({Bg_ft3:.6f} ft³/scf)\n"
        f"Classification: {classification}"
    )
    return result_text, f"{Z:.4f}", f"{Bg_bbl:.6f}", plot_obj

with gr.Blocks(title="Natural Gas Z-Factor Calculator") as demo:
    gr.Markdown("## Natural Gas Z-Factor Calculator (DAK Correlation)")
    gr.Markdown("Compute the compressibility factor Z and formation volume factor Bg using the Dranchuk-Abou-Kassem equation with optional Wichert-Aziz correction.")

    with gr.Row():
        with gr.Column():
            pressure = gr.Number(label="Pressure", value=1000, minimum=0)
            pressure_unit = gr.Dropdown(choices=["psia", "MPa"], value="psia", label="Pressure unit")
        with gr.Column():
            temperature = gr.Number(label="Temperature", value=100, minimum=0)
            temp_unit = gr.Dropdown(choices=["°F", "°C"], value="°F", label="Temperature unit")

    gas_gravity = gr.Slider(minimum=0.55, maximum=1.2, step=0.01, value=0.65, label="Gas Gravity")

    with gr.Accordion("Optional Gas Composition (mole fractions)", open=False):
        yCO2 = gr.Number(label="CO₂", value=0.0, minimum=0, maximum=1, step=0.01)
        yN2 = gr.Number(label="N₂", value=0.0, minimum=0, maximum=1, step=0.01)
        yH2S = gr.Number(label="H₂S", value=0.0, minimum=0, maximum=1, step=0.01)

    gr.Markdown("### Optional: Plot Z vs Pressure Range")
    with gr.Row():
        plot_min = gr.Number(label="Min pressure (psia)", value=500, minimum=0)
        plot_max = gr.Number(label="Max pressure (psia)", value=5000, minimum=0)
        plot_steps = gr.Number(label="Number of steps", value=50, minimum=2, step=1)

    compute_btn = gr.Button("Compute")

    output_text = gr.Textbox(label="Results", lines=4)
    output_z = gr.Textbox(label="Z-factor (decimal)", visible=False)
    output_bg = gr.Textbox(label="Bg (bbl/scf)", visible=False)
    output_plot = gr.Plot(label="Z vs Pressure")

    compute_btn.click(
        fn=compute,
        inputs=[pressure, pressure_unit, temperature, temp_unit, gas_gravity,
                yCO2, yN2, yH2S, plot_min, plot_max, plot_steps],
        outputs=[output_text, output_z, output_bg, output_plot]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
