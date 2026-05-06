import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from simulations.thermal import thermal

st.set_page_config(
    page_title="LiquidFlow AI",
    page_icon="💧",
    layout="wide"
)

st.title("💧 LiquidFlow AI")
st.caption("Physics-informed thermal intelligence for high-density AI infrastructure")

st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Cooling Inputs")

    flow_rate = st.slider("Coolant flow rate", 1.0, 50.0, 12.0)
    inlet_temp = st.slider("Inlet temperature °C", 5.0, 35.0, 20.0)
    heat_load_kw = st.slider("Heat load kW", 10.0, 300.0, 100.0)
    cooling_efficiency = st.slider("Cooling efficiency", 0.1, 1.0, 0.85)

    outlet_temp = thermal(
        flow_rate,
        inlet_temp,
        heat_load_kw,
        cooling_efficiency
    )

    if outlet_temp is None:
        st.error("Invalid parameters")
        st.stop()

    hotspot_risk = "HIGH" if outlet_temp > 30 else "LOW"

    st.metric("Predicted Outlet Temperature", f"{outlet_temp} °C")
    st.metric("Hotspot Risk", hotspot_risk)

with col2:
    st.subheader("Thermal Field Simulation")

    x = np.linspace(0, 1, 80)
    y = np.linspace(0, 1, 80)
    X, Y = np.meshgrid(x, y)

    base_temp = inlet_temp
    thermal_gradient = outlet_temp - inlet_temp

    Z = (
        base_temp
        + thermal_gradient * X
        + 8 * np.exp(-((X - 0.75) ** 2 + (Y - 0.5) ** 2) / 0.015)
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    heatmap = ax.contourf(X, Y, Z, levels=30)
    plt.colorbar(heatmap, ax=ax, label="Temperature °C")

    ax.set_title("Predicted Cooling Plate Temperature Field")
    ax.set_xlabel("Rack Width")
    ax.set_ylabel("Rack Height")

    st.pyplot(fig)

st.divider()

st.subheader("AI System Recommendation")

if hotspot_risk == "HIGH":
    st.warning(
        "High thermal risk detected. Increase coolant flow rate, improve cooling efficiency, "
        "or reduce heat load before sustained operation."
    )
else:
    st.success(
        "Thermal behavior is stable. Current cooling configuration appears acceptable."
    )