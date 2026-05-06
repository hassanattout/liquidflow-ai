from fastapi import FastAPI
from simulations.thermal import thermal
from models.surrogate_model import surrogate_temperature_prediction

app = FastAPI(
    title="LiquidFlow AI",
    description="Physics-informed thermal intelligence API for high-density AI infrastructure.",
    version="0.1.0",
)


@app.get("/")
def home():
    return {
        "project": "LiquidFlow AI",
        "status": "running",
        "description": "Thermal digital twin for AI infrastructure cooling.",
    }


@app.get("/simulate")
def simulate(
    flow_rate: float = 12.0,
    inlet_temp: float = 20.0,
    heat_load_kw: float = 100.0,
    cooling_efficiency: float = 0.85,
):
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
        return {"error": "flow_rate * cooling_efficiency must be greater than 0"}

    hotspot_risk = "HIGH" if outlet_temp > 30 else "LOW"
    risk_score = min(100, max(0, round(((outlet_temp - 20) / 30) * 100)))
    cooling_margin = round(max(0, 50 - outlet_temp), 2)

    if hotspot_risk == "HIGH":
        recommendations = [
            "Increase coolant flow rate by 15-25%",
            "Reduce rack compute density",
            "Improve cooling loop efficiency",
            "Redistribute thermal load across racks",
            "Inspect cooling plate thermal contact",
        ]
    else:
        recommendations = [
            "Maintain current cooling configuration",
            "Continue monitoring outlet temperature",
            "No immediate intervention required",
        ]

    return {
        "inputs": {
            "flow_rate": flow_rate,
            "inlet_temp": inlet_temp,
            "heat_load_kw": heat_load_kw,
            "cooling_efficiency": cooling_efficiency,
        },
        "results": {
            "outlet_temp": outlet_temp,
            "hotspot_risk": hotspot_risk,
            "thermal_risk_score": risk_score,
            "cooling_margin": cooling_margin,
            "surrogate_prediction": surrogate_prediction,
            "model_difference": round(abs(outlet_temp - surrogate_prediction), 2),
        },
        "recommendations": recommendations,
    }


@app.get("/health")
def health():
    return {"status": "healthy"}