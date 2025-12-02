import json as jsonmod
import logging
from enum import StrEnum
from typing import Any, Final, List, Optional, TypedDict

import aiohttp
from homeassistant import exceptions
from . import const

_LOGGER = logging.getLogger(__name__)

LOGIN_TYPE_API_KEY: Final = "api_key"
LOGIN_TYPE_EMAIL: Final = "email"

class WaviotClient:
    _API_URL: Final = const.API_URL
    def __init__(
            self, session: aiohttp.ClientSession ) -> None:
        self._session = session
        self.headers = None
      #  self._headers = {
       #     aiohttp.hdrs.ACCEPT: "application/json, text/plain, */*",
        #    aiohttp.hdrs.CONTENT_TYPE: "application/json",
         #   "Customer": "ikus-spb",
       # }
        #self.auth = auth
        #if auth:
         #   self._updata_auth(auth)

    async def _async_get_raw(self, url: str) -> aiohttp.ClientResponse:
        _LOGGER.debug("request: %s", url)
        return await self._session.get(f"{self._API_URL}{url}", headers=self._headers)

    async def _async_get(self, url: str):
        result = await self._async_get_raw(url)
        json = await self._async_response_json(result)
        if _LOGGER.isEnabledFor(logging.DEBUG):
            if isinstance(json, list) and len(json) > 100:
                json_str = "result is too large to display"
            else:
                json_str = "\n" + jsonmod.dumps(json, ensure_ascii=False, indent=None)
            _LOGGER.debug("%s: %s", url, json_str)
        return json