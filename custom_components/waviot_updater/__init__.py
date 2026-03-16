import logging
from typing import Final
from . import const

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .coordinator import WaviotDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS: Final = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WAVIoT integration from config entry."""
    #_LOGGER.debug("Setup %s (%s)", entry.title, entry.data[const.CONF_API_KEY])
    #api_key = entry.data[const.CONF_API_KEY]
    #modem_id = entry.data[const.CONF_MODEM_ID]
    _LOGGER.debug(f"async_setup_entry {entry.options}")
    hass.data.setdefault(const.DOMAIN, {})
    coord = WaviotDataUpdateCoordinator(hass, entry)
    hass.data[const.DOMAIN][entry.entry_id] = coord
    await coord.async_config_entry_first_refresh()

    # add options handler
    #if not entry.update_listeners:
    #    entry.add_update_listener(async_update_options)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unload %s (%s)", entry.title, entry.data[const.CONF_API_KEY])
    _LOGGER.debug(f"async_remove_entry {entry.entry_id}")
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        #if runtime_data := entry.runtime_data:
        #    _LOGGER.debug(f'get runtime_data.async_reset')
        #    runtime_data.async_reset()  # Остановка таймеров, unsubscribe
        hass.data[const.DOMAIN].pop(entry.entry_id)
    return unload_ok

#async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry):
#    """Handle removal of an entry from UI."""
#    # Дополнительная очистка при полном remove (опционально)
#    _LOGGER.debug(f"async_remove_entry {entry.entry_id}")
#    await hass.config_entries.async_remove(entry.entry_id)
#    return True