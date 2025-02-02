import pytest
from BotWeather import get_weather

@pytest.mark.asyncio
async def test_fetch_data_success(mocker):
    # Мокируем requests.get
    mock_response_location = mocker.Mock()
    mock_response_location.status_code = 200
    mock_response_location.json.return_value = [{"Key": "Location_value"}]

    mock_response_weather = mocker.Mock()
    mock_response_weather.status_code = 200
    mock_response_weather.json.return_value = [{
        "Temperature": {
            "Metric": {
                "Value": 20
            }
        },
        "WeatherText": "Солнечно"
    }]

    mocker.patch('requests.get', side_effect=[mock_response_location, mock_response_weather])

    result = await get_weather("Chelyabinsk")

    assert result == "Температура: 20°C\nСостояние: Солнечно"

@pytest.mark.asyncio
async def test_fetch_data_not_found(mocker):
    # Мокируем requests.get
    mock_response = mocker.Mock()
    mock_response.status_code = 404

    mocker.patch('requests.get', return_value=mock_response)

    result = await get_weather("Chelyabinsk")

    assert result == "Не удалось получить данные о погоде."