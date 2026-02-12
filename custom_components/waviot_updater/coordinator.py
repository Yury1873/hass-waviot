import logging
import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator #, UpdateFailed

from . import const, waviot_client, waviot_api

_LOGGER = logging.getLogger(__name__)

class WaviotDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch WAVIoT modem and energy data safely."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.api_key = entry.data[const.CONF_API_KEY]
        super().__init__(
            hass,
            _LOGGER,
            name=f"WAVIoT",
            update_interval= const.DEFAULT_UPDATE_INTERVAL,
        )

        self.api = waviot_api.WaviotApi(
            waviot_client.WaviotClient(
                async_get_clientsession(hass), self.api_key
            )
        )
        if const.CONF_UPDATE_INTERVAL in entry.options:
            self.update_interval = cv.time_period( entry.options[const.CONF_UPDATE_INTERVAL])

    async def _async_update_data(self):
        await self._fetch()

    async def _fetch(self):
       async with async_timeout.timeout(60):
             await self.api.async_fetch_all()

    #def _compute_latest(self):
    #    """Compute only the latest reading value."""
    #    if self.data is None:
    #        self.data = {}

    #   readings = self.data.get("readings", [])
    #    if not readings:
    #        _LOGGER.debug("No readings available to compute latest value.")
    #        self._init_empty_data()
    #        return

    #    latest_timestamp, latest_value = readings[-1]
    #    latest_dt = datetime.fromtimestamp(latest_timestamp, tz=timezone.utc)
    #    self.data["latest"] = latest_value
    #    self.data["last_update"] = latest_dt

    #    _LOGGER.debug("Latest reading computed: %s at %s", latest_value, latest_dt)

    def _init_empty_data(self):
        """Initialize empty data dict."""
        self.data.update({
            "battery": None,
            "temperature": None,
            "readings": [],
            "latest": None,
            "last_update": None,
        })
