"""Meteo-France component constants."""

from homeassistant.const import (
    SPEED_KILOMETERS_PER_HOUR,
    TEMP_CELSIUS,
    TIME_MINUTES,
    UNIT_PERCENTAGE,
)

DOMAIN = "meteo_france"
PLATFORMS = ["sensor", "weather"]
ATTRIBUTION = "Data provided by Météo-France"

CONF_CITY = "city"

ENTITY_NAME = "name"
ENTITY_UNIT = "unit"
ENTITY_ICON = "icon"
ENTITY_CLASS = "device_class"
ENTITY_ENABLE = "enable"
ENTITY_API_DATA_PATH = "data_path"

SENSOR_TYPES = {
    "sea_level": {
        ENTITY_NAME: "Sea level",
        ENTITY_UNIT: None,
        ENTITY_ICON: "mdi:waves",
        ENTITY_CLASS: None,
        ENTITY_ENABLE: False,
        ENTITY_API_DATA_PATH: "forecast:sea_level",
    },
    "rain_chance": {
        ENTITY_NAME: "Rain chance",
        ENTITY_UNIT: UNIT_PERCENTAGE,
        ENTITY_ICON: "mdi:weather-rainy",
        ENTITY_CLASS: None,
        ENTITY_ENABLE: True,
        ENTITY_API_DATA_PATH: "probability_forecast:rain:3h",
    },
    "snow_chance": {
        ENTITY_NAME: "Snow chance",
        ENTITY_UNIT: UNIT_PERCENTAGE,
        ENTITY_ICON: "mdi:weather-snowy",
        ENTITY_CLASS: None,
        ENTITY_ENABLE: False,
        ENTITY_API_DATA_PATH: "probability_forecast:snow:3h",
    },
    "freeze_chance": {
        ENTITY_NAME: "Freeze chance",
        ENTITY_UNIT: UNIT_PERCENTAGE,
        ENTITY_ICON: "mdi:snowflake",
        ENTITY_CLASS: None,
        ENTITY_ENABLE: True,
        ENTITY_API_DATA_PATH: "probability_forecast:freezing",
    },
    "thunder_chance": {
        ENTITY_NAME: "Thunder chance",
        ENTITY_UNIT: UNIT_PERCENTAGE,
        ENTITY_ICON: "mdi:weather-lightning",
        ENTITY_CLASS: None,
        ENTITY_ENABLE: True,
        ENTITY_API_DATA_PATH: "forecast:T:value",  # NOT_OK
    },
    "wind_speed": {
        ENTITY_NAME: "Wind Speed",
        ENTITY_UNIT: SPEED_KILOMETERS_PER_HOUR,
        ENTITY_ICON: "mdi:weather-windy",
        ENTITY_CLASS: None,
        ENTITY_ENABLE: False,
        ENTITY_API_DATA_PATH: "forecast:wind:speed",
    },
    "next_rain": {
        ENTITY_NAME: "Next rain",
        ENTITY_UNIT: TIME_MINUTES,
        ENTITY_ICON: "mdi:weather-rainy",
        ENTITY_CLASS: None,
        ENTITY_ENABLE: True,
        ENTITY_API_DATA_PATH: "forecast:T:value",  # NOT_OK
    },
    "temperature": {
        ENTITY_NAME: "Temperature",
        ENTITY_UNIT: TEMP_CELSIUS,
        ENTITY_ICON: "mdi:thermometer",
        ENTITY_CLASS: "temperature",
        ENTITY_ENABLE: False,
        ENTITY_API_DATA_PATH: "forecast:T:value",
    },
    "uv": {
        ENTITY_NAME: "UV",
        ENTITY_UNIT: None,
        ENTITY_ICON: "mdi:sunglasses",
        ENTITY_CLASS: None,
        ENTITY_ENABLE: True,
        ENTITY_API_DATA_PATH: "daily_forecast:uv",
    },
    "weather_alert": {
        ENTITY_NAME: "Weather Alert",
        ENTITY_UNIT: None,
        ENTITY_ICON: "mdi:weather-cloudy-alert",
        ENTITY_CLASS: None,
        ENTITY_ENABLE: True,
        ENTITY_API_DATA_PATH: "forecast:T:value",  # NOT_OK
    },
}

CONDITION_CLASSES = {
    "clear-night": ["Nuit Claire", "Nuit claire"],
    "cloudy": ["Très nuageux"],
    "fog": [
        "Brume ou bancs de brouillard",
        "Brume",
        "Brouillard",
        "Brouillard givrant",
    ],
    "hail": ["Risque de grêle"],
    "lightning": ["Risque d'orages", "Orages"],
    "lightning-rainy": ["Pluie orageuses", "Pluies orageuses", "Averses orageuses"],
    "partlycloudy": ["Ciel voilé", "Ciel voilé nuit", "Éclaircies", "Eclaircies"],
    "pouring": ["Pluie forte"],
    "rainy": [
        "Bruine / Pluie faible",
        "Bruine",
        "Pluie faible",
        "Pluies éparses / Rares averses",
        "Pluies éparses",
        "Rares averses",
        "Pluie / Averses",
        "Averses",
        "Pluie",
    ],
    "snowy": [
        "Neige / Averses de neige",
        "Neige",
        "Averses de neige",
        "Neige forte",
        "Quelques flocons",
    ],
    "snowy-rainy": ["Pluie et neige", "Pluie verglaçante"],
    "sunny": ["Ensoleillé"],
    "windy": [],
    "windy-variant": [],
    "exceptional": [],
}
