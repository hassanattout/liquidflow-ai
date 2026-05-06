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