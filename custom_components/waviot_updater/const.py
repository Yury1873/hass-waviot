import datetime
from typing import Final,  Literal

DOMAIN = "waviot_updater"
ConfigKey = Literal[
    'api_key',
    'update_interval',
    'diagnostic_sensors',
    'power_tariff_1',
    'power_tariff_2',
    'power_tariff_3',
    'power_tariff_4',
]

CONF_API_KEY: ConfigKey = 'api_key'
CONF_UPDATE_INTERVAL: ConfigKey = "update_interval"
CONF_DIAGNOSTIC_SENSORS: ConfigKey  = "diagnostic_sensors"
CONF_POWER_TARIFF_1: ConfigKey = 'power_tariff_1'
CONF_POWER_TARIFF_2: ConfigKey = 'power_tariff_2'
CONF_POWER_TARIFF_3: ConfigKey = 'power_tariff_3'
CONF_POWER_TARIFF_4: ConfigKey = 'power_tariff_4'

CONF_TARIFFS_KEYS: Final = (CONF_POWER_TARIFF_1,CONF_POWER_TARIFF_2,CONF_POWER_TARIFF_3,CONF_POWER_TARIFF_4)

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
        'obis': '0100010801FF',
        'tariff_name': 'День',
        'tariff_id': 1,
        'tariff_descriptor': 'day',
        'description': 'Активная энергия к потребителю по сумме фаз, 1 tariff'
    },
    'electro_ac_p_lsum_t2': {
        'channel_id': 'electro_ac_p_lsum_t2',
        'obis': '0100010802FF',
        'tariff_name': 'Ночь',
        'tariff_id': 2,
        'tariff_descriptor': 'night',
        'description': 'Активная энергия к потребителю по сумме фаз, 2 тариф "ночь"'
    },
    'electro_ac_p_lsum_t3': {
        'channel_id': 'electro_ac_p_lsum_t3',
        'obis': '0100010803FF',
        'tariff_name': 'тариф 3',
        'tariff_id': 3,
        'tariff_descriptor': 'semi_peak_tariff_1',
        'description': 'Активная энергия к потребителю по сумме фаз, 3 тариф'
    },
    'electro_ac_p_lsum_t4': {
        'channel_id': 'electro_ac_p_lsum_t4',
        'obis': '0100010804FF',
        'tariff_name': 'тариф 4',
        'tariff_id': 4,
        'tariff_descriptor': 'tariff_zone_4',
        'description': 'Активная энергия к потребителю по сумме фаз, 4 тариф'
    },
    'electro_ac_p_lsum_tsum': {
        'channel_id': 'electro_ac_p_lsum_tsum',
        'obis': '0100010800FF',
        'tariff_name': 'Сумма',
        'tariff_id': 0,
        'tariff_descriptor': 'sum',
        'description': 'Активная энергия к потребителю по сумме фаз и тарифов'
    },
    'electro_event_log': {
        'channel_id': 'electro_event_log',
        'obis': None,
        'tariff_name': None,
        'tariff_id': None,
        'tariff_descriptor': None,
        'description': 'События'
    }
}


#CONF_DESC_POWER_TARRIFF_2: Final = "desc_power_tarriff_2"