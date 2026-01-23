from __future__ import annotations
from typing import Optional, Dict
from datetime import timedelta
import voluptuous as vol

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
#from homeassistant.helpers import config_entries

from . import const, waviot_api, waviot_client

_API_KEY  = const.CONF_API_KEY

class WaviotFlowHandler(config_entries.ConfigFlow, domain=  const.DOMAIN):
    VERSION = 1

    _api: Optional[waviot_api.WaviotApi] = None

    @property
    def api(self):
        if self._api is None:
            self._api = waviot_api.WaviotApi(
                waviot_client.WaviotClient(async_get_clientsession(self.hass),self.context[_API_KEY] )
            )
        return self._api

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.context[_API_KEY] = user_input[_API_KEY]
            return self.async_create_entry(title= await self.api.settlement_name, data=user_input)

        schema = vol.Schema({
            vol.Required(const.CONF_API_KEY): str
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return SchemaOptionsFlowHandler(config_entry, OPTIONS_FLOW)

async def general_options_schema(
        handler: SchemaConfigFlowHandler | SchemaOptionsFlowHandler,
    ) -> vol.Schema:
    def timedelta_to_dict(delta: timedelta) -> dict:
                hours, seconds = divmod(delta.seconds, 3600)
                minutes, seconds = divmod(seconds, 60)
                return {
                    "days": delta.days,
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds,
                }

    #if not hasattr(handler, 'options') or handler.options is None:
    #        handler.options = {}
    #handler.options[const.CONF_UPDATE_INTERVAL] = const.DEFAULT_UPDATE_INTERVAL.total_seconds()

    return vol.Schema(
            {
            vol.Optional(
                const.CONF_UPDATE_INTERVAL,
                default=timedelta_to_dict(
                    cv.time_period(
                        handler.options.get(
                            const.CONF_UPDATE_INTERVAL,
                            const.DEFAULT_UPDATE_INTERVAL.total_seconds(),
                        )
                    )
                ),
            ): selector.DurationSelector(
                selector.DurationSelectorConfig(enable_day=False),
            ),
     #       vol.Optional(
     #           const.CONF_RATES_SENSORS,
     #           default=handler.options.get(const.CONF_RATES_SENSORS, True),
     #       ): selector.BooleanSelector(selector.BooleanSelectorConfig()),
     #       vol.Optional(
     #           const.CONF_DIAGNOSTIC_SENSORS,
     #           default=handler.options.get(const.CONF_DIAGNOSTIC_SENSORS, False),
     #       ): selector.BooleanSelector(selector.BooleanSelectorConfig()),
            vol.Optional(
                const.CONF_POWER_TARRIFF_1,
                default=handler.options.get(const.CONF_POWER_TARRIFF_1, 0.0),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                 min=0.0,
                 max=99.99,
                 step=0.01,
                mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                const.CONF_POWER_TARRIFF_2,
                default=handler.options.get(const.CONF_POWER_TARRIFF_2, 0),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.0,
                    max=99.99,
                    step=0.01,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                const.CONF_POWER_TARRIFF_3,
                default = handler.options.get(const.CONF_POWER_TARRIFF_3, 0),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.0,
                    max=99.99,
                    step=0.01,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                const.CONF_POWER_TARRIFF_4,
                default = handler.options.get(const.CONF_POWER_TARRIFF_4, 0),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.0,
                    max=99.99,
                    step=0.01,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            }
    )


OPTIONS_FLOW: Dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "init": SchemaFlowFormStep(general_options_schema),
}
