# test_water_norm.py
import pytest
from water_norm import calculate_water_norm

# ===== ПОЗИТИВНЫЕ =====

def test_normal_case():
    result = calculate_water_norm(70, 60)
    expected = 30 * 70 + (500 * 60) / 60
    assert result == expected

def test_min_weight_min_activity():
    result = calculate_water_norm(5, 0)
    assert result == 150.0

def test_max_weight_max_activity():
    result = calculate_water_norm(250, 720)
    assert result == 7500.0 + 6000.0

def test_30min():
    result = calculate_water_norm(45, 30)
    assert result == 1600

# ===== НЕГАТИВНЫЕ =====

def test_unnorm_case():
    with pytest.raises(ValueError, match="Вес должен быть от 5 до 250 кг"):
        calculate_water_norm(4, 30)

def test_weight_too_high():
    with pytest.raises(ValueError, match="Вес должен быть от 5 до 250 кг"):
        calculate_water_norm(251, 30)

def test_negative_activity():
    with pytest.raises(ValueError, match="Время активности не может быть отрицательным"):
        calculate_water_norm(70, -10)

def test_activity_too_high():
    with pytest.raises(ValueError, match="Время активности не может превышать 720 минут"):
        calculate_water_norm(70, 721)

# ===== ГРАНИЦЫ =====

def test_boundary_weight_min():
    result = calculate_water_norm(5, 60)
    expected = 150.0 + 500.0
    assert result == expected

def test_boundary_weight_max():
    result = calculate_water_norm(250, 60)
    expected = 7500.0 + 500.0
    assert result == expected

def test_boundary_activity_min():
    result = calculate_water_norm(70, 0)
    assert result == 2100.0

def test_boundary_activity_max():
    result = calculate_water_norm(70, 720)
    expected = 2100.0 + 6000.0
    assert result == expected

def test_zero_weight():
    with pytest.raises(ValueError):
        calculate_water_norm(0, 30)

def test_negative_weight():
    with pytest.raises(ValueError):
        calculate_water_norm(-10, 60)