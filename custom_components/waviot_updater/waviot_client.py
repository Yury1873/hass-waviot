import json as jsonmod
import logging
from datetime import time
import time
from typing import Final, List, Dict,  Optional

import aiohttp
from homeassistant import exceptions
from . import const,  my_types

_LOGGER = logging.getLogger(__name__)

class WaviotClient:
    BASE_URL: Final = const.BASE_URL
    _API_URL: Final = const.API_URL

    def __init__(
            self, session: aiohttp.ClientSession,  api_key ) -> None:
        self._api_key = api_key
        self._session = session
        self.headers = None
        #self._element_id = ""

    @staticmethod
    async def _async_response_json(
            result: aiohttp.ClientResponse, empty_body_request: bool = False
    ):
        try:
            if result.status != 200:
                if result.status == 404:
                    raise ClientError(
                        result.request_info, code=404, message="Страница не найдена"
                    )
                json = await result.json()
                if "code" in json and int(json["code"]) == 5:
                    raise ClientAuthError(result.request_info, json)
                error = ClientError(result.request_info, json)
                _LOGGER.error("Failed request: %s", error)
                raise error
            if empty_body_request:
                return None

            if result.content_type == "application/json":
                return await result.json()
            else:
                _LOGGER.warning(
                    "Unknown content type: %s, content length %s",
                    result.content_type,
                    result.content_length,
                )
                return {}
        except aiohttp.ContentTypeError as err:
            raise ClientError(
                result.request_info, code=err.status, message=err.message
            ) from err

    async def _async_get_raw(self, url_sufix: str, params : Dict=None) -> aiohttp.ClientResponse:
        params_local =  {
            "key": self._api_key
        }
        if  params is not None:
            params_local.update(params)
        url = f"{self._API_URL}{url_sufix}"
        _LOGGER.debug(f"url= {url}, params={params_local}")
        return await self._session.get(url, params=params_local)

    async def _async_get(self, url_sufix: str, params=None):
        result = await self._async_get_raw(url_sufix, params)
        _LOGGER.debug(" result %s",result)
        json = await self._async_response_json(result)
        if _LOGGER.isEnabledFor(logging.DEBUG):
            if isinstance(json, list) and len(json) > 100:
                json_str = "result is too large to display"
            else:
                json_str = "\n" + jsonmod.dumps(json, ensure_ascii=False, indent=None)
            _LOGGER.debug("%s: %s", url_sufix, json_str)
        return json

    async def _async_get_element_id(self) -> str:
        _LOGGER.debug("get async_element_id")
        params = {
           'key': self._api_key
        }
        url_sufix= "tree/get_element/"
        _LOGGER.debug("get url_sufix: %s", url_sufix)
        data = await self._async_get(url_sufix=url_sufix,params=params)
        _LOGGER.debug("element resp: %s", data)
        if data['status'] == 'ok' :
            self._element_id = data['element_id']
            _LOGGER.debug("element id: %s", self._element_id)
        return self._element_id

    async def async_modems(self) -> list:
        #https://lk.waviot.ru/api.data/get_full_element_info/?id=1793084
        _LOGGER.debug("get sysnc_modems")
        params = {
            "id": await self._async_get_element_id()
        }
        url= f"{const.API_URL}data/get_full_element_info"
        _LOGGER.debug("get url: %s", url)
        data = await self._async_get(f"data/get_full_element_info/",params)
        assert data.get('status') == "ok"
        _LOGGER.debug("element resp: %s", data)
        modems: List = []
        for key_dv, modem_meta in data['devices'].items():
            _LOGGER.debug("Data received device: %s", modem_meta)
            modems.append(modem_meta)
            #for reg_key, reg_val in val_dv['registrators'].items():
            #    _LOGGER.debug("registrator: ", reg_val)
        _LOGGER.debug("list modems: %s", modems)
        return modems

    async def async_modems_channels_last_values(self,modem_id: str) -> dict[my_types.Registrator_key, dict]:
        params = {
            "modem_id": modem_id,
            "from": f"{int(time.time())}",
        }
        url_sufix = "data/get_values/"
        url = f"{const.API_URL}{url_sufix}"
        _LOGGER.debug("get url: %s", url)
        data = await self._async_get(f"{url_sufix}",params)
        assert data.get('status') == "ok"
        _LOGGER.debug("resp: %s", data)
        ret: dict[my_types.Registrator_key, dict] = {}
        for item in data['registrators'].values():
            if item.get('active') :
                val: list = item.get('values')
                if val is not None:
                    reg_key: my_types.Registrator_key = my_types.Registrator_key(modem_id = modem_id, channel_id=item.get('channel'))
                    ret[reg_key] = val[-1]
        return ret

    async def async_balances(self, timestamp_from: int, timestamp_to: int ) -> Dict:
        _LOGGER.debug("get balance daily ")
        params = {
            "elementId": await self._async_get_element_id(),
            "from": timestamp_from,
            "to": timestamp_to
        }
        _LOGGER.debug(f"async_balances params {params}")
        data = await self._async_get(f"data/get_balance_info/", params)
        #####+++ Добавить обработчик ошибок
        _LOGGER.debug(f"async_balances resp {data}")
        return data

    async def get_settlement_name(self) -> str:
        def _get_setlement_recursion(node) -> str:
            if node:
                for k, meta in node.items():
                    if isinstance(meta, dict):
                        if meta['type'] == "naselennyj_punkt":
                            return meta['name']
                        return   _get_setlement_recursion(meta)
                else: return "???"
            return '???'

        url = f"{const.API_URL}tree/get_tree/"
        _LOGGER.debug("get url: %s", url)
        data = await self._async_get(f"tree/get_tree/")
        _LOGGER.debug(f"data {data}")
        return _get_setlement_recursion(data['tree'])

class ClientError(exceptions.HomeAssistantError):
        def __init__(
                self,
                info: aiohttp.RequestInfo,
                json: Optional[dict] = None,
                code: Optional[int] = None,
                message: str = "",
        ) -> None:
            super().__init__(self.__class__.__name__)
            self.info = info
            self.json = json if json else {}
            if code is not None:
                self.json["code"] = code
            if message:
                self.json["message"] = message

        @property
        def code(self) -> int:
            return self.json.get("code", -1)

        @property
        def message(self) -> str:
            return self.json.get("message", "Неизвестная ошибка")

        @property
        def cause(self) -> str:
            return self.json.get("cause", "")

        def __repr__(self) -> str:
            res = self.__class__.__name__
            res += "["
            if self.info:
                res += f"url={self.info.url}"
            if "code" in self.json:
                res += f", code={self.json['code']}"
            if "message" in self.json:
                res += f", message={self.json['message']}"
            if "cause" in self.json:
                res += f", cause={self.json['cause']}"
            res += "]"
            return res

        def __str__(self) -> str:
            res = self.message
            if "code" in self.json:
                res = f"{res}, код {self.json['code']}"
            if self.info:
                res = f"{res} ({self.info.method} {self.info.url})"
            return res

class ClientAuthError(ClientError):
    pass