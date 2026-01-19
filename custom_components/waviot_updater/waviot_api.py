import logging
#import asyncio

#from collections import namedtuple
#import datetime
from datetime import time
from datetime import datetime
from typing import Dict, Any, List
from . import waviot_client, const, my_types

_LOGGER = logging.getLogger(__name__)

#_lock_registrators = asyncio.Lock()
#_lock_balances_daily = asyncio.Lock()
#_lock_balances_monthly = asyncio.Lock()



#############################
class WaviotApi:
    def __init__(self, client: waviot_client.WaviotClient) -> None:
        _LOGGER.debug("Initialize, api_key %s", client._api_key)
        self.client = client
        self._registrators: Dict[my_types.Registrator_key, Dict] = {}
        self._balances_daily: Dict[my_types.Registrator_key, Dict] = {}
        self._balances_monthly: Dict[my_types.Registrator_key, Dict] = {}

    @property
    async def settlement_name(self) -> str:
        return await self.client.get_settlement_name()

    async def async_fetch_all(self) -> None:
        """Fetch data."""
        await self.async_fetch_data()

    async def async_fetch_data(self) -> None:
        await self._load_registrators()
        await self._fetch_balances()

    async def _load_registrators(self) -> None:
        _LOGGER.debug("get _load_registrators")

        modems: List = await self.client.async_modems()
        #_LOGGER.debug('status %s', modems.get('status'))
        _LOGGER.debug("responce - modems=%s",modems)
        #async with _lock_registrators:
        for m in modems:
                last_values = await self.client.async_modems_channels_last_values(m['modem_id'])
                _LOGGER.debug("responce last values=%s", last_values)
                for ch_id, data in m['registrators'].items():
                    if ch_id != 'electro_event_log':
                        reg_key = my_types.Registrator_key(modem_id=m['modem_id'], channel_id=ch_id)
                        _LOGGER.debug("reg_key %s", reg_key)
                        assert const.REQUIRED_KEYS_REGISTRATOR_RESP <= data.keys() #убеждаемся что в ответе есть все необходимые поля
                        self._registrators[reg_key]={**data,**const.CHANELS_LIST[ch_id] }
                        self._registrators[reg_key]['locality_name'] = m['tree_name']
                        self._registrators[reg_key]['modem_id'] = m['modem_id']
                        self._registrators[reg_key]['last_value'] = last_values[reg_key]['value']
                        self._registrators[reg_key]['last_value_timestamp'] = last_values[reg_key]['timestamp']
                        self._registrators[reg_key]['last_value_date'] = datetime.fromtimestamp(self._registrators[reg_key]['last_value_timestamp'])


    #async def _upd_last_val_registrators():
      #      ...

    def get_registrator_raw( self, key: my_types.Registrator_key) -> Dict[my_types.Registrator_key,Any]:
        #with _lock_registrators:
            return self._registrators[key].copy()

    @property
    def registrators_raw(self) -> Dict[my_types.Registrator_key,Dict]:
         #with _lock_registrators:
            return self._registrators.copy()

    async def _fetch_balances(self):
        def _extract_balances(data_raw: Dict, output_dict: Dict):
            for ch_id, b in data_raw['balance'].items():
                if isinstance(b, dict):
                    for modem_id, val in b['data'].items():
                        _LOGGER.debug("modem_id: %s data=%s", modem_id, val)

                        if (ch_id != 'electro_ac_p_lsum_t3') and (ch_id != 'electro_ac_p_lsum_t4'):
                            reg_key = my_types.Registrator_key(modem_id=modem_id, channel_id=ch_id)
                            output_dict[reg_key] = {**val, **const.CHANELS_LIST[ch_id]}
                            output_dict[reg_key]['locality_name'] = data_raw['balance']['element_name']
                            output_dict[reg_key]['last_message_date'] = datetime.fromtimestamp(val['last_message_timestamp'])
                            output_dict[reg_key]['from'] = datetime.fromtimestamp(timestamp_from)
                            output_dict[reg_key]['to'] = datetime.fromtimestamp(timestamp_to)
            return

        _LOGGER.debug("_daily_balance")
        # daily balance
        start_of_day = datetime.combine(datetime.now().date(), time.min)
        timestamp_from = int(start_of_day.timestamp())
        timestamp_to = timestamp_from + (60*60*24)
        balances = await self.client.async_balances(timestamp_from, timestamp_to)
        #async with _lock_balances_daily:
        _extract_balances(balances, self._balances_daily)
        _LOGGER.debug("resp _monthly_balances: %s", balances)
        # monthly balance
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        timestamp_from = int(start_of_month.timestamp())
        timestamp_to = int(datetime.now().timestamp())
        balances = await self.client.async_balances(timestamp_from, timestamp_to)
        #async with _lock_balances_monthly:
        _extract_balances(balances, self._balances_monthly)

    def get_balances(self, balance_type: my_types.BALANCE_TYPES ) -> Dict[my_types.Registrator_key,Dict]:
        match balance_type:
            case 'daily':
                # with _lock_balances_daily:
                    return self._balances_daily.copy()
            case 'monthly':
               # with _lock_balances_monthly:
                    return self._balances_monthly.copy()
        return {}

    def get_registrator_balance(self, key: my_types.Registrator_key, balance_type: my_types.BALANCE_TYPES) -> Dict:
        match balance_type:
            case 'daily':
               # with _lock_balances_daily:
                    return self._balances_daily[key].copy()
            case 'monthly':
               # with _lock_balances_monthly:
                    return self._balances_monthly[key].copy()
        return {}