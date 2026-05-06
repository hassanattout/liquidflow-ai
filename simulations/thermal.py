def thermal(flow_rate, inlet_temp, heat_load_kw, cooling_efficiency):

    if flow_rate * cooling_efficiency <= 0:
        return None

    delta_temp = heat_load_kw / (flow_rate * cooling_efficiency)

    outlet_temp = inlet_temp + delta_temp

    return round(outlet_temp, 2)