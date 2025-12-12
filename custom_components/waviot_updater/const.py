import datetime
from enum import IntFlag
from typing import Final

DOMAIN = "waviot_updater"
CONF_API_KEY = "api_key"
CONF_MODEM_ID = "modem_id"
UPDATE_INTERVAL = 1200  # 20 minutes
BASE_URL: Final = "https://lk.waviot.ru"
API_URL: Final = f"{BASE_URL}/api."
CHANELS_LIST: Final = {
    'electro_ac_p_lsum_t1': {
        'chanel_id': 'electro_ac_p_lsum_t1',
        'description': 'Активная энергия к потребителю по сумме фаз, 1 тариф'
    },
    'electro_ac_p_lsum_t2': {
        'chanel_id': 'electro_ac_p_lsum_t2',
        'description': 'Активная энергия к потребителю по сумме фаз, 2 тариф'
    },
    'electro_ac_p_lsum_t3': {
        'chanel_id': 'electro_ac_p_lsum_t3',
        'description': 'Активная энергия к потребителю по сумме фаз, 3 тариф'
    },
    'electro_ac_p_lsum_t4': {
        'chanel_id': 'electro_ac_p_lsum_t4',
        'description': 'Активная энергия к потребителю по сумме фаз, 4 тариф'
    },
    'electro_ac_p_lsum_tsum': {
        'chanel_id': 'electro_ac_p_lsum_tsum',
        'description': 'Активная энергия к потребителю по сумме фаз и тарифов'
    },
    'electro_event_log': {
        'chanel_id': 'electro_event_log',
        'description': 'События'
    }
}
