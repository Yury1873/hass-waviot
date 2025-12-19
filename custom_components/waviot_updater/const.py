import datetime
from enum import IntFlag
from typing import Final, Literal

DOMAIN = "waviot_updater"
CONF_API_KEY = "api_key"
CONF_MODEM_ID = "modem_id"
UPDATE_INTERVAL = 1200  # 20 minutes
BASE_URL: Final = "https://lk.waviot.ru"
API_URL: Final = f"{BASE_URL}/api."
BALANCE_TYPES: Final = Literal['daily', 'weekly', 'monthly']
CHANELS_LIST: Final = {
    'electro_ac_p_lsum_t1': {
        'channel_id': 'electro_ac_p_lsum_t1',
        'obis': '	0100010801FF',
        'тариф': 'День',
        'tariff_id': '1',
        'tariff_descriptor': 'day',
        'description': 'Активная энергия к потребителю по сумме фаз, 1 тариф'
    },
    'electro_ac_p_lsum_t2': {
        'channel_id': 'electro_ac_p_lsum_t2',
        'obis': '	0100010802FF',
        'тариф': 'Ночь',
        'tariff_id': '2',
        'tariff_descriptor': 'night',
        'description': 'Активная энергия к потребителю по сумме фаз, 2 тариф "ночь"'
    },
    'electro_ac_p_lsum_t3': {
        'channel_id': 'electro_ac_p_lsum_t3',
        'obis': '	0100010803FF',
        'тариф': 'тариф 3',
        'tariff_id': '3',
        'tariff_descriptor': 'semi_peak_tariff_1',
        'description': 'Активная энергия к потребителю по сумме фаз, 3 тариф'
    },
    'electro_ac_p_lsum_t4': {
        'channel_id': 'electro_ac_p_lsum_t4',
        'obis': '	0100010804FF',
        'тариф': 'тариф 4',
        'tariff_id': '4',
        'tariff_descriptor': 'tariff_zone_4',
        'description': 'Активная энергия к потребителю по сумме фаз, 4 тариф'
    },
    'electro_ac_p_lsum_tsum': {
        'channel_id': 'electro_ac_p_lsum_tsum',
        'obis': '0100010800FF',
        'тариф': 'Сумма тарифов',
        'tariff_descriptor': 'sum',
        'description': 'Активная энергия к потребителю по сумме фаз и тарифов'
    },
    'electro_event_log': {
        'channel_id': 'electro_event_log',
        'obis': None,
        'тариф': None,
        'tariff_id': None,
        'tariff_descriptor': None,
        'description': 'События'
    }
}
