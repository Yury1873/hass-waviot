from __future__ import annotations
from typing import Optional, Any
from datetime import timedelta
import voluptuous as vol
import logging

from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
    SchemaOptionsFlowHandler,
)
from homeassistant.data_entry_flow import section, SectionConfig

_LOGGER = logging.getLogger(__name__)

from . import const, waviot_api, waviot_client
DATA_SCHEMA_API_KEY = vol.Schema({ vol.Required(const.CONF_API_KEY): str,})

TARIFFS_CONFIG_SELECTOR = selector.NumberSelectorConfig(min=0.0, max=99.99, step=0.01, mode=selector.NumberSelectorMode.BOX)
DATA_SCHEMA_SENSORS_OPTIONS = vol.Schema( {
    vol.Required("daily_balance_options",default=["daily_balance_kwh", "daily_monetary_balance"]):
        selector.SelectSelector(
            selector.SelectSelectorConfig(  options= ["daily_balance_kwh", "daily_monetary_balance"],
                                        translation_key= "daily_balance_options", multiple=True)
        ),
    vol.Required("monthly_balance_options", default=["monthly_balance_kwh", "monthly_monetary_balance"]):
        selector.SelectSelector(
            selector.SelectSelectorConfig(options=["monthly_balance_kwh", "monthly_monetary_balance"],
                                          translation_key="monthly_balance_options", multiple=True)
        ),
    vol.Required("tariff_rate_sensors", default=True): bool,
})

DATA_SCHEMA_TARIFFS_OPTIONS = vol.Schema({
   # vol.Required("tariff_options"): section(
    #    vol.Schema({
            vol.Optional( const.CONF_POWER_TARIFF_1,default=0): selector.NumberSelector( TARIFFS_CONFIG_SELECTOR),
            vol.Optional( const.CONF_POWER_TARIFF_2,default=0): selector.NumberSelector( TARIFFS_CONFIG_SELECTOR),
            vol.Optional( const.CONF_POWER_TARIFF_3,default=0): selector.NumberSelector( TARIFFS_CONFIG_SELECTOR),
            vol.Optional( const.CONF_POWER_TARIFF_4,default=0): selector.NumberSelector( TARIFFS_CONFIG_SELECTOR),
     #   }),
    #    SectionConfig(collapsed=True),
   # ),
   })



#CONFIG_FLOW = {
#    "api_key": SchemaFlowFormStep(
#        schema=DATA_SCHEMA_API_KEY,
#        next_step="options",
#        #next_step=None,
#        #validate_user_input=validate_connection,
#    ),
#     "options": SchemaFlowFormStep(
#        schema=DATA_SCHEMA_OPTIONS,
#        next_step=None,
#    ),
#}

class WaviotFlowHandler(config_entries.ConfigFlow, domain= const.DOMAIN):
    VERSION = 1
    MINOR_VERSION = 1
    _api: Optional[waviot_api.WaviotApi] = None

    @property
    def api(self):
        if self._api is None:
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
            return await self.async_step_confirm_api_key(user_input)
        return self.async_show_form( step_id="user", data_schema=DATA_SCHEMA_API_KEY)


    async def async_step_confirm_api_key(self, user_input):
        _LOGGER.debug(f"user_input {user_input}")
        #тут надо бы организовать проверку api_key
        return await self.async_step_select_sensors()

    async def async_step_select_sensors(self, user_input=None):
        if user_input:
            self.context.update(user_input)
            _LOGGER.debug(f"user_input {user_input}")
            return await self.async_step_tariffs()
        return self.async_show_form( step_id="select_sensors", data_schema=DATA_SCHEMA_SENSORS_OPTIONS)


    async def async_step_tariffs(self, user_input=None):
        if user_input:
            self.context.update(user_input)
            _LOGGER.debug(f"user_input {user_input}")
            title = await self.api.settlement_name
            return self.async_create_entry(title=title,
                                           data={const.CONF_API_KEY: self._api_key},
                                           options = self.context
                                          )
        return self.async_show_form( step_id="tariffs", data_schema=DATA_SCHEMA_TARIFFS_OPTIONS)

    @staticmethod
    @callback
    def async_get_options_flow(  config_entry: config_entries.ConfigEntry ) -> config_entries.OptionsFlow:
        return WaviotOptionsFlowHandler(config_entry)

    #@callback
    #def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
    #    return options.get("name", "Default")


#OPTIONS_FLOW = {
#    "init": SchemaFlowFormStep(DATA_SCHEMA_OPTIONS),
#}
###########################################################
class WaviotOptionsFlowHandler(config_entries.OptionsFlowWithReload):

    #options_flow = OPTIONS_FLOW  # Словарь шагов options

    def __init__(self, entry: config_entries.ConfigEntry):
        self.entry = entry
        _LOGGER.debug(f"options.options {entry.options}")

    async def async_step_init( self, user_input: dict[str, Any] | None = None ) -> config_entries.FlowResult:
        """Инициализация options."""
        _LOGGER.debug(f"user_input {user_input}")
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        schema = DATA_SCHEMA_TARIFFS_OPTIONS
        if self.entry.options is not None and len(self.entry.options) > 0:
            schema = self.add_suggested_values_to_schema( DATA_SCHEMA_TARIFFS_OPTIONS, self.entry.options )

        #self.show_advanced_options=True
        #if self.show_advanced_options or True:
        #    schema[vol.Optional("allow_groups")] = selector.SelectSelectorConfig (
        #                            options= ["all", "light", "switch"],
        #                        )

        return self.async_show_form(step_id="init", data_schema= schema)