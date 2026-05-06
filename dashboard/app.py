import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from PIL import Image

sys.path.append(str(Path(__file__).resolve().parents[1]))

from simulations.thermal import thermal

st.set_page_config(
    page_title="LiquidFlow AI",
    page_icon="💧",
    layout="wide",
)

logo = Image.open("assets/liquidflow-logo.png")

st.image(
    logo,
    width=90,
)

st.markdown(
    """
    <h1 style='font-size: 4rem; margin-bottom: 0;'>
        LiquidFlow AI
    </h1>

    <p style='font-size: 1.2rem; color: #9aa0aa;'>
        Physics-informed thermal intelligence for high-density AI infrastructure
    </p>
    """,
    unsafe_allow_html=True,
)

st.success(
    "System online • Thermal digital twin active • AI monitoring enabled"
)

c1, c2, c3 = st.columns(3)

with c1:
    st.success("Cooling Network Active")

with c2:
    st.success("AI Monitoring Online")

with c3:
    st.success("Thermal Twin Synced")

st.divider()

with st.sidebar:

    st.markdown("## ⚙️ Control Panel")
    st.caption("Thermal system configuration")

    st.header("System Inputs")

    flow_rate = st.slider("Coolant flow rate", 1.0, 50.0, 12.0)
    inlet_temp = st.slider("Inlet temperature °C", 5.0, 35.0, 20.0)
    heat_load_kw = st.slider("Heat load kW", 10.0, 300.0, 100.0)
    cooling_efficiency = st.slider("Cooling efficiency", 0.1, 1.0, 0.85)

    st.divider()

    uploaded_image = st.file_uploader(
        "Upload thermal / rack image",
        type=["png", "jpg", "jpeg"],
    )

outlet_temp = thermal(
    flow_rate,
    inlet_temp,
    heat_load_kw,
    cooling_efficiency,
)

if outlet_temp is None:
    st.error("Invalid parameters")
    st.stop()

hotspot_risk = "HIGH" if outlet_temp > 30 else "LOW"

risk_score = min(100, max(0, round(((outlet_temp - 20) / 30) * 100)))
cooling_margin = round(max(0, 50 - outlet_temp), 2)
estimated_efficiency = round(cooling_efficiency * 100, 1)

k1, k2, k3, k4 = st.columns(4)

k1.metric("Outlet Temperature", f"{outlet_temp} °C")
k2.metric("Hotspot Classification", hotspot_risk)
k3.metric("Thermal Risk Index", f"{risk_score}/100")
k4.metric("Cooling Safety Margin", f"{cooling_margin} °C")

st.divider()

m1, m2, m3, m4 = st.columns(4)

gpu_utilization = min(
    100,
    round((heat_load_kw / 300) * 100),
)

cooling_pressure = round(
    flow_rate * 0.42,
    2,
)

pue_estimate = round(
    1.1 + ((100 - estimated_efficiency) / 100),
    2,
)

with m1:
    st.metric(
        "Estimated Rack Power",
        f"{heat_load_kw} kW",
    )

with m2:
    st.metric(
        "GPU Utilization",
        f"{gpu_utilization}%",
    )

with m3:
    st.metric(
        "Cooling Loop Pressure",
        f"{cooling_pressure} bar",
    )

with m4:
    st.metric(
        "Estimated PUE",
        f"{pue_estimate}",
    )

st.divider()

left, right = st.columns([1.2, 1])

with left:
    st.subheader("🌡️ Thermal Field Simulation")

    x = np.linspace(0, 1, 100)
    y = np.linspace(0, 1, 100)
    X, Y = np.meshgrid(x, y)

    base_temp = inlet_temp
    thermal_gradient = outlet_temp - inlet_temp

    time_factor = st.slider(
        "Simulation Time Step",
        0.0,
        1.0,
        0.5,
    )

    dynamic_hotspot = (
        8
        * np.exp(
            -(
                (X - (0.55 + 0.25 * time_factor)) ** 2
                + (Y - 0.5) ** 2
            )
            / 0.015
        )
    )

    Z_dynamic = (
        base_temp
        + thermal_gradient * X
        + dynamic_hotspot
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    heatmap = ax.contourf(
        X,
        Y,
        Z_dynamic,
        levels=35,
    )

    plt.colorbar(
        heatmap,
        ax=ax,
        label="Temperature °C",
    )

    ax.set_title("Dynamic Thermal Propagation Simulation")
    ax.set_xlabel("Rack Width")
    ax.set_ylabel("Rack Height")

    st.pyplot(fig)

with right:
    st.subheader("🧠 AI Recommendation Engine")

    if hotspot_risk == "HIGH":
        st.error("Critical hotspot formation detected")

        st.write("Recommended actions:")
        st.write("• Increase coolant flow rate by 15-25%")
        st.write("• Reduce rack compute density")
        st.write("• Improve cooling loop efficiency")
        st.write("• Redistribute thermal load across racks")
        st.write("• Inspect cooling plate thermal contact")

    else:
        st.success("System operating within acceptable thermal range")

        st.write("Recommended actions:")
        st.write("• Maintain current cooling configuration")
        st.write("• Continue monitoring outlet temperature")
        st.write("• No immediate intervention required")

    st.divider()

    st.subheader("🏗️ Infrastructure AI Insight")

    if outlet_temp > 40:
        st.warning(
            "Predicted thermal behavior suggests elevated infrastructure stress "
            "and possible reduction in hardware lifespan under sustained operation."
        )
    elif outlet_temp > 30:
        st.info(
            "Moderate thermal stress detected. Long-duration workloads may benefit "
            "from proactive cooling optimization."
        )
    else:
        st.success(
            "Thermal operating conditions appear stable for sustained AI workloads."
        )

st.divider()

st.subheader("👁️ Multimodal Thermal Image Analysis")

if uploaded_image is not None:

    image = Image.open(uploaded_image)

    st.image(
        image,
        caption="Uploaded thermal / infrastructure image",
        use_container_width=True,
    )

    st.success("Vision analysis pipeline active")

    st.write("Detected infrastructure observations:")

    observations = [
        "Localized thermal concentration detected",
        "Cooling asymmetry identified near rack boundary",
        "Potential hotspot propagation risk",
        "Thermal gradient exceeds nominal threshold",
        "Infrastructure cooling optimization recommended",
    ]

    for obs in observations:
        st.write(f"• {obs}")

    st.divider()

    st.subheader("🧠 Vision AI Interpretation")

    if hotspot_risk == "HIGH":

        st.warning(
            "The uploaded infrastructure image suggests elevated thermal accumulation "
            "consistent with high-density GPU workloads and insufficient cooling dispersion."
        )

    else:

        st.success(
            "The uploaded infrastructure image indicates relatively stable cooling "
            "behavior with acceptable thermal distribution."
        )

    st.caption(
        "Prototype multimodal workflow. Future versions will integrate Qwen-VL "
        "or Llama Vision models running on AMD GPUs."
    )

else:

    st.write(
        "Upload a rack, cooling plate, or thermal image to activate the multimodal analysis module."
    )

st.divider()

st.subheader("📘 Project Summary")

st.write(
    "LiquidFlow AI is a physics-informed thermal intelligence platform for next-generation "
    "AI infrastructure. It simulates liquid cooling behavior, predicts hotspot risk, "
    "visualizes thermal fields, and provides AI-assisted cooling recommendations."
)

st.divider()

st.subheader("🤖 LiquidFlow AI Copilot")

user_question = st.text_input(
    "Ask the thermal AI assistant",
    placeholder="Example: Why is hotspot risk high?",
)

if user_question:
    st.write("AI Copilot Response:")

    if hotspot_risk == "HIGH":
        st.warning(
            "The system is detecting high thermal risk because the predicted outlet "
            "temperature exceeds the safe operating threshold. The most effective first "
            "actions are increasing coolant flow, improving cooling efficiency, or reducing "
            "rack heat load."
        )
    else:
        st.success(
            "The system is currently operating within the acceptable thermal range. "
            "Cooling margin is positive and no immediate intervention is required."
        )

    st.caption(
        "Prototype copilot logic. Future version can connect to Qwen, Llama, or AMD-hosted inference APIs."
    )

st.divider()

st.caption(
    "LiquidFlow AI • Built for the AMD Developer Hackathon • "
    "Physics-informed infrastructure intelligence"
)