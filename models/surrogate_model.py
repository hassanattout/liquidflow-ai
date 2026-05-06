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

    thermal_response = (
        inlet_temp
        + (heat_load_kw / (flow_rate * cooling_efficiency))
        + 0.02 * np.sqrt(heat_load_kw)
    )

    return round(thermal_response, 2)