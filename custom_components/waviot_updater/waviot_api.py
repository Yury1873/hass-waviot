import logging
import asyncio

from collections import namedtuple
import datetime
from typing import Dict
from . import waviot_client, const

_LOGGER = logging.getLogger(__name__)
lock = asyncio.Lock()

Registrator_key = namedtuple('Registrator_key', ['modem_id', 'channel_id'])


#############################
class ResponseData:
    def __init__(self, req_type: str,response_data: Dict, ) -> None:
        self.req_type= req_type
        self.response_data = response_data
        self.resp_timestamp = datetime.datetime.now()


#############################
class WaviotApi:
    def __init__(self, client: waviot_client.WaviotClient) -> None:
        _LOGGER.debug("Initialize, api_key %s", client._api_key)
        self.client = client
        self._profile = None
        self._registrators_raw: Dict[Registrator_key, Dict] = {}
        self._balances_daily: Dict[Registrator_key, Dict] = {}

    @property
    async def settlement_name(self) -> str:
        return await self.client.get_settlement_name()

    async def async_fetch_all(self) -> None:
        """Fetch profile and data."""
        #await self.async_fetch_profile()
        await self.async_fetch_data()

    async def async_fetch_profile(self) -> None:
            _LOGGER.debug("Fetch profile")
            #self._profile = None
            self._profile = await self.client.async_profile()

    async def async_fetch_data(self) -> None:
        await self._load_registrators()
        await self._fetch_daily_balances()
        await self._fetch_monthly_balances()

    #@property
    #def registrators(self) -> Dict[Registrator_key,Registrator]:
    #    return self._registrators

    @property
    def registrators_raw(self) -> Dict[Registrator_key,Dict]:
        return self._registrators_raw

    @property
    def balances_daily_raw(self) -> Dict[Registrator_key,Dict]:
        return self._balances_daily

    def get_balances(self, key: Registrator_key, type: const.BALANCE_TYPES='daily') -> Dict:
        match type:
            case 'daily':
                return self._balances_daily[key]
            #case 'monthly':
            #    return self._balances_daily[key]
        return {}

    async def _load_registrators(self) -> None:
        _LOGGER.debug("get _load_registrators")
        modems = await self.client.async_modems()
        _LOGGER.debug("responce - modems=%s",modems)
        async with lock:
        #pass
            for m in modems:
                for ch_id, data in m['registrators'].items():
                    if ch_id != 'electro_event_log':
                        reg_key = Registrator_key(modem_id=m['modem_id'], channel_id=ch_id)
                        _LOGGER.debug("reg_key %s", reg_key)
                        self._registrators_raw[reg_key]={**data,**const.CHANELS_LIST[ch_id] }
                        self._registrators_raw[reg_key]['locality_name'] = m['tree_name']
                        self._registrators_raw[reg_key]['modem_id'] = m['modem_id']

    async def _fetch_daily_balances(self ):
        _LOGGER.debug("_daily_balance")
        daily_balances = await self.client.async_balances('daily')
        _LOGGER.debug("resp _daily_balances: %s",daily_balances)
       # async with lock:
        for ch_id, b in daily_balances['balance'].items():
                if isinstance(b, dict):
                    for modem_id, data in b['data'].items():
                        _LOGGER.debug("modem_id: %s data=%s", modem_id, data)
                        if (ch_id != 'electro_ac_p_lsum_t3') and (ch_id != 'electro_ac_p_lsum_t4'):
                            reg_key = Registrator_key(modem_id=modem_id, channel_id=ch_id)
                            _LOGGER.debug("reg_key %s", reg_key)
                            self._balances_daily[reg_key] = {**data, **const.CHANELS_LIST[ch_id]}
                            #self._balances_daily[reg_key]['channel_id'] = ch_id
                            self._balances_daily[reg_key]['locality_name'] = daily_balances['balance']['element_name']

                            #self._registrators_raw[reg_key] = {**data, **const.CHANELS_LIST[ch_id]}
                            #self._registrators_raw[reg_key]['locality_name'] = m['tree_name']
                            #self._registrators_raw[reg_key]['modem_id'] = m['modem_id']


    async def _fetch_monthly_balances(self):
        ...

    #def get_registrator( self, modem_id:str, channel_id:str ) -> Registrator:
     #   return self.get_registrator(Registrator_key(modem_id=modem_id, channel_id=channel_id))

    #def get_registrator( self, key: Registrator_key) -> Registrator:
     #       return self._registrators[key]


