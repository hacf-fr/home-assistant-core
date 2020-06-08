"""Config flow to configure the Meteo-France integration."""
import logging

from meteofrance.client import MeteoFranceClient

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE

from .const import CONF_CITY
from .const import DOMAIN  # pylint: disable=unused-import

_LOGGER = logging.getLogger(__name__)


class MeteoFranceFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Meteo-France config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def _show_setup_form(self, user_input=None, errors=None):
        """Show the setup form to the user."""

        if user_input is None:
            user_input = {}

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_CITY, default=user_input.get(CONF_CITY, "")): str}
            ),
            errors=errors or {},
        )

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is None:
            return self._show_setup_form(user_input, errors)

        city = user_input[CONF_CITY]  # Might be a city name or a postal code
        latitude = user_input.get(CONF_LATITUDE)
        longitude = user_input.get(CONF_LONGITUDE)

        client = MeteoFranceClient()

        try:
            if not latitude:
                places = await self.hass.async_add_executor_job(
                    client.search_places, city, latitude, longitude
                )
                _LOGGER.error(places)
                return await self.async_step_cities(places=places)
        except Exception as exp:  # pylint: disable=broad-except
            _LOGGER.error(exp)
            return self.async_abort(reason="unknown")

        # Check if already configured
        await self.async_set_unique_id(f"{latitude}, {longitude}")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=city, data={CONF_LATITUDE: latitude, CONF_LONGITUDE: longitude},
        )

    async def async_step_import(self, user_input):
        """Import a config entry."""
        return await self.async_step_user(user_input)

    async def async_step_cities(self, user_input=None, places=None):
        """Step where the user choose the city from the API search results."""
        if places and len(places) > 1 and self.source != SOURCE_IMPORT:
            places_for_form = {}
            for place in places:
                places_for_form[
                    _build_place_key(place)
                ] = f"{place.name} - {place.admin} - {place.country}"
            _LOGGER.warning(places_for_form)

            return await self._show_cities_form(places_for_form)
        else:
            user_input = {CONF_CITY: _build_place_key(places[0])}

        city_infos = user_input.get(CONF_CITY).split(";")
        return await self.async_step_user(
            {
                CONF_CITY: city_infos[0],
                CONF_LATITUDE: city_infos[1],
                CONF_LONGITUDE: city_infos[2],
            }
        )

    async def _show_cities_form(self, cities):
        """Show the form to choose the city."""
        return self.async_show_form(
            step_id="cities",
            data_schema=vol.Schema(
                {vol.Required(CONF_CITY): vol.All(vol.Coerce(str), vol.In(cities))}
            ),
        )


def _build_place_key(place) -> str:
    return f"{place.name};{place.latitude};{place.longitude}"
