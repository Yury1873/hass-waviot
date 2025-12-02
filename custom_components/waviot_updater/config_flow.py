from homeassistant import config_entries
from . import const
import voluptuous as vol
from typing import Any, Dict, Final, Optional

class WaviotFlowHandler(config_entries.ConfigFlow, domain=  const.DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=f"Modem {user_input[const.CONF_MODEM_ID]}", data=user_input)

        schema = vol.Schema({
            vol.Required(const.CONF_API_KEY): str,
            vol.Required(const.CONF_MODEM_ID): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema)
