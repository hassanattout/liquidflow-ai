import pytest

from simulations.thermal import (
    apply_neighbor_heat_propagation,
    generate_rack_cluster,
    optimize_cooling,
    thermal,
)


def test_thermal_uses_water_energy_balance():
    result = thermal(200.0, 20.0, 100.0, 0.85)
    assert result == pytest.approx(28.47, abs=0.02)


@pytest.mark.parametrize(
    "args",
    [
        (0, 20, 100, 0.85),
        (200, 2, 100, 0.85),
        (200, 20, 0, 0.85),
        (200, 20, 100, 0),
    ],
)
def test_thermal_rejects_invalid_operating_points(args):
    with pytest.raises(ValueError):
        thermal(*args)


def test_more_flow_reduces_outlet_temperature():
    low_flow = thermal(100, 20, 100, 0.85)
    high_flow = thermal(250, 20, 100, 0.85)
    assert high_flow < low_flow


def test_optimization_uses_shared_model_and_reduces_temperature():
    result = optimize_cooling(150, 24, 180, 0.7)
    assert result["optimized_outlet_temp"] < thermal(150, 24, 180, 0.7)
    assert result["temperature_reduction_c"] > 0


def test_cluster_propagation_preserves_rack_count():
    racks = generate_rack_cluster(n_rows=2, n_cols=3)
    propagated = apply_neighbor_heat_propagation(racks, n_rows=2, n_cols=3)
    assert len(propagated) == 6
    assert all("propagated_outlet_temp" in rack for rack in propagated)
