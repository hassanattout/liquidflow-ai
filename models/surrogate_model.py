import numpy as np


def surrogate_temperature_prediction(
    flow_rate,
    inlet_temp,
    heat_load_kw,
    cooling_efficiency,
):
    """
    Lightweight surrogate thermal prediction model.

    Placeholder for future PINN / neural surrogate integration.
    """
    if flow_rate * cooling_efficiency <= 0:
        return None

    thermal_response = (
        inlet_temp
        + (heat_load_kw / (flow_rate * cooling_efficiency))
        + 0.02 * np.sqrt(heat_load_kw)
    )

    return round(float(thermal_response), 2)


def surrogate_cluster_risk_prediction(racks: list[dict]) -> dict:
    """
    Simple surrogate layer for cluster-level risk estimation.
    """
    temps = np.array([rack["propagated_outlet_temp"] for rack in racks])
    heat_loads = np.array([rack["heat_load_kw"] for rack in racks])

    thermal_variance = float(np.var(temps))
    density_factor = float(np.mean(heat_loads) / 300.0)
    max_temp = float(np.max(temps))

    risk_probability = min(
        0.99,
        max(
            0.01,
            0.015 * max_temp + 0.20 * density_factor + 0.01 * thermal_variance,
        ),
    )

    return {
        "cluster_hotspot_probability": round(risk_probability, 3),
        "thermal_variance": round(thermal_variance, 3),
        "risk_driver": "temperature_concentration" if thermal_variance > 12 else "sustained_heat_load",
    }
