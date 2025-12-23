import logging
import asyncio

from collections import namedtuple
#import datetime
from datetime import datetime, time
from datetime import datetime
from typing import Dict, Any
from . import waviot_client, const

_LOGGER = logging.getLogger(__name__)
lock = asyncio.Lock()

Registrator_key = namedtuple('Registrator_key', ['modem_id', 'channel_id'])

#############################
class WaviotApi:
    def __init__(self, client: waviot_client.WaviotClient) -> None:
        _LOGGER.debug("Initialize, api_key %s", client._api_key)
        self.client = client
        self._profile = None
        self._registrators_raw: Dict[Registrator_key, Dict] = {}
        self._balances_daily: Dict[Registrator_key, Dict] = {}
        self._balances_monthly: Dict[Registrator_key, Dict] = {}

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
        await self._fetch_balances()

    @property
    def registrators_raw(self) -> Dict[Registrator_key,Dict]:
        return self._registrators_raw

    def get_balances(self,type: const.BALANCE_TYPES ) -> Dict[Registrator_key,Dict]:
        match type:
            case 'daily':
                return self._balances_daily
            case 'monthly':
                return self._balances_monthly
        return {}

    def get_registrator_balance(self, key: Registrator_key, type: const.BALANCE_TYPES) -> Dict:
        match type:
            case 'daily':
                return self._balances_daily[key]
            case 'monthly':
                return self._balances_monthly[key]
        return {}

    async def _load_registrators(self) -> None:
        _LOGGER.debug("get _load_registrators")
        modems = await self.client.async_modems()
        _LOGGER.debug("responce - modems=%s",modems)
        async with lock:
            for m in modems:
                for ch_id, data in m['registrators'].items():
                    if ch_id != 'electro_event_log':
                        reg_key = Registrator_key(modem_id=m['modem_id'], channel_id=ch_id)
                        _LOGGER.debug("reg_key %s", reg_key)
                        self._registrators_raw[reg_key]={**data,**const.CHANELS_LIST[ch_id] }
                        self._registrators_raw[reg_key]['locality_name'] = m['tree_name']
                        self._registrators_raw[reg_key]['modem_id'] = m['modem_id']
                        self._registrators_raw[reg_key]['last_value_date'] = datetime.fromtimestamp(data['last_value_timestamp'])

    async def _fetch_balances(self):

        def _extract_balances(data_raw: Dict, output_dict: Dict):
            for ch_id, b in data_raw['balance'].items():
                if isinstance(b, dict):
                    for modem_id, val in b['data'].items():
                        _LOGGER.debug("modem_id: %s data=%s", modem_id, val)
                        if (ch_id != 'electro_ac_p_lsum_t3') and (ch_id != 'electro_ac_p_lsum_t4'):
                            reg_key = Registrator_key(modem_id=modem_id, channel_id=ch_id)
                            output_dict[reg_key] = {**val, **const.CHANELS_LIST[ch_id]}
                            output_dict[reg_key]['locality_name'] = data_raw['balance']['element_name']
                            output_dict[reg_key]['last_message_date'] = datetime.fromtimestamp(val['last_message_timestamp'])
                            output_dict[reg_key]['from'] = datetime.fromtimestamp(timestamp_from)
                            output_dict[reg_key]['to'] = datetime.fromtimestamp(timestamp_to)
            return

        _LOGGER.debug("_daily_balance")
        #daily
        start_of_day = datetime.combine(datetime.now().date(), time.min)
        timestamp_from = int(start_of_day.timestamp())
        timestamp_to = timestamp_from + (60*60*24)
        balances = await self.client.async_balances(timestamp_from, timestamp_to)
        _extract_balances(balances, self._balances_daily)
        _LOGGER.debug("resp _monthly_balances: %s", balances)
        #'monthly':
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        timestamp_from = int(start_of_month.timestamp())
        timestamp_to = int(datetime.now().timestamp())
        balances = await self.client.async_balances(timestamp_from, timestamp_to)
        _extract_balances(balances, self._balances_monthly)

    def get_registrator_raw( self, key: Registrator_key) -> Dict[Registrator_key,Any]:
            return self._registrators_raw[key]
