import numpy as np
from fastapi import FastAPI, Query

from simulations.thermal import thermal
from models.surrogate_model import surrogate_temperature_prediction


app = FastAPI(
    title="LiquidFlow AI",
    description="Physics-informed thermal intelligence API for high-density AI infrastructure.",
    version="0.1.0",
)


def classify_hotspot(outlet_temp: float) -> str:
    return "HIGH" if outlet_temp > 30 else "LOW"


def calculate_risk_score(outlet_temp: float) -> int:
    return min(100, max(0, round(((outlet_temp - 20) / 30) * 100)))


def get_recommendations(hotspot_risk: str) -> list[str]:
    if hotspot_risk == "HIGH":
        return [
            "Increase coolant flow rate by 15-25%",
            "Reduce rack compute density",
            "Improve cooling loop efficiency",
            "Redistribute thermal load across racks",
            "Inspect cooling plate thermal contact",
        ]

    return [
        "Maintain current cooling configuration",
        "Continue monitoring outlet temperature",
        "No immediate intervention required",
    ]

def optimize_cooling(
    flow_rate: float,
    inlet_temp: float,
    heat_load_kw: float,
    cooling_efficiency: float,
) -> dict:
    best_result = None

    flow_options = np.linspace(flow_rate, min(flow_rate * 2.0, 50), 20)
    inlet_options = np.linspace(max(inlet_temp - 8, 5), inlet_temp, 10)
    efficiency_options = np.linspace(cooling_efficiency, min(cooling_efficiency + 0.15, 1.0), 10)

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

@app.get("/")
def home():
    return {
        "project": "LiquidFlow AI",
        "status": "running",
        "description": "Thermal digital twin for AI infrastructure cooling.",
        "docs": "/docs",
        "health": "/health",
        "simulate": "/simulate",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "LiquidFlow AI API",
    }


@app.get("/simulate")
def simulate(
    flow_rate: float = Query(12.0, gt=0, description="Coolant flow rate"),
    inlet_temp: float = Query(20.0, description="Inlet temperature in °C"),
    heat_load_kw: float = Query(100.0, gt=0, description="Rack heat load in kW"),
    cooling_efficiency: float = Query(
        0.85,
        gt=0,
        le=1,
        description="Cooling efficiency from 0 to 1",
    ),
):
    outlet_temp = thermal(
        flow_rate,
        inlet_temp,
        heat_load_kw,
        cooling_efficiency,
    )

    if outlet_temp is None:
        return {
            "status": "error",
            "message": "flow_rate * cooling_efficiency must be greater than 0",
        }

    surrogate_prediction = surrogate_temperature_prediction(
        flow_rate,
        inlet_temp,
        heat_load_kw,
        cooling_efficiency,
    )

    outlet_temp = round(float(outlet_temp), 2)
    surrogate_prediction = round(float(surrogate_prediction), 2)

    hotspot_risk = classify_hotspot(outlet_temp)
    risk_score = calculate_risk_score(outlet_temp)
    cooling_margin = round(max(0, 50 - outlet_temp), 2)
    model_difference = round(abs(outlet_temp - surrogate_prediction), 2)

    estimated_efficiency = round(cooling_efficiency * 100, 1)
    gpu_utilization = min(100, round((heat_load_kw / 300) * 100))
    cooling_pressure = round(flow_rate * 0.42, 2)
    pue_estimate = round(1.1 + ((100 - estimated_efficiency) / 100), 2)

    return {
        "status": "success",
        "project": "LiquidFlow AI",
        "inputs": {
            "flow_rate": flow_rate,
            "inlet_temp": inlet_temp,
            "heat_load_kw": heat_load_kw,
            "cooling_efficiency": cooling_efficiency,
        },
        "results": {
            "outlet_temp": outlet_temp,
            "surrogate_prediction": surrogate_prediction,
            "model_difference": model_difference,
            "hotspot_risk": hotspot_risk,
            "thermal_risk_score": risk_score,
            "cooling_margin": cooling_margin,
        },
        "infrastructure_metrics": {
            "estimated_efficiency_percent": estimated_efficiency,
            "estimated_gpu_utilization_percent": gpu_utilization,
            "cooling_loop_pressure_bar": cooling_pressure,
            "estimated_pue": pue_estimate,
        },
        "recommendations": get_recommendations(hotspot_risk),
    }


@app.get("/recommend")
def recommend(
    outlet_temp: float = Query(32.0, description="Predicted outlet temperature in °C"),
):
    hotspot_risk = classify_hotspot(outlet_temp)

    return {
        "outlet_temp": outlet_temp,
        "hotspot_risk": hotspot_risk,
        "recommendations": get_recommendations(hotspot_risk),
    }


@app.get("/optimize")
def optimize(
    flow_rate: float = Query(12.0, gt=0, description="Current coolant flow rate"),
    inlet_temp: float = Query(20.0, description="Current inlet temperature in °C"),
    heat_load_kw: float = Query(100.0, gt=0, description="Current rack heat load in kW"),
    cooling_efficiency: float = Query(
        0.85,
        gt=0,
        le=1,
        description="Current cooling efficiency from 0 to 1",
    ),
):
    current_outlet = thermal(
        flow_rate,
        inlet_temp,
        heat_load_kw,
        cooling_efficiency,
    )

    if current_outlet is None:
        return {
            "status": "error",
            "message": "Invalid cooling parameters.",
        }

    current_outlet = round(float(current_outlet), 2)
    current_risk = classify_hotspot(current_outlet)
    current_score = calculate_risk_score(current_outlet)

    optimized = optimize_cooling(
        flow_rate,
        inlet_temp,
        heat_load_kw,
        cooling_efficiency,
    )

    temp_reduction = round(
        current_outlet - optimized["optimized_outlet_temp"],
        2,
    )

    risk_reduction = current_score - optimized["optimized_risk_score"]

    return {
        "status": "success",
        "project": "LiquidFlow AI",
        "current_state": {
            "flow_rate": flow_rate,
            "inlet_temp": inlet_temp,
            "heat_load_kw": heat_load_kw,
            "cooling_efficiency": cooling_efficiency,
            "outlet_temp": current_outlet,
            "hotspot_risk": current_risk,
            "thermal_risk_score": current_score,
        },
        "optimized_state": optimized,
        "improvement": {
            "temperature_reduction_c": temp_reduction,
            "risk_score_reduction": risk_reduction,
            "risk_transition": f"{current_risk} → {optimized['optimized_hotspot_risk']}",
        },
    }