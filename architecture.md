# LiquidFlow AI Architecture

## Strategic Positioning

LiquidFlow AI is a physics-based thermal intelligence prototype designed for high-density AI infrastructure and liquid-cooled GPU clusters.

The system explores how lightweight thermal modeling, infrastructure simulation, forecasting, and optimization can support operational decision-making inside next-generation AI compute environments.

Modern AI infrastructure is increasingly constrained by:
- rack power density
- cooling system limitations
- thermal reliability
- energy efficiency
- workload concentration

LiquidFlow AI models a simplified infrastructure intelligence stack composed of:

1. thermal simulation
2. multi-rack thermal propagation
3. transparent risk heuristics
4. cooling optimization
5. thermal forecasting
6. infrastructure recommendations

---

## Infrastructure Constraints Modeled

The current prototype models simplified forms of:

- rack-level thermal behavior
- hotspot formation
- rack-to-rack heat propagation
- cooling degradation
- thermal accumulation
- workload-induced thermal stress
- cluster-level risk escalation

The implementation is intentionally lightweight to support fast simulation, real-time visualization, and infrastructure prototyping workflows.

---

## Architecture Diagram

```text
                        ┌──────────────────────────┐
                        │  User / Operator Inputs  │
                        └─────────────┬────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │   Streamlit Dashboard    │
                        └─────────────┬────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │       FastAPI Layer      │
                        │                          │
                        │ /simulate                │
                        │ /cluster-status          │
                        │ /thermal-forecast        │
                        │ /energy-optimization     │
                        └─────────────┬────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │ Thermal Simulation Engine│
                        └─────────────┬────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │ Multi-Rack Propagation   │
                        └─────────────┬────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │ Heuristic Risk Layer     │
                        └─────────────┬────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │ Forecast + Optimization  │
                        └─────────────┬────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │ Operator Recommendations │
                        └──────────────────────────┘
```

---

## Core Modules

### 1. Thermal Simulation Engine

Location:

```text
simulations/thermal.py
```

Purpose:

- compute outlet temperature
- classify hotspot risk
- estimate thermal risk score
- generate multi-rack cluster state

---

### 2. Multi-Rack Propagation Model

Purpose:

- simulate rack-to-rack thermal influence
- create cluster-level thermal behavior
- detect multi-zone heat concentration

Key concept:

```text
rack temperature = local thermal response + neighbor heat influence
```

This makes the project feel like infrastructure software instead of a single-equation demo.

---

### 3. Heuristic Comparison Layer

Location:

```text
models/surrogate_model.py
```

Purpose:

- provide a deterministic comparison with the energy-balance model
- calculate an uncalibrated cluster hotspot score
- provide a placeholder path for a future trained surrogate or PINN

This layer is not a trained machine-learning model and its score is not a
calibrated probability.

---

### 4. Forecasting Layer

Purpose:

- predict future thermal drift
- detect possible escalation
- estimate peak temperature under sustained workload

---

### 5. Optimization Layer

Purpose:

- recommend improved coolant flow
- recommend cooling efficiency improvements
- estimate temperature reduction
- support operator action

---

### 6. API Layer

Location:

```text
app/main.py
```

Endpoints:

```text
/
 /health
 /simulate
 /recommend
 /optimize
 /cluster-status
 /rack/{rack_id}
 /thermal-forecast
 /energy-optimization
```

---

### 7. Dashboard Layer

Location:

```text
dashboard/app.py
```

Purpose:

- display infrastructure state
- visualize rack thermal map
- show forecast trends
- provide operator recommendations
- demonstrate a clearly labeled, scenario-driven image overlay

---

## Future Production Architecture

```text
GPU Telemetry
    ↓
Streaming Pipeline
    ↓
Thermal Digital Twin
    ↓
Neural Surrogate / PINN
    ↓
Cooling + Workload Optimizer
    ↓
Operator Console / API
    ↓
Data Center Control Layer
```

---

## Future Real-World Data Inputs

- GPU temperature
- rack inlet and outlet temperature
- coolant flow rate
- coolant pressure
- power draw
- workload utilization
- fan speed
- cooling plate efficiency
- facility PUE
- carbon intensity
- electricity price
