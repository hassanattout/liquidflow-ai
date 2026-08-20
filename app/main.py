from fastapi import FastAPI, HTTPException, Query

from simulations.thermal import (
    thermal,
    optimize_cooling,
    classify_hotspot,
    calculate_risk_score,
    generate_rack_cluster,
    apply_neighbor_heat_propagation,
    cluster_summary,
    forecast_cluster_temperature,
    get_cluster_recommendations,
)
from models.surrogate_model import (
    heuristic_temperature_prediction,
    heuristic_cluster_risk_prediction,
)


app = FastAPI(
    title="LiquidFlow AI",
    description="Physics-based thermal intelligence prototype for high-density AI infrastructure.",
    version="0.2.0",
)


def get_recommendations(hotspot_risk: str) -> list[str]:
    if hotspot_risk in ["HIGH", "CRITICAL"]:
        return [
            "Increase coolant flow rate by 15-25%",
            "Reduce rack compute density",
            "Improve cooling loop efficiency",
            "Redistribute thermal load across racks",
            "Inspect cooling plate thermal contact",
        ]

    if hotspot_risk == "WARNING":
        return [
            "Increase monitoring frequency",
            "Prepare cooling adjustment if workload increases",
            "Check cooling margin during sustained training workloads",
        ]

    return [
        "Maintain current cooling configuration",
        "Continue monitoring outlet temperature",
        "No immediate intervention required",
    ]


@app.get("/")
def home():
    return {
        "project": "LiquidFlow AI",
        "status": "running",
        "version": "0.2.0",
        "description": "Thermal digital twin for AI infrastructure cooling.",
        "docs": "/docs",
        "health": "/health",
        "simulate": "/simulate",
        "optimize": "/optimize",
        "cluster_status": "/cluster-status",
        "thermal_forecast": "/thermal-forecast",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "LiquidFlow AI API",
    }


@app.get("/simulate")
def simulate(
    flow_rate: float = Query(200.0, gt=0, le=1000, description="Coolant flow rate in L/min"),
    inlet_temp: float = Query(20.0, ge=5, le=35, description="Inlet temperature in °C"),
    heat_load_kw: float = Query(100.0, gt=0, le=500, description="Rack heat load in kW"),
    cooling_efficiency: float = Query(
        0.85,
        ge=0.1,
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

    heuristic_prediction = heuristic_temperature_prediction(
        flow_rate,
        inlet_temp,
        heat_load_kw,
        cooling_efficiency,
    )

    outlet_temp = round(float(outlet_temp), 2)
    heuristic_prediction = round(float(heuristic_prediction), 2)

    hotspot_risk = classify_hotspot(outlet_temp)
    risk_score = calculate_risk_score(outlet_temp)
    cooling_margin = round(max(0, 50 - outlet_temp), 2)
    model_difference = round(abs(outlet_temp - heuristic_prediction), 2)

    estimated_efficiency = round(cooling_efficiency * 100, 1)
    gpu_utilization = min(100, round((heat_load_kw / 300) * 100))
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
            "heuristic_prediction": heuristic_prediction,
            "model_difference": model_difference,
            "hotspot_risk": hotspot_risk,
            "thermal_risk_score": risk_score,
            "cooling_margin": cooling_margin,
        },
        "infrastructure_metrics": {
            "estimated_efficiency_percent": estimated_efficiency,
            "synthetic_load_proxy_percent": gpu_utilization,
            "estimated_pue_proxy": pue_estimate,
        },
        "recommendations": get_recommendations(hotspot_risk),
    }


@app.get("/recommend")
def recommend(
    outlet_temp: float = Query(32.0, ge=5, le=100, description="Predicted outlet temperature in °C"),
):
    hotspot_risk = classify_hotspot(outlet_temp)

    return {
        "outlet_temp": outlet_temp,
        "hotspot_risk": hotspot_risk,
        "recommendations": get_recommendations(hotspot_risk),
    }


@app.get("/optimize")
def optimize(
    flow_rate: float = Query(200.0, gt=0, le=1000, description="Current coolant flow rate in L/min"),
    inlet_temp: float = Query(20.0, ge=5, le=35, description="Current inlet temperature in °C"),
    heat_load_kw: float = Query(100.0, gt=0, le=500, description="Current rack heat load in kW"),
    cooling_efficiency: float = Query(
        0.85,
        ge=0.1,
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
            "risk_transition": f"{current_risk} -> {optimized['optimized_hotspot_risk']}",
        },
    }


@app.get("/cluster-status")
def cluster_status(
    n_rows: int = Query(3, ge=2, le=6),
    n_cols: int = Query(4, ge=2, le=8),
    base_heat_load_kw: float = Query(140.0, gt=10, le=500),
    base_flow_rate: float = Query(200.0, gt=0, le=1000),
    inlet_temp: float = Query(20.0, ge=5, le=35),
    cooling_efficiency: float = Query(0.82, ge=0.1, le=1),
    degradation_factor: float = Query(0.0, ge=0, le=1),
):
    racks = generate_rack_cluster(
        n_rows=n_rows,
        n_cols=n_cols,
        base_heat_load_kw=base_heat_load_kw,
        base_flow_rate=base_flow_rate,
        inlet_temp=inlet_temp,
        cooling_efficiency=cooling_efficiency,
        degradation_factor=degradation_factor,
    )

    propagated = apply_neighbor_heat_propagation(racks, n_rows=n_rows, n_cols=n_cols)
    summary = cluster_summary(propagated)
    heuristic_risk = heuristic_cluster_risk_prediction(propagated)

    return {
        "status": "success",
        "project": "LiquidFlow AI",
        "cluster_summary": summary,
        "heuristic_cluster_risk": heuristic_risk,
        "recommendations": get_cluster_recommendations(summary),
        "racks": propagated,
    }


@app.get("/rack/{rack_id}")
def rack_detail(
    rack_id: str,
    n_rows: int = Query(3, ge=2, le=6),
    n_cols: int = Query(4, ge=2, le=8),
    base_heat_load_kw: float = Query(140.0, gt=10, le=500),
    base_flow_rate: float = Query(200.0, gt=0, le=1000),
    inlet_temp: float = Query(20.0, ge=5, le=35),
    cooling_efficiency: float = Query(0.82, ge=0.1, le=1),
    degradation_factor: float = Query(0.0, ge=0, le=1),
):
    racks = generate_rack_cluster(
        n_rows=n_rows,
        n_cols=n_cols,
        base_heat_load_kw=base_heat_load_kw,
        base_flow_rate=base_flow_rate,
        inlet_temp=inlet_temp,
        cooling_efficiency=cooling_efficiency,
        degradation_factor=degradation_factor,
    )
    propagated = apply_neighbor_heat_propagation(racks, n_rows=n_rows, n_cols=n_cols)

    for rack in propagated:
        if rack["rack_id"].lower() == rack_id.lower():
            return {
                "status": "success",
                "rack": rack,
                "recommendations": get_recommendations(rack["propagated_hotspot_risk"]),
            }

    raise HTTPException(status_code=404, detail=f"Rack {rack_id} not found")


@app.get("/thermal-forecast")
def thermal_forecast(
    current_max_temp: float = Query(32.0, ge=5, le=100),
    cooling_efficiency: float = Query(0.82, ge=0.1, le=1),
    heat_load_kw: float = Query(180.0, gt=10, le=500),
    steps: int = Query(24, ge=4, le=96),
):
    forecast = forecast_cluster_temperature(
        current_max_temp=current_max_temp,
        cooling_efficiency=cooling_efficiency,
        heat_load_kw=heat_load_kw,
        steps=steps,
    )

    peak = max(forecast, key=lambda item: item["predicted_max_temp_c"])

    return {
        "status": "success",
        "project": "LiquidFlow AI",
        "forecast_horizon_steps": steps,
        "peak_forecast": peak,
        "forecast": forecast,
    }


@app.get("/energy-optimization")
def energy_optimization(
    total_heat_load_kw: float = Query(1200.0, gt=100),
    cooling_efficiency: float = Query(0.82, gt=0, le=1),
    utilization_percent: float = Query(75.0, ge=0, le=100),
):
    estimated_it_power_kw = total_heat_load_kw
    cooling_overhead_kw = total_heat_load_kw * (1.0 - cooling_efficiency)
    facility_power_kw = estimated_it_power_kw + cooling_overhead_kw
    pue = round(facility_power_kw / estimated_it_power_kw, 3)

    potential_savings_kw = round(cooling_overhead_kw * 0.18, 2)

    return {
        "status": "success",
        "estimated_it_power_kw": round(estimated_it_power_kw, 2),
        "cooling_overhead_kw": round(cooling_overhead_kw, 2),
        "facility_power_kw": round(facility_power_kw, 2),
        "estimated_pue": pue,
        "potential_cooling_savings_kw": potential_savings_kw,
        "recommendations": [
            "Shift flexible workloads toward cooler racks",
            "Increase cooling efficiency before raising facility power draw",
            "Prioritize thermal balancing over uniform utilization",
            "Monitor PUE drift during sustained high-utilization periods",
        ],
    }
