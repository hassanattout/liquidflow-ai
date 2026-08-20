import numpy as np


WATER_DENSITY_KG_PER_L = 0.997
WATER_HEAT_CAPACITY_J_PER_KG_K = 4182.0


def _require_finite(name: str, value: float) -> float:
    value = float(value)
    if not np.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def thermal(flow_rate, inlet_temp, heat_load_kw, cooling_efficiency):
    """
    Estimate coolant outlet temperature with a steady-state energy balance.

    ``flow_rate`` is water flow in L/min and ``heat_load_kw`` is heat transferred
    to the coolant in kW. The calculation uses Q = m_dot * cp * delta_T.
    """
    flow_rate = _require_finite("flow_rate", flow_rate)
    inlet_temp = _require_finite("inlet_temp", inlet_temp)
    heat_load_kw = _require_finite("heat_load_kw", heat_load_kw)
    cooling_efficiency = _require_finite("cooling_efficiency", cooling_efficiency)

    if flow_rate <= 0:
        raise ValueError("flow_rate must be greater than 0 L/min")
    if not 5 <= inlet_temp <= 35:
        raise ValueError("inlet_temp must be between 5 and 35 °C")
    if heat_load_kw <= 0:
        raise ValueError("heat_load_kw must be greater than 0 kW")
    if not 0 < cooling_efficiency <= 1:
        raise ValueError("cooling_efficiency must be in (0, 1]")

    mass_flow_kg_s = flow_rate * WATER_DENSITY_KG_PER_L / 60.0
    heat_load_w = heat_load_kw * 1000.0
    delta_temp = heat_load_w / (
        mass_flow_kg_s
        * WATER_HEAT_CAPACITY_J_PER_KG_K
        * cooling_efficiency
    )
    outlet_temp = inlet_temp + delta_temp

    return round(float(outlet_temp), 2)


def optimize_cooling(
    flow_rate: float,
    inlet_temp: float,
    heat_load_kw: float,
    cooling_efficiency: float,
) -> dict:
    """Search bounded operating points using the shared thermal model."""
    current_outlet = thermal(
        flow_rate, inlet_temp, heat_load_kw, cooling_efficiency
    )
    best_result = None

    flow_options = np.linspace(flow_rate, min(flow_rate * 2.0, 1000.0), 20)
    inlet_options = np.linspace(max(inlet_temp - 8.0, 5.0), inlet_temp, 10)
    efficiency_options = np.linspace(
        cooling_efficiency, min(cooling_efficiency + 0.15, 1.0), 10
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
                candidate_risk = classify_hotspot(candidate_outlet)
                candidate_score = calculate_risk_score(candidate_outlet)

                relative_flow_change = abs(candidate_flow - flow_rate) / flow_rate
                inlet_change = abs(candidate_inlet - inlet_temp)
                efficiency_change = abs(candidate_efficiency - cooling_efficiency)
                penalty = (
                    relative_flow_change * 3.0
                    + inlet_change * 0.8
                    + efficiency_change * 20.0
                )
                objective = candidate_outlet + penalty

                result = {
                    "optimized_flow_rate": round(float(candidate_flow), 2),
                    "optimized_inlet_temp": round(float(candidate_inlet), 2),
                    "optimized_cooling_efficiency": round(float(candidate_efficiency), 3),
                    "optimized_outlet_temp": round(float(candidate_outlet), 2),
                    "optimized_hotspot_risk": candidate_risk,
                    "optimized_risk_score": candidate_score,
                    "objective_score": round(float(objective), 4),
                }
                if best_result is None or objective < best_result["objective_score"]:
                    best_result = result

    best_result["temperature_reduction_c"] = round(
        current_outlet - best_result["optimized_outlet_temp"], 2
    )
    return best_result


def classify_hotspot(outlet_temp: float) -> str:
    if outlet_temp >= 42:
        return "CRITICAL"
    if outlet_temp >= 32:
        return "HIGH"
    if outlet_temp >= 27:
        return "WARNING"
    return "LOW"


def calculate_risk_score(outlet_temp: float) -> int:
    return min(100, max(0, round(((outlet_temp - 20) / 30) * 100)))


def generate_rack_cluster(
    n_rows: int = 3,
    n_cols: int = 4,
    base_heat_load_kw: float = 140.0,
    base_flow_rate: float = 200.0,
    inlet_temp: float = 20.0,
    cooling_efficiency: float = 0.82,
    hotspot_row: int = 1,
    hotspot_col: int = 2,
    hotspot_intensity: float = 1.65,
    degradation_factor: float = 0.0,
) -> list[dict]:
    """
    Generate a synthetic multi-rack AI cluster.

    Each rack has local heat load, flow rate, cooling efficiency, and spatial position.
    A controlled hotspot is injected to simulate high-density GPU concentration.
    """
    racks = []

    for row in range(n_rows):
        for col in range(n_cols):
            distance_to_hotspot = np.sqrt((row - hotspot_row) ** 2 + (col - hotspot_col) ** 2)
            hotspot_effect = hotspot_intensity * np.exp(-(distance_to_hotspot ** 2) / 1.4)

            load_variation = 1.0 + 0.08 * np.sin(row + col)
            heat_load = base_heat_load_kw * load_variation * (1.0 + hotspot_effect * 0.35)

            local_flow = base_flow_rate * (1.0 - degradation_factor * 0.25)
            local_efficiency = cooling_efficiency * (1.0 - degradation_factor * 0.20)

            outlet = thermal(local_flow, inlet_temp, heat_load, local_efficiency)

            racks.append(
                {
                    "rack_id": f"R{row + 1}-{col + 1}",
                    "row": row,
                    "col": col,
                    "heat_load_kw": round(float(heat_load), 2),
                    "flow_rate": round(float(local_flow), 2),
                    "inlet_temp": round(float(inlet_temp), 2),
                    "cooling_efficiency": round(float(local_efficiency), 3),
                    "outlet_temp": outlet,
                    "risk_score": calculate_risk_score(outlet),
                    "hotspot_risk": classify_hotspot(outlet),
                }
            )

    return racks


def apply_neighbor_heat_propagation(
    racks: list[dict],
    n_rows: int,
    n_cols: int,
    propagation_strength: float = 0.12,
) -> list[dict]:
    """
    Propagate heat from hotter racks to neighboring racks.

    This creates system behavior instead of isolated rack calculations.
    """
    rack_map = {(rack["row"], rack["col"]): rack for rack in racks}
    updated = []

    for rack in racks:
        neighbor_delta = 0.0
        row, col = rack["row"], rack["col"]

        neighbors = [
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1),
        ]

        for n_row, n_col in neighbors:
            neighbor = rack_map.get((n_row, n_col))
            if neighbor is None:
                continue

            temp_gap = max(0.0, neighbor["outlet_temp"] - rack["outlet_temp"])
            neighbor_delta += temp_gap * propagation_strength

        propagated_temp = round(float(rack["outlet_temp"] + neighbor_delta), 2)

        updated_rack = dict(rack)
        updated_rack["propagated_outlet_temp"] = propagated_temp
        updated_rack["propagated_risk_score"] = calculate_risk_score(propagated_temp)
        updated_rack["propagated_hotspot_risk"] = classify_hotspot(propagated_temp)

        updated.append(updated_rack)

    return updated


def cluster_summary(racks: list[dict]) -> dict:
    temps = np.array([rack["propagated_outlet_temp"] for rack in racks])
    heat_loads = np.array([rack["heat_load_kw"] for rack in racks])
    risk_scores = np.array([rack["propagated_risk_score"] for rack in racks])

    critical_racks = [
        rack["rack_id"]
        for rack in racks
        if rack["propagated_hotspot_risk"] in ["HIGH", "CRITICAL"]
    ]

    return {
        "rack_count": len(racks),
        "total_heat_load_kw": round(float(heat_loads.sum()), 2),
        "average_outlet_temp_c": round(float(temps.mean()), 2),
        "max_outlet_temp_c": round(float(temps.max()), 2),
        "average_risk_score": round(float(risk_scores.mean()), 1),
        "critical_rack_count": len(critical_racks),
        "critical_racks": critical_racks,
        "cluster_status": "CRITICAL" if len(critical_racks) >= 3 else "WATCH" if len(critical_racks) > 0 else "STABLE",
    }


def forecast_cluster_temperature(
    current_max_temp: float,
    cooling_efficiency: float,
    heat_load_kw: float,
    steps: int = 24,
) -> list[dict]:
    """
    Lightweight thermal drift forecast.

    Models heat accumulation under sustained workload and cooling degradation.
    """
    forecast = []

    for step in range(1, steps + 1):
        workload_pressure = (heat_load_kw / 300.0) * 0.18 * step
        cooling_drift = (1.0 - cooling_efficiency) * 0.22 * step
        periodic_variation = 0.8 * np.sin(step / 3)

        predicted_temp = current_max_temp + workload_pressure + cooling_drift + periodic_variation

        forecast.append(
            {
                "time_step": step,
                "predicted_max_temp_c": round(float(predicted_temp), 2),
                "risk_score": calculate_risk_score(predicted_temp),
                "risk_class": classify_hotspot(predicted_temp),
            }
        )

    return forecast


def get_cluster_recommendations(summary: dict) -> list[str]:
    status = summary["cluster_status"]

    if status == "CRITICAL":
        return [
            "Trigger emergency cooling intervention for critical racks",
            "Increase coolant flow in the affected rack row",
            "Redistribute workload away from high-risk racks",
            "Inspect cold plate contact and cooling loop pressure",
            "Reduce local rack power density until temperatures stabilize",
        ]

    if status == "WATCH":
        return [
            "Increase monitoring frequency for warning racks",
            "Pre-emptively raise coolant flow by 10-15%",
            "Balance workload across lower-temperature racks",
            "Check for early-stage cooling degradation",
        ]

    return [
        "Maintain current cooling configuration",
        "Continue telemetry monitoring",
        "No immediate intervention required",
    ]
