import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from homeassistant.util import slugify

class Account:
    def __init__(self,*args,**account_info):
        self.account_info = account_info