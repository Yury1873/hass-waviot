from collections import namedtuple
from typing import Literal

BALANCE_TYPES = Literal['daily', 'weekly', 'monthly']
Registrator_key = namedtuple('Registrator_key', ['modem_id', 'channel_id'])