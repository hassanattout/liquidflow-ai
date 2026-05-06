from fastapi import FastAPI
from simulations.thermal import thermal

app = FastAPI(title="LiquidFlow AI")

@app.get("/")
def home():
    return {
        "project": "LiquidFlow AI",
        "status": "running"
    }

@app.get("/simulate")
def simulate(
    flow_rate: float,
    inlet_temp: float,
    heat_load_kw: float,
    cooling_efficiency: float
):

    outlet_temp = thermal(
        flow_rate,
        inlet_temp,
        heat_load_kw,
        cooling_efficiency
    )

    if outlet_temp is None:
        return {
            "error": "invalid parameters"
        }

    hotspot_risk = "HIGH" if outlet_temp > 30 else "LOW"

    return {
        "flow_rate": flow_rate,
        "inlet_temp": inlet_temp,
        "heat_load_kw": heat_load_kw,
        "cooling_efficiency": cooling_efficiency,
        "outlet_temp": outlet_temp,
        "hotspot_risk": hotspot_risk
    }