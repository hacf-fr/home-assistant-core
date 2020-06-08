"""Support for Meteo-France weather service."""
from datetime import datetime
import logging

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    WeatherEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MODE, TEMP_CELSIUS
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

# from . import MeteoFranceDataUpdateCoordinator
from .const import (
    ATTRIBUTION,
    CONDITION_CLASSES,
    COORDINATOR_FORECAST,
    DOMAIN,
    FORECAST_MODE_HOURLY,
)

_LOGGER = logging.getLogger(__name__)


def format_condition(condition: str):
    """Return condition from dict CONDITION_CLASSES."""
    for key, value in CONDITION_CLASSES.items():
        if condition in value:
            return key
    return condition


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up the Meteo-France weather platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR_FORECAST]

    async_add_entities(
        [MeteoFranceWeather(coordinator, entry.options.get(CONF_MODE))], True
    )


class MeteoFranceWeather(WeatherEntity):
    """Representation of a weather condition."""

    def __init__(self, coordinator: DataUpdateCoordinator, mode: str):
        """Initialise the platform with a data instance and station name."""
        self.coordinator = coordinator
        self._city_name = self.coordinator.data.position["name"]
        self._mode = mode

    @property
    def unique_id(self):
        """Return the unique id of the sensor."""
        return self._city_name

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._city_name

    @property
    def condition(self):
        """Return the current condition."""
        return format_condition(self.coordinator.data.forecast[2]["weather"]["desc"])

    @property
    def temperature(self):
        """Return the temperature."""
        return self.coordinator.data.forecast[2]["T"]["value"]

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def pressure(self):
        """Return the pressure."""
        return self.coordinator.data.forecast[2]["sea_level"]

    @property
    def humidity(self):
        """Return the humidity."""
        return self.coordinator.data.forecast[2]["humidity"]

    @property
    def wind_speed(self):
        """Return the wind speed."""
        return self.coordinator.data.forecast[2]["wind"]["speed"]

    @property
    def wind_bearing(self):
        """Return the wind bearing."""
        wind_bearing = self.coordinator.data.forecast[2]["wind"]["direction"]
        if wind_bearing != -1:
            return wind_bearing

    @property
    def forecast(self):
        """Return the forecast."""
        forecast_data = []

        if self._mode == FORECAST_MODE_HOURLY:
            today = datetime.now().timestamp()
            for forecast in self.coordinator.data.forecast:
                # Can have data of yesterday
                if forecast["dt"] < today:
                    _LOGGER.error("remove_forecast %s %s", self._mode, forecast)
                    continue
                forecast_data.append(
                    {
                        ATTR_FORECAST_TIME: self.coordinator.data.timestamp_to_locale_time(
                            forecast["dt"]
                        ),
                        ATTR_FORECAST_CONDITION: format_condition(
                            forecast["weather"]["desc"]
                        ),
                        ATTR_FORECAST_TEMP: forecast["T"]["value"],
                        ATTR_FORECAST_PRECIPITATION: forecast["rain"].get("1h"),
                        ATTR_FORECAST_WIND_SPEED: forecast["wind"]["speed"],
                        ATTR_FORECAST_WIND_BEARING: forecast["wind"]["direction"]
                        if forecast["wind"]["direction"] != -1
                        else None,
                    }
                )
        else:
            today = datetime.utcnow().timestamp()
            for forecast in self.coordinator.data.daily_forecast:
                # Can have data of yesterday
                if forecast["dt"] < today:
                    _LOGGER.error("remove_forecast %s %s", self._mode, forecast)
                    continue
                # stop when we don't have a weather condition (can happen around last days of forcast, max 14)
                if not forecast.get("weather12H"):
                    break
                forecast_data.append(
                    {
                        ATTR_FORECAST_TIME: self.coordinator.data.timestamp_to_locale_time(
                            forecast["dt"]
                        ),
                        ATTR_FORECAST_CONDITION: format_condition(
                            forecast["weather12H"]["desc"]
                        ),
                        ATTR_FORECAST_TEMP: forecast["T"]["max"],
                        ATTR_FORECAST_TEMP_LOW: forecast["T"]["min"],
                        ATTR_FORECAST_PRECIPITATION: forecast["precipitation"]["24h"],
                    }
                )
        return forecast_data

    @property
    def available(self):
        """Return if state is available."""
        return self.coordinator.last_update_success

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    async def async_update(self):
        """Only used by the generic entity update service."""
        if not self.enabled:
            return

        await self.coordinator.async_request_refresh()

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION
