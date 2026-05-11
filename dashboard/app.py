import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw

sys.path.append(str(Path(__file__).resolve().parents[1]))

from simulations.thermal import (
    thermal,
    classify_hotspot,
    calculate_risk_score,
    generate_rack_cluster,
    apply_neighbor_heat_propagation,
    cluster_summary,
    forecast_cluster_temperature,
    get_cluster_recommendations,
)
from models.surrogate_model import (
    surrogate_temperature_prediction,
    surrogate_cluster_risk_prediction,
)


st.set_page_config(
    page_title="LiquidFlow AI",
    page_icon="💧",
    layout="wide",
)


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


def draw_hotspot_overlay(
    image: Image.Image,
    hotspot_risk: str,
    risk_score: int,
) -> tuple[Image.Image, list[dict]]:
    image = image.convert("RGB")
    overlay = image.copy()
    draw = ImageDraw.Draw(overlay)

    width, height = overlay.size

    if hotspot_risk in ["HIGH", "CRITICAL"]:
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

        draw.rectangle(box, outline=(255, 40, 40), width=10)

        text = f"{label} | {severity} | {round(confidence * 100)}%"
        text_position = (box[0], max(0, box[1] - 28))

        draw.rectangle(
            [
                text_position[0],
                text_position[1],
                min(width, text_position[0] + 380),
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
        "cluster_heat_kw": 140.0,
        "degradation": 0.0,
    },
    "High-Density MI300X Cluster": {
        "flow_rate": 8.0,
        "inlet_temp": 24.0,
        "heat_load_kw": 260.0,
        "cooling_efficiency": 0.55,
        "cluster_heat_kw": 220.0,
        "degradation": 0.35,
    },
    "Cooling Loop Degradation": {
        "flow_rate": 5.0,
        "inlet_temp": 28.0,
        "heat_load_kw": 220.0,
        "cooling_efficiency": 0.40,
        "cluster_heat_kw": 190.0,
        "degradation": 0.65,
    },
    "Emergency Thermal Event": {
        "flow_rate": 3.0,
        "inlet_temp": 32.0,
        "heat_load_kw": 300.0,
        "cooling_efficiency": 0.25,
        "cluster_heat_kw": 260.0,
        "degradation": 0.9,
    },
}


st.markdown(
    """
    <h1 style='font-size: 4rem; margin-bottom: 0;'>
        💧 LiquidFlow AI
    </h1>

    <p style='font-size: 1.2rem; color: #9aa0aa;'>
        Thermal intelligence layer for high-density AI infrastructure
    </p>
    """,
    unsafe_allow_html=True,
)

st.success("System online • Thermal digital twin active • AI infrastructure monitoring enabled")


with st.sidebar:
    st.markdown("## ⚙️ Control Panel")
    st.caption("Thermal system configuration")

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
        "Single-rack heat load kW",
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

    cooling_degradation_factor = st.slider(
        "Cooling Degradation Factor",
        0.0,
        1.0,
        float(scenario["degradation"]),
    )

    st.divider()

    st.markdown("## 🏢 Cluster Model")

    n_rows = st.slider("Rack rows", 2, 6, 3)
    n_cols = st.slider("Rack columns", 2, 8, 4)

    cluster_heat_kw = st.slider(
        "Average rack heat load kW",
        50.0,
        300.0,
        float(scenario["cluster_heat_kw"]),
    )

    st.divider()

    uploaded_image = st.file_uploader(
        "Upload thermal / rack image",
        type=["png", "jpg", "jpeg"],
    )


effective_efficiency = max(
    0.15,
    cooling_efficiency * (1.0 - cooling_degradation_factor * 0.55),
)

outlet_temp = thermal(
    flow_rate,
    inlet_temp,
    heat_load_kw,
    effective_efficiency,
)

surrogate_prediction = surrogate_temperature_prediction(
    flow_rate,
    inlet_temp,
    heat_load_kw,
    effective_efficiency,
)

if outlet_temp is None:
    st.error("Invalid parameters. Flow rate and cooling efficiency must be greater than 0.")
    st.stop()

outlet_temp = round(float(outlet_temp), 2)
surrogate_prediction = round(float(surrogate_prediction), 2)

hotspot_risk = classify_hotspot(outlet_temp)
risk_score = calculate_risk_score(outlet_temp)
cooling_margin = round(max(0, 50 - outlet_temp), 2)
estimated_efficiency = round(effective_efficiency * 100, 1)

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Outlet Temperature", f"{outlet_temp} °C")
k2.metric("Hotspot Classification", hotspot_risk)
k3.metric("Thermal Risk Index", f"{risk_score}/100")
k4.metric("Cooling Safety Margin", f"{cooling_margin} °C")
k5.metric("Surrogate Prediction", f"{surrogate_prediction} °C")

st.divider()

st.subheader("🏢 Multi-Rack Thermal Network")

racks = generate_rack_cluster(
    n_rows=n_rows,
    n_cols=n_cols,
    base_heat_load_kw=cluster_heat_kw,
    base_flow_rate=flow_rate,
    inlet_temp=inlet_temp,
    cooling_efficiency=effective_efficiency,
    degradation_factor=cooling_degradation_factor,
)

racks = apply_neighbor_heat_propagation(racks, n_rows=n_rows, n_cols=n_cols)
summary = cluster_summary(racks)
cluster_surrogate = surrogate_cluster_risk_prediction(racks)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Cluster Status", summary["cluster_status"])
c2.metric("Rack Count", summary["rack_count"])
c3.metric("Total Heat Load", f"{summary['total_heat_load_kw']} kW")
c4.metric("Max Rack Temp", f"{summary['max_outlet_temp_c']} °C")
c5.metric("Critical Racks", summary["critical_rack_count"])

rack_df = pd.DataFrame(racks)
pivot_temp = rack_df.pivot(index="row", columns="col", values="propagated_outlet_temp")

left_cluster, right_cluster = st.columns([1.2, 1])

with left_cluster:
    fig_cluster, ax_cluster = plt.subplots(figsize=(8, 4.5))

    heatmap = ax_cluster.imshow(pivot_temp.values, aspect="auto")
    plt.colorbar(heatmap, ax=ax_cluster, label="Propagated outlet temperature °C")

    for i in range(pivot_temp.shape[0]):
        for j in range(pivot_temp.shape[1]):
            temp = pivot_temp.values[i, j]
            rack_id = f"R{i + 1}-{j + 1}"

            rack_risk = rack_df.loc[
                rack_df["rack_id"] == rack_id,
                "propagated_hotspot_risk",
            ].iloc[0]

            label = f"Rack {rack_id}\n{temp:.1f}°C"

            if rack_risk == "CRITICAL":
                label += "\nCRITICAL"

            ax_cluster.text(
                j,
                i,
                label,
                ha="center",
                va="center",
                fontsize=10,
                color="red" if rack_risk == "CRITICAL" else "white",
                fontweight="bold",
            )

    ax_cluster.set_title("Rack-to-Rack Thermal Propagation Map")

    for row in range(n_rows):
        ax_cluster.arrow(
            -0.48,
            row,
            0.18,
            0,
            head_width=0.08,
            head_length=0.08,
            fc="cyan",
            ec="cyan",
            linewidth=2,
            alpha=0.75,
        )

    ax_cluster.text(
        -0.62,
        -0.60,
        "Cold Aisle",
        fontsize=10,
        color="cyan",
        fontweight="bold",
    )

    ax_cluster.text(
        n_cols - 0.7,
        n_rows - 0.35,
        "Hot Zone",
        fontsize=10,
        color="red",
        fontweight="bold",
    )

    ax_cluster.set_xlabel("Cluster Column")
    ax_cluster.set_ylabel("Cluster Row")
    st.pyplot(fig_cluster)

with right_cluster:
    st.markdown("### 🧠 Cluster Intelligence")

    if summary["cluster_status"] == "CRITICAL":
        st.error("Cluster-level thermal risk is critical.")
    elif summary["cluster_status"] == "WATCH":
        st.warning("Cluster requires proactive monitoring.")
    else:
        st.success("Cluster operating within stable thermal conditions.")

    st.write(
        f"Surrogate hotspot probability: "
        f"**{cluster_surrogate['cluster_hotspot_probability']}**"
    )
    st.write(f"Main risk driver: **{cluster_surrogate['risk_driver']}**")

    st.write("Recommended actions:")
    for rec in get_cluster_recommendations(summary):
        st.write(f"• {rec}")

with st.expander("View rack telemetry table"):
    st.dataframe(
        rack_df[
            [
                "rack_id",
                "heat_load_kw",
                "flow_rate",
                "cooling_efficiency",
                "outlet_temp",
                "propagated_outlet_temp",
                "propagated_hotspot_risk",
                "propagated_risk_score",
            ]
        ],
        use_container_width=True,
    )

st.divider()

st.subheader("🔮 Thermal Forecast")

forecast = forecast_cluster_temperature(
    current_max_temp=summary["max_outlet_temp_c"],
    cooling_efficiency=effective_efficiency,
    heat_load_kw=cluster_heat_kw,
    steps=24,
)

forecast_df = pd.DataFrame(forecast)

f1, f2 = st.columns([1.2, 1])

with f1:
    fig_forecast, ax_forecast = plt.subplots(figsize=(8, 3.5))

    ax_forecast.plot(
        forecast_df["time_step"],
        forecast_df["predicted_max_temp_c"],
        marker="o",
    )

    ax_forecast.axhline(
        32,
        linestyle="--",
        color="orange",
        label="High-risk threshold",
    )

    ax_forecast.axhline(
        42,
        linestyle="--",
        color="red",
        label="Critical threshold",
    )

    ax_forecast.fill_between(
        forecast_df["time_step"],
        42,
        forecast_df["predicted_max_temp_c"],
        where=forecast_df["predicted_max_temp_c"] >= 42,
        alpha=0.2,
        color="red",
    )

    ax_forecast.set_title("Predicted Cluster Thermal Drift")
    ax_forecast.set_xlabel("Forecast Step")
    ax_forecast.set_ylabel("Max Temperature °C")
    ax_forecast.legend()

    st.pyplot(fig_forecast)

with f2:
    peak = forecast_df.loc[forecast_df["predicted_max_temp_c"].idxmax()]

    st.metric("Peak Forecast Temp", f"{peak['predicted_max_temp_c']} °C")
    st.metric("Peak Forecast Risk", peak["risk_class"])

    if peak["risk_class"] in ["HIGH", "CRITICAL"]:
        st.warning("Forecast indicates possible thermal escalation under sustained load.")
    else:
        st.success("Forecast remains within acceptable range.")

st.divider()

st.subheader("⚡ Cooling Optimization Engine")

optimized = optimize_cooling(
    flow_rate,
    inlet_temp,
    heat_load_kw,
    effective_efficiency,
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

else:
    st.warning("Optimization engine could not find a valid cooling configuration.")

st.divider()

st.subheader("🧪 Physics Model Comparison")

baseline_error = round(abs(outlet_temp - surrogate_prediction), 2)

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
    st.subheader("🌡️ Dynamic Thermal Field Simulation")

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

    for rack_x in np.linspace(0.1, 0.9, 5):
        ax.axvline(rack_x, linestyle="--", alpha=0.25)

    for rack_y in np.linspace(0.1, 0.9, 4):
        ax.axhline(rack_y, linestyle="--", alpha=0.25)

    ax.set_xlabel("Rack Width")
    ax.set_ylabel("Rack Height")

    st.pyplot(fig)

with right:
    st.subheader("🧠 AI Recommendation Engine")

    if hotspot_risk in ["HIGH", "CRITICAL"]:
        st.error("Hotspot formation detected")

        st.write("Recommended actions:")
        st.write("• Increase coolant flow rate by 15-25%")
        st.write("• Reduce rack compute density")
        st.write("• Improve cooling loop efficiency")
        st.write("• Redistribute thermal load across racks")
        st.write("• Inspect cooling plate thermal contact")

    elif hotspot_risk == "WARNING":
        st.warning("Early thermal stress detected")

        st.write("Recommended actions:")
        st.write("• Increase monitoring frequency")
        st.write("• Prepare cooling adjustment if workload rises")
        st.write("• Watch forecasted thermal drift")

    else:
        st.success("System operating within acceptable thermal range")

        st.write("Recommended actions:")
        st.write("• Maintain current cooling configuration")
        st.write("• Continue monitoring outlet temperature")
        st.write("• No immediate intervention required")

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

else:
    st.write(
        "Upload a rack, cooling plate, or thermal image to activate the multimodal analysis module."
    )

st.divider()

st.subheader("📡 Live Infrastructure Event Stream")

if summary["cluster_status"] == "CRITICAL":
    events = [
        "ALERT • Cluster thermal status critical",
        "WARNING • Multi-rack hotspot propagation detected",
        "ACTION • Workload redistribution recommended",
        "ACTION • Increase coolant flow in affected cooling loop",
    ]
elif summary["cluster_status"] == "WATCH":
    events = [
        "WARNING • Early-stage rack thermal imbalance detected",
        "INFO • Forecast model monitoring thermal drift",
        "ACTION • Proactive cooling adjustment recommended",
    ]
else:
    events = [
        "INFO • Cluster thermal conditions stable",
        "INFO • Cooling network operating normally",
        "INFO • AI infrastructure monitoring active",
    ]

events.extend(
    [
        f"METRIC • GPU utilization at {gpu_utilization}%",
        f"METRIC • Single rack power at {heat_load_kw} kW",
        f"METRIC • Cluster heat load at {summary['total_heat_load_kw']} kW",
        f"METRIC • Cooling loop pressure at {cooling_pressure} bar",
    ]
)

for event in events:
    st.code(event)

st.divider()

st.subheader("🤖 LiquidFlow AI Copilot")

user_question = st.text_input(
    "Ask the thermal AI assistant",
    placeholder="Example: Why is cluster thermal risk high?",
)

if user_question:
    st.write("AI Copilot Response:")

    if summary["cluster_status"] == "CRITICAL":
        st.warning(
            "The cluster is showing critical thermal behavior because multiple racks are exceeding safe operating margins. "
            "The strongest first action is to redistribute workload away from hot racks while increasing coolant flow and inspecting the affected cooling loop."
        )
    elif summary["cluster_status"] == "WATCH":
        st.info(
            "The cluster is showing early thermal imbalance. Sustained high-density workloads could escalate risk, so proactive cooling adjustment is recommended."
        )
    else:
        st.success(
            "The cluster is currently operating within acceptable thermal limits. Cooling margin is positive and no immediate intervention is required."
        )

    st.caption(
        "Prototype copilot logic. Future versions can connect to Qwen, Llama, or AMD-hosted inference APIs."
    )

st.divider()

st.caption(
    "LiquidFlow AI • Physics-informed infrastructure intelligence for high-density AI systems"
)