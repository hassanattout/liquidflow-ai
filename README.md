# LiquidFlow AI

Physics-informed thermal intelligence for high-density AI infrastructure.

LiquidFlow AI simulates liquid cooling behavior, predicts hotspot risk, visualizes thermal fields, and provides AI-assisted recommendations for next-generation GPU racks and AI data centers.

## Features

- Thermal simulation API with FastAPI
- Streamlit dashboard
- Hotspot risk detection
- Thermal risk scoring
- Cooling margin estimation
- AI recommendation engine
- Thermal image upload module
- Designed for AMD Developer Hackathon

## Run API

```bash
uvicorn app.main:app --reload
```

## Open

```text
http://127.0.0.1:8000/docs
```

## Run Dashboard

```bash
streamlit run dashboard/app.py
```

## Project Vision

AI infrastructure is becoming increasingly power-dense. Liquid cooling is essential, but difficult to monitor and optimize in real time.  

LiquidFlow AI acts as a thermal digital twin for AI infrastructure, helping operators predict hotspots, evaluate cooling efficiency, and make better infrastructure decisions.

## System Architecture

```text
User Input
    ↓
Streamlit Dashboard
    ↓
FastAPI Backend
    ↓
Thermal Simulation Engine
    ↓
Hotspot Detection + Risk Scoring
    ↓
AI Recommendation Engine
    ↓
Thermal Visualization Layer
    ↓
Future Multimodal Vision Analysis
```

## Demo Preview

<img src="screenshots/dashboard-high-risk-demo.png" width="900"/>

## Why AMD

LiquidFlow AI is designed for high-performance AI infrastructure workloads and aligns naturally with AMD GPU acceleration and ROCm-based compute environments.

Potential AMD acceleration pathways include:

- Physics-informed neural network (PINN) training on AMD Instinct GPUs
- High-throughput thermal simulation workloads
- Multimodal vision inference using ROCm-compatible models
- GPU-accelerated infrastructure optimization
- Real-time AI inference for thermal digital twins

The project is being developed as part of the AMD Developer Hackathon using AMD Developer Cloud resources.

## Future Roadmap

- Real PINN integration for PDE-constrained thermal prediction
- Qwen-VL or Llama Vision integration
- GPU telemetry ingestion
- Real-time rack monitoring
- Distributed cooling optimization
- AI infrastructure copilot
- Multi-rack thermal orchestration
- Deployment on AMD GPU infrastructure