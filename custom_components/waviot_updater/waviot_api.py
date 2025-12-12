import asyncio
import logging
from collections import namedtuple
from datetime import datetime
from typing import Dict, List, Optional

from homeassistant.util import slugify
from . import waviot_client, const

_LOGGER = logging.getLogger(__name__)

#Modem=namedtuple('Modem','modem_id tree_name registrators')



class Modem:
    #__slots__ = ("id", "serial")

    def __init__(
        self,
        modem: waviot_client.Modem,
    ) -> None:

        self._modem_id = modem['modem_id']
        self._locality = modem['tree_name']
        self.registrators = modem['registrators']
        #self.serial = "serial"
        #self.subservice_id = "dfsf"
        #self.id = modem["id"]["registration"]
        #self.serial = modem["serial"]
        #self.subservice_id = modem["subserviceId"]
    @property
    def locality(self) ->str:
        return self._locality

    @property
    def modem_id(self) ->str:
        return self._modem_id

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + f"[modem_id={self.modem_id}, serial={self._locality}]"
        )

class Registrator:
    #__slots__ = ("id", "channel_id", "modem_id", "name","unit_id","serial","last_value","last_value_timestamp")

    def __init__(
        self,
        modem_id: str,
        raw_data
    ) -> None:
        self.registrator_id: str = raw_data['id']
        self.channel_id = raw_data['channel_id']
        self.modem_id: str = modem_id
        self.name = raw_data['name']
        self.unit_id = raw_data['unit_id']
        self.serial = raw_data['serial']
        self.last_value = raw_data['last_value']
        self.last_value_timestamp = raw_data['last_value_timestamp']
        #self.value = ind["previousReading"]
        #self.date = (
        #    datetime.strptime(ind["previousReadingDate"], "%d.%m.%Y").date()
        #    if ind["previousReadingDate"] is not None
        #    else None
        #self.unit = ind["unit"]
        #self.name = ind["scaleName"]
        #self.scale_id = ind["meterScaleId"]
        #self.account = account
        #self.Registrator = Registrator

    @property
    def id(self) -> str:
        #return f"{self.Registrator.id}_{self.scale_id}"
        return f"{self.Registrator.chanel_id}"

    @property
    def auto(self) -> bool:
        return self.account.type == "auto"

    def __repr__(self) -> str:
        return (
                self.__class__.__name__
                + f"[id={self.id}, channel_id={self.channel_id}, name={self.name}, "
                + f"unit_id={self.unit_id},modem serial={self.serial}, "
                + f"last_value={self.last_value}, last_value_timestamp={self.last_value_timestamp}]"
        )


#class Account:

#    account_info = {}
#    def __init__(self,*args,**account_info):
#        self.account_info = account_info

class WaviotApi:
    #_profile: Optional[pesc_client.Profile] = None
 #   _modems: List[Modem] = []

    #_groups: List[Group] = []
    #_tariffs: Dict[int, list[Tariff]] = {}
    #_subservices: Dict[int, pesc_client.Subservice] = {}

    def __init__(self, client: waviot_client.WaviotClient) -> None:
        _LOGGER.debug("Initialize, api_key %s", client._api_key)
        self.client = client
        self._profile = None
        self._modems: List[Modem] = []
        self._registrators: Dict[str, waviot_client.Modem] = {}
        self._load_modems()

    @property
    async def settlement_name(self) -> str:
        return await self.client.get_settlement_name()

    async def _load_modems(self):
        _LOGGER.debug("get async_modems")
        modems = await self.client.async_modems()
        for m in modems:
         #   mod: Modem = Modem(**m)
          #  self._modems.append(Modem(**m))
            _LOGGER.debug("rsv modem=%s",(m))
        for m in modems:
            self._modems.append( Modem( m ) )
        #for key_dev, val_dev in element_info['devices'].items():
        #    _LOGGER.debug("Init modems: modem id - %s", val_dev['modem_id'])
        #    self._modems[val_dev['modem_id']] = val_dev
            #print("Data received device: ", val_dv['modem_id'])
            #for reg_key, reg_val in val_dv['registrators'].items():
            #    print("registrator: ", reg_val)
            #for modem in modems:
             #
            #for met_ind in meter["indications"]:
            #    ind = MeterInd(acc, met, met_ind)
            #    self._meters.append(ind)
            #    _LOGGER.debug("Got %s", ind)

    async def async_fetch_all(self) -> None:
        """Fetch profile and data."""
        #await self.async_fetch_profile()
        await self.async_fetch_data()

    async def async_fetch_profile(self) -> None:
            _LOGGER.debug("Fetch profile")
            #self._profile = None
            self._profile = await self.client.async_profile()

    async def async_fetch_data(self) -> None:
       await self._load_modems()

    @property
    def modems(self) -> List[Modem]:
        """
        Returns meters without duplicates. A values with an older account will be skipped.
        """
        #_LOGGER.debug("api modems: %s",self._modems )
        #modems: dict[str, Modem] = {}
        #for modem in sorted(self._modems, key=lambda x: f"{x.modem_id}"):
         #   modems[modem.id] = modem
        return self._modems
        #return list(modems.values())