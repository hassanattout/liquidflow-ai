import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_simulate_returns_physical_and_honestly_labeled_results():
    response = client.get(
        "/simulate",
        params={
            "flow_rate": 200,
            "inlet_temp": 20,
            "heat_load_kw": 100,
            "cooling_efficiency": 0.85,
        },
    )
    assert response.status_code == 200
    results = response.json()["results"]
    assert results["outlet_temp"] == pytest.approx(28.46, abs=0.02)
    assert "heuristic_prediction" in results
    assert "surrogate_prediction" not in results


def test_api_rejects_out_of_range_inputs():
    response = client.get("/simulate", params={"inlet_temp": -50})
    assert response.status_code == 422


def test_missing_rack_returns_404():
    response = client.get("/rack/not-a-rack")
    assert response.status_code == 404
