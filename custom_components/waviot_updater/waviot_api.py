import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from homeassistant.util import slugify
from . import waviot_client, const

class Account:
    account_info = {}
    def __init__(self,*args,**account_info):
        self.account_info = account_info

class WaviotApi:
    #_profile: Optional[pesc_client.Profile] = None
    #_meters: List[MeterInd] = []
    #_groups: List[Group] = []
    #_tariffs: Dict[int, list[Tariff]] = {}
    #_subservices: Dict[int, pesc_client.Subservice] = {}

    def __init__(self, client: waviot_client.WaviotClient) -> None:
        # _LOGGER.debug("Initialize %s", client.token)
        self.client = client
