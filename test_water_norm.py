# test_water_norm.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from water_norm import calculate_water_norm
from weather_service import WeatherService

@pytest.fixture
def event_loop():
    """Фикстура для asyncio event loop"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_normal_case():
    result = await calculate_water_norm(70, 60)
    expected = 30 * 70 + (500 * 60) / 60
    assert result == expected


@pytest.mark.asyncio
async def test_min_weight_min_activity():
    result = await calculate_water_norm(5, 0)
    assert result == 150.0


@pytest.mark.asyncio
async def test_max_weight_max_activity():
    result = await calculate_water_norm(250, 720)
    assert result == 7500.0 + 6000.0


@pytest.mark.asyncio
async def test_30min():
    result = await calculate_water_norm(45, 30)
    assert result == 1600


# НЕГАТИВНЫЕ (тоже async)

@pytest.mark.asyncio
async def test_unnorm_case():
    with pytest.raises(ValueError, match="Вес должен быть от 5 до 250 кг"):
        await calculate_water_norm(4, 30)


@pytest.mark.asyncio
async def test_weight_too_high():
    with pytest.raises(ValueError, match="Вес должен быть от 5 до 250 кг"):
        await calculate_water_norm(251, 30)


@pytest.mark.asyncio
async def test_negative_activity():
    with pytest.raises(ValueError, match="Время активности не может быть отрицательным"):
        await calculate_water_norm(70, -10)


@pytest.mark.asyncio
async def test_activity_too_high():
    with pytest.raises(ValueError, match="Время активности не может превышать 720 минут"):
        await calculate_water_norm(70, 721)


# ГРАНИЦЫ

@pytest.mark.asyncio
async def test_boundary_weight_min():
    result = await calculate_water_norm(5, 60)
    expected = 150.0 + 500.0
    assert result == expected


@pytest.mark.asyncio
async def test_boundary_weight_max():
    result = await calculate_water_norm(250, 60)
    expected = 7500.0 + 500.0
    assert result == expected


@pytest.mark.asyncio
async def test_boundary_activity_min():
    result = await calculate_water_norm(70, 0)
    assert result == 2100.0


@pytest.mark.asyncio
async def test_boundary_activity_max():
    result = await calculate_water_norm(70, 720)
    expected = 2100.0 + 6000.0
    assert result == expected


@pytest.mark.asyncio
async def test_zero_weight():
    with pytest.raises(ValueError):
        await calculate_water_norm(0, 30)


@pytest.mark.asyncio
async def test_negative_weight():
    with pytest.raises(ValueError):
        await calculate_water_norm(-10, 60)


@pytest.mark.asyncio
async def test_with_mock_object():
    """Тест с AsyncMock - ПРАВИЛЬНО"""
    # 1. Создаем AsyncMock для метода
    fake_weather_service = AsyncMock(spec=WeatherService)

    # 2. НАСТРАИВАЕМ return_value для метода
    fake_weather_service.get_temperature_async.return_value = 40

    # 3. Вызываем с await
    result = await calculate_water_norm(70, 60, fake_weather_service)

    # 4. Проверяем
    assert result == 3120.0
    # Используем assert_awaited_once() для async методов
    fake_weather_service.get_temperature_async.assert_awaited_once()


@pytest.mark.asyncio
async def test_extreme_heat():
    """Экстремальная жара - ПРАВИЛЬНО"""
    fake_service = AsyncMock()
    # Важно: настраиваем метод get_temperature
    fake_service.get_temperature_async.return_value = 40  # Температура 40

    result = await calculate_water_norm(70, 60, fake_service)
    assert result == 3120.0


@pytest.mark.asyncio
async def test_normal_temperature():
    """Нормальная температура - ПРАВИЛЬНО"""
    fake_service = AsyncMock()
    fake_service.get_temperature_async.return_value = 20  # Температура 20

    result = await calculate_water_norm(70, 60, fake_service)
    assert result == 2600.0


# ===== ПАРАМЕТРИЗОВАННЫЙ ТЕСТ =====

@pytest.mark.asyncio
@pytest.mark.parametrize("temp,expected", [
    (29, 2600.0),  # 29°C - без изменений
    (30, 2600.0),  # 30°C - без изменений
    (31, 3120.0),  # 31°C - +20%
    (40, 3120.0),  # 40°C - +20%
])
async def test_temperature_logic(temp, expected):
    fake_service = AsyncMock()
    fake_service.get_temperature_async.return_value = temp  # Устанавливаем температуру

    result = await calculate_water_norm(70, 60, fake_service)
    assert result == expected


# ===== SPY ТЕСТ (исправленный) =====

@pytest.mark.asyncio
async def test_spy_on_weather_service():
    """Spy - проверяем вызовы"""
    # Создаем реальный сервис
    real_service = WeatherService()

    # Патчим метод get_temperature
    with patch.object(real_service, 'get_temperature_async', AsyncMock()) as spy_method:
        # Настраиваем spy
        spy_method.return_value = 35

        # Вызываем
        result = await calculate_water_norm(70, 60, real_service)

        # Проверяем - для AsyncMock используем assert_awaited_once
        spy_method.assert_awaited_once()
        assert result == 3120.0


# ===== РАЗНЫЕ ОТВЕТЫ =====

@pytest.mark.asyncio
async def test_mock_different_responses():
    """Разные ответы от сервиса"""
    mock_service = AsyncMock()

    # Тест 1: Успешный ответ 40°C
    mock_service.get_temperature_async.return_value = 40
    result1 = await calculate_water_norm(70, 60, mock_service)
    assert result1 == 3120.0

    # Тест 2: Успешный ответ 20°C (нужно сбросить)
    mock_service.get_temperature_async.return_value = 20
    result2 = await calculate_water_norm(70, 60, mock_service)
    assert result2 == 2600.0

    # Тест 3: Ошибка
    mock_service.get_temperature_async.side_effect = ValueError("Сервис недоступен")
    with pytest.raises(ValueError, match="Сервис недоступен"):
        await calculate_water_norm(70, 60, mock_service)


# ===== ВЕРИФИКАЦИЯ =====

@pytest.mark.asyncio
async def test_verification_calls():
    """Верификация вызовов"""
    mock_service = AsyncMock()
    mock_service.get_temperature_async.return_value = 25

    # Вызываем два раза
    await calculate_water_norm(70, 60, mock_service)
    await calculate_water_norm(80, 90, mock_service)

    # Проверяем что вызвали 2 раза
    assert mock_service.get_temperature_async.await_count == 2
    mock_service.get_temperature_async.assert_awaited()


# ===== ЗАДЕРЖКА =====

@pytest.mark.asyncio
async def test_weather_service_delay():
    """Задержка ответа"""

    async def delayed_response():
        await asyncio.sleep(0.05)
        return 30

    mock_service = AsyncMock()
    mock_service.get_temperature_async.side_effect = delayed_response

    result = await calculate_water_norm(70, 60, mock_service)
    assert result == 2600.0  # 30°C = без изменений


# ===== НЕСКОЛЬКО ВЫЗОВОВ =====

@pytest.mark.asyncio
async def test_multiple_concurrent_calls():
    """Несколько одновременных вызовов"""
    mock_service = AsyncMock()
    mock_service.get_temperature_async.return_value = 35

    # Создаем задачи
    task1 = calculate_water_norm(70, 60, mock_service)
    task2 = calculate_water_norm(80, 90, mock_service)
    task3 = calculate_water_norm(90, 120, mock_service)

    # Запускаем одновременно
    results = await asyncio.gather(task1, task2, task3)

    assert len(results) == 3
    assert results[0] == 3120.0  # 2600 * 1.2
    assert results[1] == 3780.0  # (2400 + 750) * 1.2 = 3150
    assert mock_service.get_temperature_async.await_count == 3
# УЛУЧШЕНИЕ ПОКРЫВАЕМОСТИ ДО 92%

def test_get_user_input_valid():
    """Тест корректного ввода пользователя"""
    with patch('builtins.input', side_effect=['70', '60']):
        from water_norm import get_user_input
        weight, activity = get_user_input()
        assert weight == 70.0
        assert activity == 60

def test_get_user_input_invalid_weight():
    """Тест некорректного ввода веса"""
    with patch('builtins.input', side_effect=['не число', '60']):
        from water_norm import get_user_input
        with pytest.raises(ValueError, match="Некорректный ввод данных"):
            get_user_input()

def test_get_user_input_invalid_activity():
    """Тест некорректного ввода активности"""
    with patch('builtins.input', side_effect=['70', 'не число']):
        from water_norm import get_user_input
        with pytest.raises(ValueError, match="Некорректный ввод данных"):
            get_user_input()

def test_get_user_input_float_weight():
    """Тест ввода веса с плавающей точкой"""
    with patch('builtins.input', side_effect=['70.5', '60']):
        from water_norm import get_user_input
        weight, activity = get_user_input()
        assert weight == 70.5
        assert activity == 60

def test_calculate_water_norm_sync():
    """Тест синхронной обертки"""
    with patch('asyncio.run') as mock_run:
        from water_norm import calculate_water_norm_sync
        mock_run.return_value = 2500.0
        result = calculate_water_norm_sync(70, 60)
        assert result == 2500.0
        mock_run.assert_called_once()

def test_main_success(capsys):
    """Тест успешного выполнения main"""
    with patch('builtins.input', side_effect=['70', '60']):
        with patch('water_norm.calculate_water_norm_sync', return_value=2450.0):
            from water_norm import main
            main()
            captured = capsys.readouterr()
            assert "Калькулятор нормы воды" in captured.out
            assert "дневная норма воды" in captured.out
            assert "2450" in captured.out
            assert "2.5 литров" in captured.out

def test_main_value_error(capsys):
    """Тест main с ошибкой ввода"""
    with patch('builtins.input', side_effect=['не число', '60']):
        from water_norm import main
        main()
        captured = capsys.readouterr()
        assert "Ошибка" in captured.out
        assert "Некорректный ввод данных" in captured.out

def test_main_keyboard_interrupt(capsys):
    """Тест прерывания программы"""
    with patch('builtins.input', side_effect=KeyboardInterrupt):
        from water_norm import main
        main()
        captured = capsys.readouterr()
        assert "Программа прервана" in captured.out

def test_main_extreme_values(capsys):
    """Тест main с крайними значениями"""
    with patch('builtins.input', side_effect=['5', '720']):
        with patch('water_norm.calculate_water_norm_sync', return_value=7650.0):
            from water_norm import main
            main()
            captured = capsys.readouterr()
            assert "дневная норма воды" in captured.out
            assert "7650" in captured.out
            assert "7.7 литров" in captured.out  # 7650/1000 = 7.65 → 7.7

def test_main_decimal_weight(capsys):
    """Тест main с десятичным весом"""
    with patch('builtins.input', side_effect=['70.5', '45']):
        with patch('water_norm.calculate_water_norm_sync', return_value=2362.5):
            from water_norm import main
            main()
            captured = capsys.readouterr()
            assert "дневная норма воды" in captured.out
            assert "2362.5" in captured.out
def test_module_can_be_imported():
    """Тест что модуль импортируется без ошибок"""
    import water_norm
    assert hasattr(water_norm, 'calculate_water_norm')
    assert hasattr(water_norm, 'calculate_water_norm_sync')
    assert hasattr(water_norm, 'get_user_input')
    assert hasattr(water_norm, 'main')

def test_calculate_water_norm_sync_propagates_exceptions():
    """Тест что синхронная обертка прокидывает исключения"""
    with patch('asyncio.run') as mock_run:
        from water_norm import calculate_water_norm_sync
        mock_run.side_effect = ValueError("Ошибка в асинхронном коде")
        with pytest.raises(ValueError, match="Ошибка в асинхронном коде"):
            calculate_water_norm_sync(70, 60)