import numpy as np

from simulations.thermal import thermal


def heuristic_temperature_prediction(
    flow_rate,
    inlet_temp,
    heat_load_kw,
    cooling_efficiency,
):
    """
    Deterministic comparison heuristic, not a trained ML model.
    """
    thermal_response = thermal(
        flow_rate, inlet_temp, heat_load_kw, cooling_efficiency
    ) + 0.02 * np.sqrt(heat_load_kw)

    return round(float(thermal_response), 2)


def heuristic_cluster_risk_prediction(racks: list[dict]) -> dict:
    """
    Deterministic cluster-risk heuristic, not a calibrated probability model.
    """
    temps = np.array([rack["propagated_outlet_temp"] for rack in racks])
    heat_loads = np.array([rack["heat_load_kw"] for rack in racks])

    thermal_variance = float(np.var(temps))
    density_factor = float(np.mean(heat_loads) / 300.0)
    max_temp = float(np.max(temps))

    risk_score = min(
        0.99,
        max(
            0.01,
            0.015 * max_temp + 0.20 * density_factor + 0.01 * thermal_variance,
        ),
    )

    return {
        "cluster_hotspot_score": round(risk_score, 3),
        "thermal_variance": round(thermal_variance, 3),
        "risk_driver": "temperature_concentration" if thermal_variance > 12 else "sustained_heat_load",
    }
