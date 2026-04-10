"""
AgroCure - Weather API Integration
Fetches weather context to improve disease risk predictions
"""

import os
import httpx
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
#
# TODO: Set env var OPENWEATHER_API_KEY with your OpenWeatherMap key
# Get a free key at: https://openweathermap.org/api
# ─────────────────────────────────────────────────────────────────────────────

OPENWEATHER_BASE = "https://api.openweathermap.org/data/2.5"


async def get_weather(lat: float, lon: float) -> Optional[dict]:
    """
    Fetches current weather for given coordinates.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        dict with weather context or None on failure
    """
    api_key = os.getenv("bd5e378503939ddaee76f12ad7a97608")
    if not api_key:
        # Return mock data for development / if no key set
        return _mock_weather()

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{OPENWEATHER_BASE}/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": api_key,
                    "units": "metric",
                },
            )
            resp.raise_for_status()
            data = resp.json()

            return _parse_weather(data)

    except Exception as e:
        print(f"[weather_api] Error: {e}")
        return None


def _parse_weather(data: dict) -> dict:
    """Parses OpenWeatherMap response into clean weather context."""
    main = data.get("main", {})
    weather = data.get("weather", [{}])[0]
    wind = data.get("wind", {})
    rain = data.get("rain", {})

    temperature = main.get("temp", 0)
    humidity = main.get("humidity", 0)
    rainfall_1h = rain.get("1h", 0)

    # Disease risk hints from weather
    disease_risk_hint = _assess_disease_risk_from_weather(temperature, humidity, rainfall_1h)

    return {
        "temperature_c": round(temperature, 1),
        "humidity_pct": humidity,
        "description": weather.get("description", "").title(),
        "rainfall_mm_1h": rainfall_1h,
        "wind_speed_ms": wind.get("speed", 0),
        "city": data.get("name", "Unknown"),
        "disease_risk_hint": disease_risk_hint,
    }


def _assess_disease_risk_from_weather(
    temperature: float,
    humidity: float,
    rainfall: float,
) -> dict:
    """
    Contextual disease risk based on weather conditions.
    Used to enhance model prediction context.
    """
    risks = []
    risk_level = "LOW"

    if humidity > 70:
        risks.append("High humidity increases fungal disease risk (blight, rust, mold)")
        risk_level = "MEDIUM"

    if humidity > 85:
        risks.append("Very high humidity — Late Blight outbreak conditions")
        risk_level = "HIGH"

    if 15 <= temperature <= 25 and humidity > 60:
        risks.append("Cool + humid conditions = ideal for Phytophthora (Late Blight)")
        risk_level = "HIGH"

    if rainfall > 5:
        risks.append("Recent rainfall — avoid spraying, monitor for splash-borne infections")
        if risk_level == "LOW":
            risk_level = "MEDIUM"

    if temperature > 35:
        risks.append("High temperature may stress crops; heat-tolerant diseases more active")

    return {
        "risk_level": risk_level,
        "factors": risks if risks else ["Weather conditions are favorable for crops"],
    }


def _mock_weather() -> dict:
    """Returns mock weather data when no API key is set (dev mode)."""
    return {
        "temperature_c": 28.5,
        "humidity_pct": 72,
        "description": "Partly Cloudy",
        "rainfall_mm_1h": 0,
        "wind_speed_ms": 3.2,
        "city": "Demo Mode",
        "disease_risk_hint": {
            "risk_level": "MEDIUM",
            "factors": [
                "Mock data — set OPENWEATHER_API_KEY for real weather",
                "High humidity increases fungal disease risk (blight, rust, mold)",
            ],
        },
    }
