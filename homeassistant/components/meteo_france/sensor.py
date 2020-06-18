"""Support for Meteo-France raining forecast sensor."""
import logging

from meteofrance.helpers import (
    get_warning_text_status_from_indice_color,
    readeable_phenomenoms_dict,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_NEXT_RAIN_1_HOUR_FORECAST,
    ATTR_NEXT_RAIN_SUMMARY,
    ATTRIBUTION,
    COORDINATOR_ALERT,
    COORDINATOR_FORECAST,
    COORDINATOR_RAIN,
    DOMAIN,
    ENTITY_API_DATA_PATH,
    ENTITY_CLASS,
    ENTITY_ENABLE,
    ENTITY_ICON,
    ENTITY_NAME,
    ENTITY_UNIT,
    SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up the Meteo-France sensor platform."""
    coordinator_forecast = hass.data[DOMAIN][entry.entry_id][COORDINATOR_FORECAST]
    coordinator_rain = hass.data[DOMAIN][entry.entry_id][COORDINATOR_RAIN]
    coordinator_alert = hass.data[DOMAIN][entry.entry_id][COORDINATOR_ALERT]

    entities = []
    for sensor_type in SENSOR_TYPES:
        if sensor_type == "next_rain":
            if coordinator_rain:
                entities.append(MeteoFranceRainSensor(sensor_type, coordinator_rain))
                _LOGGER.debug(
                    "Next rain sensor added for %s.",
                    coordinator_forecast.data.position["name"],
                )

        elif sensor_type == "weather_alert":
            department = coordinator_forecast.data.position["dept"]
            coordinator_alert_added = hass.data[DOMAIN].get(department)
            if coordinator_alert_added is False:
                hass.data[DOMAIN][department] = True
                entities.append(MeteoFranceAlertSensor(sensor_type, coordinator_alert))
                _LOGGER.debug(
                    "Weather alert sensor for department n°%s added with %s.",
                    coordinator_forecast.data.position["dept"],
                    coordinator_forecast.data.position["name"],
                )
            else:
                _LOGGER.info(
                    "Weather alert sensor for department n°%s skipped within %s: already added with another city",
                    coordinator_forecast.data.position["dept"],
                    coordinator_forecast.data.position["name"],
                )

        else:
            entities.append(MeteoFranceSensor(sensor_type, coordinator_forecast))
            _LOGGER.debug(
                "Sensor %s added for %s.",
                sensor_type,
                coordinator_forecast.data.position["name"],
            )

    async_add_entities(
        entities, False,
    )


class MeteoFranceSensor(Entity):
    """Representation of a Meteo-France sensor."""

    def __init__(self, sensor_type: str, coordinator: DataUpdateCoordinator):
        """Initialize the Meteo-France sensor."""
        self._type = sensor_type
        self.coordinator = coordinator
        city_name = self.coordinator.data.position["name"]
        self._name = f"{city_name} {SENSOR_TYPES[self._type][ENTITY_NAME]}"
        self._unique_id = f"{self.coordinator.data.position['lat']},{self.coordinator.data.position['lon']}_{self._type}"

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    @property
    def name(self):
        """Return the name."""
        return self._name

    @property
    def state(self):
        """Return the state."""
        path = SENSOR_TYPES[self._type][ENTITY_API_DATA_PATH].split(":")
        data = getattr(self.coordinator.data, path[0])

        if path[0] == "probability_forecast":
            # TODO: return often 'null' with France cities. Need investigation
            # TODO: "probability_forecast" not always available.
            data = data[0]

        if len(path) == 3:
            value = data[path[1]][path[2]]
        value = data[path[1]]

        if self._type == "wind_speed":
            # convert API wind speed from m/s to km/h
            value = round(value * 3.6)
        return value

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._type][ENTITY_UNIT]

    @property
    def icon(self):
        """Return the icon."""
        return SENSOR_TYPES[self._type][ENTITY_ICON]

    @property
    def device_class(self):
        """Return the device class."""
        return SENSOR_TYPES[self._type][ENTITY_CLASS]

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return SENSOR_TYPES[self._type][ENTITY_ENABLE]

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {ATTR_ATTRIBUTION: ATTRIBUTION}

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

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


class MeteoFranceRainSensor(MeteoFranceSensor):
    """Representation of a Meteo-France rain sensor."""

    @property
    def state(self):
        """Return the state."""
        next_rain_date_locale = self.coordinator.data.next_rain_date_locale()
        return (
            dt_util.as_local(next_rain_date_locale) if next_rain_date_locale else None
        )

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        next_rain_date_locale = self.coordinator.data.next_rain_date_locale()
        next_rain_datetime = (
            dt_util.as_local(next_rain_date_locale) if next_rain_date_locale else None
        )
        if next_rain_datetime:
            rain_text_summary = (
                f"La pluie est attendue à {next_rain_datetime.strftime('%H:%M')}."
            )
        else:
            rain_text_summary = "Pas de pluie dans la prochaine heure."

        return {
            ATTR_NEXT_RAIN_1_HOUR_FORECAST: [
                {
                    dt_util.as_local(
                        self.coordinator.data.timestamp_to_locale_time(item["dt"])
                    ).strftime("%H:%M"): item["desc"]
                }
                for item in self.coordinator.data.forecast
            ],
            ATTR_NEXT_RAIN_SUMMARY: rain_text_summary,
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }


class MeteoFranceAlertSensor(MeteoFranceSensor):
    """Representation of a Meteo-France alert sensor."""

    # pylint: disable=super-init-not-called
    def __init__(self, sensor_type: str, coordinator: DataUpdateCoordinator):
        """Initialize the Meteo-France sensor."""
        self._type = sensor_type
        self.coordinator = coordinator
        dept_code = self.coordinator.data.domain_id
        self._name = f"{dept_code} {SENSOR_TYPES[self._type][ENTITY_NAME]}"
        self._unique_id = self._name

    @property
    def state(self):
        """Return the state."""
        return get_warning_text_status_from_indice_color(
            self.coordinator.data.get_domain_max_color()
        )

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            **readeable_phenomenoms_dict(self.coordinator.data.phenomenons_max_colors),
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }
