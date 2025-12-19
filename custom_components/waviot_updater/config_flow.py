from __future__ import annotations
from . import const
import voluptuous as vol
from homeassistant import config_entries




import logging
from collections.abc import Mapping
from datetime import timedelta
from typing import Any, Dict, Final, Optional
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowError, FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
    SchemaOptionsFlowHandler,
)
from homeassistant.util import slugify

from . import const, waviot_api, waviot_client

_API_KEY: Final = const.CONF_API_KEY

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
#            return self.async_create_entry(title=f"Modem {user_input[const.CONF_API_KEY]}", data=user_input)
            return self.async_create_entry(title= await self.api.settlement_name, data=user_input)

        schema = vol.Schema({
            vol.Required(const.CONF_API_KEY): str
        })
        return self.async_show_form(step_id="user", data_schema=schema)
