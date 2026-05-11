# 💧 LiquidFlow AI

### Thermal Intelligence Layer for High-Density AI Infrastructure

LiquidFlow AI is a physics-informed thermal intelligence platform for liquid-cooled GPU clusters and next-generation AI data centers.

The platform combines thermal simulation, multi-rack propagation modeling, surrogate risk estimation, cooling optimization, infrastructure telemetry visualization, and operator recommendations.

It is designed as an early prototype of an AI infrastructure intelligence layer: a system that helps operators understand, forecast, and optimize thermal behavior in high-density compute environments.

---

## Live Demo

### Streamlit Dashboard

https://liquiflow-ai.streamlit.app

---

## Core Thesis

AI infrastructure is becoming physically constrained.

As GPU clusters scale, performance is no longer limited only by model architecture or software efficiency. It is increasingly constrained by:

- rack power density
- liquid cooling capacity
- heat propagation across infrastructure zones
- thermal reliability
- energy efficiency
- operational response time

Traditional CFD simulations are powerful but often too heavy for real-time operational monitoring.

LiquidFlow AI explores a lightweight alternative:

> physics-informed simulation + surrogate prediction + infrastructure optimization.

---

## Current Capabilities

### Thermal Intelligence Engine

- Single-rack liquid cooling simulation
- Multi-rack thermal network modeling
- Rack-to-rack heat propagation
- Thermal risk scoring
- Cooling margin estimation
- Cluster-level thermal status

### Infrastructure Optimization

- Cooling parameter optimization
- Flow rate recommendation
- Cooling efficiency adjustment
- Rack risk classification
- Workload redistribution recommendations

### Forecasting

- Thermal drift forecast
- Future hotspot risk estimation
- Peak temperature prediction
- Escalation detection under sustained workload

### Multimodal Inspection Workflow

- Rack or thermal image upload
- Hotspot overlay
- Detection confidence scoring
- Infrastructure inspection simulation

### API Layer

FastAPI endpoints include:

- `/simulate`
- `/optimize`
- `/cluster-status`
- `/rack/{rack_id}`
- `/thermal-forecast`
- `/energy-optimization`
- `/recommend`
- `/health`

---

## Infrastructure Scenarios

LiquidFlow AI includes multiple operating scenarios:

- Balanced AI Training Rack
- High-Density MI300X Cluster
- Cooling Loop Degradation
- Emergency Thermal Event

Each scenario changes heat load, coolant flow, cooling efficiency, degradation factor, and cluster-level thermal behavior.

---

## System Architecture

```text
User Input / Infrastructure Scenario
        ↓
Streamlit Dashboard + FastAPI API
        ↓
Thermal Simulation Engine
        ↓
Multi-Rack Propagation Model
        ↓
Surrogate Risk Prediction
        ↓
Thermal Forecasting Layer
        ↓
Cooling Optimization Engine
        ↓
AI Infrastructure Recommendations
        ↓
Operator Decision Support
```

---

## Tech Stack

### Core

- Python
- Streamlit
- FastAPI
- NumPy
- Pandas
- Matplotlib
- Pillow

### AI / Simulation

- Physics-informed thermal logic
- Surrogate risk prediction
- Multi-rack propagation model
- Forecasting heuristics
- PINN-ready architecture

### Infrastructure Roadmap

- GPU telemetry ingestion
- ROCm acceleration
- AMD Instinct GPU support
- Qwen-VL or Llama Vision integration
- Workload-aware thermal optimization
- Energy-aware compute orchestration

---

## Run Locally

### Clone Repository

```bash
git clone https://github.com/hassanattout/liquidflow-ai.git
cd liquidflow-ai
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run FastAPI Backend

```bash
python3 -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

### Run Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

---

## Example API Calls

### Single Rack Simulation

```bash
curl "http://127.0.0.1:8000/simulate?flow_rate=12&inlet_temp=20&heat_load_kw=150&cooling_efficiency=0.82"
```

### Cluster Status

```bash
curl "http://127.0.0.1:8000/cluster-status?base_heat_load_kw=180&degradation_factor=0.4"
```

### Thermal Forecast

```bash
curl "http://127.0.0.1:8000/thermal-forecast?current_max_temp=34&cooling_efficiency=0.75&heat_load_kw=220"
```

---

## Why This Matters

AI infrastructure is becoming an energy and thermal systems problem.

LiquidFlow AI explores how physically grounded software can support:

- infrastructure reliability
- cooling optimization
- GPU cluster operations
- data center energy efficiency
- thermal risk forecasting
- operator decision support

The long-term vision is an AI infrastructure operating layer that connects telemetry, thermal simulation, workload orchestration, and energy optimization.

---

## Current Prototype Status

LiquidFlow AI is a functional prototype.

Current version includes deterministic thermal simulation, multi-rack propagation, surrogate risk estimation, forecasting heuristics, API endpoints, and a Streamlit dashboard.

Future versions can integrate real telemetry, CFD-calibrated models, neural surrogates, PINNs, and GPU-accelerated inference.

---

## Roadmap

### Near Term

- Improve multi-rack thermal physics
- Add real telemetry schema
- Add workload scheduling logic
- Improve dashboard UI polish
- Add architecture diagrams and demo video

### Medium Term

- Train neural surrogate model
- Add PINN-based thermal field prediction
- Add GPU telemetry ingestion
- Integrate external inference endpoint
- Deploy stronger API backend

### Long Term

- Workload-aware thermal orchestration
- Energy-aware AI cluster optimization
- Cooling loop control recommendations
- Data center digital twin
- AI infrastructure operating system
