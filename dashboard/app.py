import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

sys.path.append(str(Path(__file__).resolve().parents[1]))

from simulations.thermal import thermal
from models.surrogate_model import surrogate_temperature_prediction


st.set_page_config(
    page_title="LiquidFlow AI",
    page_icon="💧",
    layout="wide",
)


def classify_hotspot(outlet_temp: float) -> str:
    return "HIGH" if outlet_temp > 30 else "LOW"


def calculate_risk_score(outlet_temp: float) -> int:
    return min(100, max(0, round(((outlet_temp - 20) / 30) * 100)))


def optimize_cooling(
    flow_rate: float,
    inlet_temp: float,
    heat_load_kw: float,
    cooling_efficiency: float,
) -> dict:
    best_result = None

    flow_options = np.linspace(flow_rate, min(flow_rate * 2.0, 50), 20)
    inlet_options = np.linspace(max(inlet_temp - 8, 5), inlet_temp, 10)
    efficiency_options = np.linspace(
        cooling_efficiency,
        min(cooling_efficiency + 0.15, 1.0),
        10,
    )

    for candidate_flow in flow_options:
        for candidate_inlet in inlet_options:
            for candidate_efficiency in efficiency_options:
                candidate_outlet = thermal(
                    candidate_flow,
                    candidate_inlet,
                    heat_load_kw,
                    candidate_efficiency,
                )

                if candidate_outlet is None:
                    continue

                candidate_outlet = round(float(candidate_outlet), 2)
                candidate_risk = classify_hotspot(candidate_outlet)
                candidate_score = calculate_risk_score(candidate_outlet)

                penalty = (
                    abs(candidate_flow - flow_rate) * 0.4
                    + abs(candidate_inlet - inlet_temp) * 0.8
                    + abs(candidate_efficiency - cooling_efficiency) * 20
                )

                objective = candidate_outlet + penalty

                result = {
                    "optimized_flow_rate": round(float(candidate_flow), 2),
                    "optimized_inlet_temp": round(float(candidate_inlet), 2),
                    "optimized_cooling_efficiency": round(float(candidate_efficiency), 2),
                    "optimized_outlet_temp": candidate_outlet,
                    "optimized_hotspot_risk": candidate_risk,
                    "optimized_risk_score": candidate_score,
                    "objective_score": round(float(objective), 2),
                }

                if best_result is None or objective < best_result["objective_score"]:
                    best_result = result

    return best_result


def draw_hotspot_overlay(image: Image.Image, hotspot_risk: str, risk_score: int) -> tuple[Image.Image, list[dict]]:
    image = image.convert("RGB")
    overlay = image.copy()
    draw = ImageDraw.Draw(overlay)

    width, height = overlay.size

    if hotspot_risk == "HIGH":
        detections = [
            {
                "label": "Primary Hotspot",
                "severity": "Critical",
                "confidence": 0.91,
                "box": (
                    int(width * 0.57),
                    int(height * 0.18),
                    int(width * 0.82),
                    int(height * 0.48),
                ),
            },
            {
                "label": "Cooling Imbalance",
                "severity": "High",
                "confidence": 0.84,
                "box": (
                    int(width * 0.15),
                    int(height * 0.35),
                    int(width * 0.42),
                    int(height * 0.70),
                ),
            },
        ]
    else:
        detections = [
            {
                "label": "Stable Thermal Zone",
                "severity": "Low",
                "confidence": 0.78,
                "box": (
                    int(width * 0.58),
                    int(height * 0.32),
                    int(width * 0.86),
                    int(height * 0.62),
                ),
            }
        ]

    for detection in detections:
        box = detection["box"]
        label = detection["label"]
        severity = detection["severity"]
        confidence = detection["confidence"]

        if severity in ["Critical", "High"]:
            color = (255, 0, 0)
        else:
            color = (0, 255, 0)

        draw.rectangle(box, outline=(255, 40, 40), width=10)

        text = f"{label} | {severity} | {round(confidence * 100)}%"
        text_position = (box[0], max(0, box[1] - 28))

        draw.rectangle(
            [
                text_position[0],
                text_position[1],
                min(width, text_position[0] + 360),
                text_position[1] + 24,
            ],
            fill="black",
        )

        draw.text(text_position, text, fill=(255, 60, 60))

    return overlay, detections


SCENARIOS = {
    "Balanced AI Training Rack": {
        "flow_rate": 12.0,
        "inlet_temp": 20.0,
        "heat_load_kw": 100.0,
        "cooling_efficiency": 0.85,
    },
    "High-Density MI300X Cluster": {
        "flow_rate": 8.0,
        "inlet_temp": 24.0,
        "heat_load_kw": 260.0,
        "cooling_efficiency": 0.55,
    },
    "Cooling Loop Degradation": {
        "flow_rate": 5.0,
        "inlet_temp": 28.0,
        "heat_load_kw": 220.0,
        "cooling_efficiency": 0.40,
    },
    "Emergency Thermal Event": {
        "flow_rate": 3.0,
        "inlet_temp": 32.0,
        "heat_load_kw": 300.0,
        "cooling_efficiency": 0.25,
    },
}


logo_path = Path("assets/liquidflow-logo.png")

if logo_path.exists():
    logo = Image.open(logo_path)
    st.image(logo, width=90)
else:
    st.markdown("# 💧")

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

st.success("System online • Thermal digital twin active • AI monitoring enabled")

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

    selected_scenario = st.selectbox(
        "Infrastructure Scenario",
        list(SCENARIOS.keys()),
    )

    scenario = SCENARIOS[selected_scenario]

    flow_rate = st.slider(
        "Coolant flow rate",
        1.0,
        50.0,
        float(scenario["flow_rate"]),
    )

    inlet_temp = st.slider(
        "Inlet temperature °C",
        5.0,
        35.0,
        float(scenario["inlet_temp"]),
    )

    heat_load_kw = st.slider(
        "Heat load kW",
        10.0,
        300.0,
        float(scenario["heat_load_kw"]),
    )

    cooling_efficiency = st.slider(
        "Cooling efficiency",
        0.1,
        1.0,
        float(scenario["cooling_efficiency"]),
    )

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

surrogate_prediction = surrogate_temperature_prediction(
    flow_rate,
    inlet_temp,
    heat_load_kw,
    cooling_efficiency,
)

if outlet_temp is None:
    st.error("Invalid parameters. Flow rate and cooling efficiency must be greater than 0.")
    st.stop()

outlet_temp = round(float(outlet_temp), 2)
surrogate_prediction = round(float(surrogate_prediction), 2)

hotspot_risk = classify_hotspot(outlet_temp)
risk_score = calculate_risk_score(outlet_temp)
cooling_margin = round(max(0, 50 - outlet_temp), 2)
estimated_efficiency = round(cooling_efficiency * 100, 1)

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Outlet Temperature", f"{outlet_temp} °C")
k2.metric("Hotspot Classification", hotspot_risk)
k3.metric("Thermal Risk Index", f"{risk_score}/100")
k4.metric("Cooling Safety Margin", f"{cooling_margin} °C")
k5.metric("Surrogate Prediction", f"{surrogate_prediction} °C")

st.divider()

st.subheader("⚡ Cooling Optimization Engine")

optimized = optimize_cooling(
    flow_rate,
    inlet_temp,
    heat_load_kw,
    cooling_efficiency,
)

if optimized is not None:
    temp_reduction = round(outlet_temp - optimized["optimized_outlet_temp"], 2)
    risk_reduction = risk_score - optimized["optimized_risk_score"]

    o1, o2, o3, o4 = st.columns(4)

    with o1:
        st.metric(
            "Optimized Outlet Temp",
            f"{optimized['optimized_outlet_temp']} °C",
            delta=f"{temp_reduction} °C reduced",
        )

    with o2:
        st.metric(
            "Optimized Risk",
            optimized["optimized_hotspot_risk"],
            delta=f"{risk_reduction} points",
        )

    with o3:
        st.metric(
            "Recommended Flow Rate",
            f"{optimized['optimized_flow_rate']} L/min",
        )

    with o4:
        st.metric(
            "Recommended Efficiency",
            f"{optimized['optimized_cooling_efficiency']}",
        )

    before_after = {
        "Current": outlet_temp,
        "Optimized": optimized["optimized_outlet_temp"],
    }

    fig_opt, ax_opt = plt.subplots(figsize=(7, 3))
    ax_opt.bar(before_after.keys(), before_after.values())
    ax_opt.axhline(30, linestyle="--", label="Hotspot threshold")
    ax_opt.set_ylabel("Outlet Temperature °C")
    ax_opt.set_title("Current vs Optimized Cooling Performance")
    ax_opt.legend()

    st.pyplot(fig_opt)

    st.success(
        f"Optimization complete: risk transition {hotspot_risk} → "
        f"{optimized['optimized_hotspot_risk']}, with {temp_reduction} °C "
        "estimated temperature reduction."
    )

else:
    st.warning("Optimization engine could not find a valid cooling configuration.")

st.divider()

st.subheader("🏢 Infrastructure Scenario Intelligence")

if selected_scenario == "Balanced AI Training Rack":
    st.success(
        "Nominal AI training workload detected. "
        "Infrastructure operating within stable thermal conditions."
    )

elif selected_scenario == "High-Density MI300X Cluster":
    st.warning(
        "High-density accelerated compute workload detected. "
        "Thermal stress increasing due to elevated rack power density."
    )

elif selected_scenario == "Cooling Loop Degradation":
    st.error(
        "Cooling degradation scenario detected. "
        "Flow instability and reduced cooling efficiency may trigger hotspot formation."
    )

elif selected_scenario == "Emergency Thermal Event":
    st.error(
        "Critical infrastructure thermal event detected. "
        "Immediate cooling intervention recommended to prevent hardware damage."
    )

st.caption("Scenario-driven infrastructure simulation for AI data center thermal analysis.")

st.divider()

st.subheader("🧪 Physics Model Comparison")

baseline_error = round(abs(outlet_temp - surrogate_prediction), 2)

st.write("Comparison between the thermal simulation engine and the surrogate prediction layer.")

p1, p2, p3 = st.columns(3)

with p1:
    st.metric("Simulation Engine", f"{outlet_temp} °C")

with p2:
    st.metric("Surrogate Model", f"{surrogate_prediction} °C")

with p3:
    st.metric("Model Difference", f"{baseline_error} °C")

if baseline_error < 2:
    st.success("Surrogate model is closely aligned with the physics simulation.")
elif baseline_error < 5:
    st.info("Surrogate model shows moderate deviation from the physics simulation.")
else:
    st.warning("Surrogate model deviation is high. Future PINN training can reduce this gap.")

st.divider()

m1, m2, m3, m4 = st.columns(4)

gpu_utilization = min(100, round((heat_load_kw / 300) * 100))
cooling_pressure = round(flow_rate * 0.42, 2)
pue_estimate = round(1.1 + ((100 - estimated_efficiency) / 100), 2)

with m1:
    st.metric("Estimated Rack Power", f"{heat_load_kw} kW")

with m2:
    st.metric("GPU Utilization", f"{gpu_utilization}%")

with m3:
    st.metric("Cooling Loop Pressure", f"{cooling_pressure} bar")

with m4:
    st.metric("Estimated PUE", f"{pue_estimate}")

st.divider()

left, right = st.columns([1.2, 1])

with left:
    st.subheader("🌡️ Thermal Field Simulation")

    x = np.linspace(0, 1, 100)
    y = np.linspace(0, 1, 100)
    X, Y = np.meshgrid(x, y)

    time_factor = st.slider("Simulation Time Step", 0.0, 1.0, 0.5)

    base_temp = inlet_temp
    thermal_gradient = outlet_temp - inlet_temp

    dynamic_hotspot = 8 * np.exp(
        -(
            (X - (0.55 + 0.25 * time_factor)) ** 2
            + (Y - 0.5) ** 2
        )
        / 0.015
    )

    Z_dynamic = base_temp + thermal_gradient * X + dynamic_hotspot

    fig, ax = plt.subplots(figsize=(8, 5))

    heatmap = ax.contourf(
        X,
        Y,
        Z_dynamic,
        levels=35,
    )

    plt.colorbar(heatmap, ax=ax, label="Temperature °C")

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
        st.success("Thermal operating conditions appear stable for sustained AI workloads.")

st.divider()

st.subheader("👁️ Multimodal Thermal Image Analysis")

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    annotated_image, detections = draw_hotspot_overlay(
    image,
    hotspot_risk,
    risk_score,
)

    img1, img2 = st.columns(2)

    with img1:
        st.image(
            image,
            caption="Original thermal / infrastructure image",
            use_container_width=True,
        )

    with img2:
        st.image(
            annotated_image,
            caption="AI hotspot overlay",
            use_container_width=True,
        )
    
    st.subheader("🔎 Vision Detection Results")

    for detection in detections:
        st.write(
            f"• {detection['label']} | "
            f"Severity: {detection['severity']} | "
            f"Confidence: {round(detection['confidence'] * 100)}%"
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

st.subheader("📡 Live Infrastructure Event Stream")

if hotspot_risk == "HIGH":
    events = [
        "WARNING • Hotspot threshold exceeded",
        "ALERT • Cooling efficiency degradation detected",
        "ACTION • AI recommendation engine triggered",
        "INFO • Thermal propagation increasing near rack boundary",
    ]
else:
    events = [
        "INFO • Thermal conditions stable",
        "INFO • Cooling network operating normally",
        "INFO • AI monitoring active",
        "INFO • No critical infrastructure anomalies detected",
    ]

events.extend(
    [
        f"METRIC • GPU utilization at {gpu_utilization}%",
        f"METRIC • Estimated rack power at {heat_load_kw} kW",
        f"METRIC • Cooling loop pressure at {cooling_pressure} bar",
    ]
)

for event in events:
    st.code(event)

st.divider()

st.subheader("📈 Thermal Anomaly Trend")

time_steps = np.arange(1, 21)

thermal_trend = (
    inlet_temp
    + (outlet_temp - inlet_temp) * (time_steps / 20)
    + 2 * np.sin(time_steps / 2)
)

fig_trend, ax_trend = plt.subplots(figsize=(8, 3))

ax_trend.plot(time_steps, thermal_trend, marker="o")
ax_trend.axhline(30, linestyle="--", label="Hotspot threshold")
ax_trend.set_title("Predicted Thermal Risk Evolution")
ax_trend.set_xlabel("Time Step")
ax_trend.set_ylabel("Temperature °C")
ax_trend.legend()

st.pyplot(fig_trend)

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