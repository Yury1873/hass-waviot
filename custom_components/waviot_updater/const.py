import datetime
#from enum import IntFlag
from typing import Final, Literal

DOMAIN = "waviot_updater"
CONF_API_KEY: Final[str] = "api_key"

CONF_MODEM_ID = "modem_id"
#UPDATE_INTERVAL = 1200  # 20 minutes
DEFAULT_UPDATE_INTERVAL: Final = datetime.timedelta(minutes=20)
BASE_URL: Final = "https://lk.waviot.ru"
API_URL: Final = f"{BASE_URL}/api."

REQUIRED_KEYS_REGISTRATOR_RESP: Final = {
                                    "id",
                                    "name",
                                    "channel_id",
                                    "unit_id",
                                    "serial",
                                    "last_value",
                                    "last_value_timestamp",
                        }


CHANELS_LIST: Final = {
    'electro_ac_p_lsum_t1': {
        'channel_id': 'electro_ac_p_lsum_t1',
        'obis': '	0100010801FF',
        'tariff': 'День',
        'tariff_id': '1',
        'tariff_descriptor': 'day',
        'description': 'Активная энергия к потребителю по сумме фаз, 1 tariff'
    },
    'electro_ac_p_lsum_t2': {
        'channel_id': 'electro_ac_p_lsum_t2',
        'obis': '	0100010802FF',
        'tariff': 'Ночь',
        'tariff_id': '2',
        'tariff_descriptor': 'night',
        'description': 'Активная энергия к потребителю по сумме фаз, 2 тариф "ночь"'
    },
    'electro_ac_p_lsum_t3': {
        'channel_id': 'electro_ac_p_lsum_t3',
        'obis': '	0100010803FF',
        'tariff': 'тариф 3',
        'tariff_id': '3',
        'tariff_descriptor': 'semi_peak_tariff_1',
        'description': 'Активная энергия к потребителю по сумме фаз, 3 тариф'
    },
    'electro_ac_p_lsum_t4': {
        'channel_id': 'electro_ac_p_lsum_t4',
        'obis': '	0100010804FF',
        'tariff': 'тариф 4',
        'tariff_id': '4',
        'tariff_descriptor': 'tariff_zone_4',
        'description': 'Активная энергия к потребителю по сумме фаз, 4 тариф'
    },
    'electro_ac_p_lsum_tsum': {
        'channel_id': 'electro_ac_p_lsum_tsum',
        'obis': '0100010800FF',
        'tariff': 'Сумма тарифов',
        'tariff_descriptor': 'sum',
        'description': 'Активная энергия к потребителю по сумме фаз и тарифов'
    },
    'electro_event_log': {
        'channel_id': 'electro_event_log',
        'obis': None,
        'tariff': None,
        'tariff_id': None,
        'tariff_descriptor': None,
        'description': 'События'
    }
}


CONF_UPDATE_INTERVAL: Final = "update_interval"
CONF_DIAGNOSTIC_SENSORS: Final = "diagnostic_sensors"
CONF_RATES_SENSORS: Final = "rates_sensors"
CONF_POWER_TARRIFF_1: Final = "Тариф \"День\", стоимость kW/h"
CONF_POWER_TARRIFF_2: Final = "Тариф \"Ночь\", стоимость kW/h"
CONF_POWER_TARRIFF_3: Final = "Тариф \"Мультипиковый\", стоимость kW/h"
CONF_POWER_TARRIFF_4: Final = "Тариф \"Зональный\", стоимость kW/h"

#CONF_DESC_POWER_TARRIFF_2: Final = "desc_power_tarriff_2"