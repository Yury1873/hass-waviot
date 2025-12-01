import logging
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

# from .const import DOMAIN, CONF_API_KEY, CONF_MODEM_ID
from . import const
from .coordinator import WaviotDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS: Final = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WAVIoT integration from config entry."""
    _LOGGER.debug("Setup %s (%s)", entry.title, entry.data[const.CONF_USERNAME])
    _LOGGER.debug("Setup %s (%s)", entry.title, entry.data[const._MODEM_ID])
    api_key = entry.data[const.CONF_API_KEY]
    modem_id = entry.data[const.CONF_MODEM_ID]

    hass.data.setdefault(const.DOMAIN, {})  # в примере наоборот с пред. строкой
    coordinator = WaviotDataUpdateCoordinator(hass, api_key, modem_id)
    hass.data[const.DOMAIN][entry.entry_id] = coordinator
    await coordinator.async_config_entry_first_refresh()

    # add options handler
    #if not entry.update_listeners:
    #    entry.add_update_listener(async_update_options)

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
   # _LOGGER.debug("Unload %s (%s)", entry.title, entry.data[const.CONF_USERNAME])
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ['sensor'])
    if unload_ok:
        hass.data[const.DOMAIN].pop(entry.entry_id)
    return unload_ok
