from __future__ import annotations
from typing import Optional, Dict, Any, Mapping
from datetime import timedelta
import voluptuous as vol
import logging

from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import callback
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
    SchemaOptionsFlowHandler,
)
from homeassistant.const import CONF_NAME

_LOGGER = logging.getLogger(__name__)

from . import const, waviot_api, waviot_client


DATA_SCHEMA_API_KEY = vol.Schema({ vol.Required(const.CONF_API_KEY): str,})
DATA_SCHEMA_OPTIONS = vol.Schema(
            {
    #        vol.Optional(
    #            const.CONF_UPDATE_INTERVAL,
    #            default=timedelta_to_dict(
    #                cv.time_period(
    #                    handler.options.get(
    #                        const.CONF_UPDATE_INTERVAL,
    #                        const.DEFAULT_UPDATE_INTERVAL.total_seconds(),
    #                    )
    #                )
    #            ),
    #        ): selector.DurationSelector(
    #            selector.DurationSelectorConfig(enable_day=False),
    #        ),
            vol.Optional( const.CONF_POWER_TARRIFF_1,): selector.NumberSelector(
                        selector.NumberSelectorConfig(min=0.0, max=99.99, step=0.01, mode=selector.NumberSelectorMode.BOX)
                    ),
            vol.Optional( const.CONF_POWER_TARRIFF_2,): selector.NumberSelector(
                        selector.NumberSelectorConfig(min=0.0, max=99.99, step=0.01, mode=selector.NumberSelectorMode.BOX)
                    ),
            vol.Optional( const.CONF_POWER_TARRIFF_3,):  selector.NumberSelector(
                        selector.NumberSelectorConfig(min=0.0, max=99.99, step=0.01, mode=selector.NumberSelectorMode.BOX)
                    ),
            vol.Optional( const.CONF_POWER_TARRIFF_4, ): selector.NumberSelector(
                        selector.NumberSelectorConfig(min=0.0, max=99.99, step=0.01, mode=selector.NumberSelectorMode.BOX)
                    ),
            }
    )

CONFIG_FLOW = {
    "api_key": SchemaFlowFormStep(
        schema=DATA_SCHEMA_API_KEY,
        next_step="options",
        #next_step=None,
        #validate_user_input=validate_connection,
    ),
     "options": SchemaFlowFormStep(
        schema=DATA_SCHEMA_OPTIONS,
        next_step=None,
    ),
}

class WaviotFlowHandler(config_entries.ConfigFlow, domain= const.DOMAIN):
    VERSION = 1
    MINOR_VERSION = 1
    #config_flow = CONFIG_FLOW
    _api: Optional[waviot_api.WaviotApi] = None

    @property
    def api(self):
        if self._api is None:
            #self._api_key = self._async_param_or_none(const.CONF_API_KEY)
            #self._api_key = self.context[const.CONF_API_KEY]
            if self._api_key is None:
                    raise ValueError("API key not available")
            self._api = waviot_api.WaviotApi(
                waviot_client.WaviotClient(async_get_clientsession(self.hass),self._api_key )
            )
        return self._api

    async def async_step_user(  self, user_input: dict[str, Any] | None = None ) -> ConfigFlowResult:
        if user_input is not None:
            self._api_key = user_input[const.CONF_API_KEY]
            title = await self.api.settlement_name
            return self.async_create_entry(title=title, data=user_input, options = user_input)
        return self.async_show_form( step_id="user", data_schema=DATA_SCHEMA_API_KEY)

    @staticmethod
    @callback
    def async_get_options_flow(  config_entry: config_entries.ConfigEntry ) -> config_entries.OptionsFlow:
        return WaviotOptionsFlowHandler(config_entry)

    @callback
    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        return options.get("name", "Default")


#OPTIONS_FLOW = {
#    "init": SchemaFlowFormStep(DATA_SCHEMA_OPTIONS),
#}

class WaviotOptionsFlowHandler(config_entries.OptionsFlow):
    #options_flow = OPTIONS_FLOW  # Словарь шагов options

    def __init__(self, options: config_entries.ConfigEntry):
        self.options = options
        _LOGGER.debug(f"options.options {options.options}")

    async def async_step_init( self, user_input: dict[str, Any] | None = None ) -> config_entries.FlowResult:
        """Инициализация options."""
        _LOGGER.debug(f"user_input {user_input}")
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        if self.options.options is not None and len(self.options.options) > 0:
            schema = self.add_suggested_values_to_schema( DATA_SCHEMA_OPTIONS, self.options.options )
        else:
            schema = DATA_SCHEMA_OPTIONS
        return self.async_show_form(step_id="init", data_schema= schema)