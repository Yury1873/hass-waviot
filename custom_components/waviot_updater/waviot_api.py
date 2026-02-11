import logging
#import asyncio
import re

#from collections import namedtuple
#import datetime
from datetime import time
#import time
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
        #self._balances_daily: Dict[my_types.Registrator_key, Dict] = {}
        #self._balances_monthly: Dict[my_types.Registrator_key, Dict] = {}
        self._last_date_timestamp: int = 0
    @property
    async def settlement_name(self) -> str:
        return await self.client.get_settlement_name()

    @staticmethod
    def validate_obis( in_obis: str) -> str:
        pattern = r'[0-9A-F]{12}'
        match = re.search(pattern, in_obis)
        if match:
            return match.group(0)  # Полная найденная строка
        return ''
    async def async_fetch_all(self) -> None:
        """Fetch data."""
    #    await self.async_fetch_data()
        delta_time =  datetime.now().timestamp() - self._last_date_timestamp
        if delta_time > (3600 + 300):  #не долбим запросами, если прошло меньше часа(+5 мин, т.к. бесполезно перв. 5 мин. ждать обн.)
            _LOGGER.debug(" fetch all data. Delta time %i", delta_time)
            await self._load_registrators()
            await self._fetch_balances()
        else:
            _LOGGER.debug("skip fetch data. Delta time %i", delta_time)


   # async def async_fetch_data(self) -> None:


    async def _load_registrators(self) -> None:
        _LOGGER.debug("get _load_registrators")
        modems: List = await self.client.async_modems()
        #_LOGGER.debug('status %s', modems.get('status'))
        _LOGGER.debug("responce - modems=%s",modems)
        #async with _lock_registrators:
        for m in modems:
                #получаем последние данные по modem_id
                last_values = await self.client.async_modems_channels_last_values(m['modem_id'])
                _LOGGER.debug("responce last values=%s", last_values)
                for ch_id, data in m['registrators'].items():
                    if ch_id != 'electro_event_log':
                        reg_key = my_types.Registrator_key(modem_id=m['modem_id'], channel_id=ch_id)
                        _LOGGER.debug("reg_key %s", reg_key)
                        assert const.REQUIRED_KEYS_REGISTRATOR_RESP <= data.keys() #убеждаемся что в ответе есть все необходимые поля
                        self._registrators[reg_key]={**data,**const.CHANELS_LIST[ch_id] }
                        self._registrators[reg_key]['active'] = True
                        self._registrators[reg_key]['locality_name'] = m['tree_name']
                        self._registrators[reg_key]['modem_id'] = m['modem_id']
                        #obis_str = self.validate_obis(self._registrators[reg_key]['obis'])
                        #obis_str = self._registrators[reg_key]['obis']
                        #obis_int = int(self._registrators[reg_key]['obis'], 16)
                        #self._registrators[reg_key]['obis'] = obis_str
                        self._registrators[reg_key]['obis_int'] = int(self._registrators[reg_key]['obis'], 16)
                        self._registrators[reg_key]['last_value'] = last_values[reg_key]['value']
                        self._registrators[reg_key]['last_value_timestamp'] = last_values[reg_key]['timestamp']
                        self._registrators[reg_key]['last_value_date'] = datetime.fromtimestamp(self._registrators[reg_key]['last_value_timestamp'])
                        self._last_date_timestamp = last_values[reg_key]['timestamp']


    def get_registrator_raw( self, key: my_types.Registrator_key) -> Dict[my_types.Registrator_key,Any]:
        #with _lock_registrators:
            return self._registrators[key].copy()

    @property
    def registrators_raw(self) -> Dict[my_types.Registrator_key,Dict]:
         #with _lock_registrators:
            return self._registrators.copy()

    def registrator_is_active(self,reg_key: my_types.Registrator_key) ->bool:
        if ( (reg_key in self._registrators)  and (self._registrators[reg_key]['active'] == True)):
            _LOGGER.debug(f"registrator_is_active True, status: {self._registrators[reg_key]['active']} , key: {reg_key}")
            return True
        _LOGGER.debug("registrator_is_active False")
        return False

    async def _fetch_balances(self):
        #def _extract_balances(data_raw: Dict, output_dict: Dict,balance_type: str):
        def _extract_balances(data_raw: Dict, balance_type: str):
            balances: dict[int, dict] = {}
            for ch_id, b in data_raw['balance'].items():
                if  (isinstance(b, dict)) and (ch_id in [
                                                    "electro_ac_p_lsum_t1",
                                                    "electro_ac_p_lsum_t2",
                                                    "electro_ac_p_lsum_t3",
                                                    "electro_ac_p_lsum_t4",
                                                    "electro_ac_p_lsum_tsum"]):
                    for modem_id, val in b['data'].items():
                                _LOGGER.debug("modem_id: %s data=%s", modem_id, val)
                        #if ch_id in ["electro_ac_p_lsum_t1","electro_ac_p_lsum_t2","electro_ac_p_lsum_tsum"]:
                                reg_key = my_types.Registrator_key(modem_id=modem_id, channel_id=ch_id)
                                if (not reg_key in self._registrators) or (self._registrators[reg_key]['active']==False):
                                    continue
                                #output_dict[reg_key] = {**val, **const.CHANELS_LIST[ch_id]}
                                #при переходе суток/месяца, сервер возвращает баланс за весь период измерений а не за запрашиваемый период
                                #охоже это происходит когда еще нет расчитанного баланса по запрашиваемому периоду
                                #соотв. банально обнуляем баланс чтобы не искажать реальность....
                                if val['start'] == 0:
                                    val['start'] = val['end']
                                    val['diff'] = 0
                                #output_dict[reg_key]['start'] = round(val['start'],2)
                                #output_dict[reg_key]['end'] = round(val['end'],2)
                                #output_dict[reg_key]['diff'] = round(val['diff'],2)
                                #output_dict[reg_key]['locality_name'] = data_raw['balance']['element_name']
                                #output_dict[reg_key]['last_message_date'] = datetime.fromtimestamp(
                                #val['last_message_timestamp'])
                                #output_dict[reg_key]['from'] = datetime.fromtimestamp(timestamp_from)
                                #output_dict[reg_key]['to'] = datetime.fromtimestamp(timestamp_to)

                                tariff_id = self._registrators[reg_key]['tariff_id']
                                self._registrators[reg_key][balance_type] = {}
                                for k in ['start', 'end', 'diff']:
                                    self._registrators[reg_key][balance_type][k] = round(val[k], 2)
                                    if tariff_id not in balances:
                                        balances[tariff_id]={}
                                    balances[tariff_id][k]= round(val[k],2)
                                #если это сумма тарифов тогда добавляем инфо по входящим в сумму тарифам
                                if tariff_id == 0:
                                    _LOGGER.debug(f"balances ={balances}")
                                    for t_id, v in balances.items():
                                        self._registrators[reg_key][balance_type][t_id]=v
            return

        _LOGGER.debug("_daily_balance")
        # daily balance
        start_of_day = datetime.combine(datetime.now().date(), time.min)
        timestamp_from = int(start_of_day.timestamp())
        timestamp_to = timestamp_from + (60*60*24)
        balances = await self.client.async_balances(timestamp_from, timestamp_to)
        #async with _lock_balances_daily:
        #_extract_balances(balances, self._balances_daily,'balance_daily')
        _extract_balances(balances,'balance_daily')
        _LOGGER.debug("resp _monthly_balances: %s", balances)
        # monthly balance
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        timestamp_from = int(start_of_month.timestamp())
        timestamp_to = int(datetime.now().timestamp())
        balances = await self.client.async_balances(timestamp_from, timestamp_to)
        #async with _lock_balances_monthly:
        _extract_balances(balances,'balance_monthly')

#    def get_balances(self, balance_type: my_types.BALANCE_TYPES ) -> Dict[my_types.Registrator_key,Dict]:
#        match balance_type:
#            case 'daily':
#                # with _lock_balances_daily:
#                    return self._balances_daily.copy()
#            case 'monthly':
#               # with _lock_balances_monthly:
#                    return self._balances_monthly.copy()
#        return {}

#    def get_registrator_balance(self, key: my_types.Registrator_key, balance_type: my_types.BALANCE_TYPES) -> Dict:
#        match balance_type:
#            case 'daily':
#               # with _lock_balances_daily:
#                    return self._balances_daily[key].copy()
#            case 'monthly':
#               # with _lock_balances_monthly:
#                    return self._balances_monthly[key].copy()
#        return {}