# sensor.py - Fixed subscriptable error, modernized to use SensorEntity and CoordinatorEntity, added device_info

import logging
import re
from typing import Callable, Any, Dict
from homeassistant.components import sensor
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import (
    HomeAssistant,
    callback
)
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo #, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from . import WaviotDataUpdateCoordinator, const, waviot_api, waviot_client, my_types

_LOGGER = logging.getLogger(__name__)

################################
async def async_setup_entry(
            hass: HomeAssistant, entry: ConfigEntry,
            async_add_entities: Callable
):
    _LOGGER.debug("Setup %s ", entry.title)
    coord: WaviotDataUpdateCoordinator = hass.data[const.DOMAIN][entry.entry_id]
    sensors = []

    for key, registrator_raw in coord.api.registrators_raw.items():
        _LOGGER.debug('registrator_raw: %s', registrator_raw)
        sensors.append( WaviotRegistratorSensor( coord,  registrator_raw))
        ## дневные балансы ##
        sensors.append( WaviotBalanceMonetarySensor_v2 ( coord, registrator_raw, balance_type='daily'))
        ## месячные балансы ##
        sensors.append( WaviotBalanceMonetarySensor_v2 ( coord, registrator_raw, balance_type='monthly'))

    for vl in coord.api.get_balances(balance_type='daily').values():
        _LOGGER.debug('daily_balances_raw: %s', vl)
        sensors.append( WaviotBalanceSensor( coord,  balance_data=vl, balance_type='daily'))

    for vl in coord.api.get_balances(balance_type='monthly').values():
        _LOGGER.debug('monthly_balances_raw: %s', vl)
        sensors.append( WaviotBalanceSensor( coord,  balance_data=vl, balance_type='monthly'))


    async_add_entities( sensors)

################################
class _WaviotBaseSensor(
    CoordinatorEntity[WaviotDataUpdateCoordinator], sensor.SensorEntity
):
    def __init__(
        self,
        coordinator: WaviotDataUpdateCoordinator,
#        entry: ConfigEntry,
        unique_id: str,
        name: str,
        model: str,
    ):
        super().__init__(coordinator)
        entry = coordinator.config_entry
        _LOGGER.debug("Initialize %s for %s", self.__class__.__name__, entry.title)
        self._attr_unique_id = unique_id
        self._attr_device_info =  DeviceInfo(
                configuration_url=waviot_client.WaviotClient.BASE_URL,
                #connections={},
                entry_type=DeviceEntryType.SERVICE,
                identifiers={(const.DOMAIN, entry.entry_id)},
                #manufacturer=self.coordinator.api.profile_name,
                model=model,
                name=name,
                # sw_version="",
                # hw_version="",
            )
        self.entity_id = f"sensor.{self._attr_unique_id}"

    @staticmethod
    def validate_obis( in_obis: str) -> str:
        pattern = r'[0-9A-F]{12}'
        match = re.search(pattern, in_obis)
        if match:
            return match.group(0)  # Полная найденная строка
        return ''

    @property
    def api(self) -> waviot_api.WaviotApi:
        return self.coordinator.api

################################
class WaviotRegistratorSensor(_WaviotBaseSensor):
    _attr_state_class = sensor.SensorStateClass.TOTAL_INCREASING
    _attr_has_entity_name = True
    #_attr_supported_features = 0
    _attr_translation_key = "meter"

    def __init__(
        self,
        coordinator: WaviotDataUpdateCoordinator,
        #registrator: waviot_api.Registrator,
        registrator_raw: Dict[str, Any],
        id_suffix: str = ''
    ):
        super().__init__(
            coordinator = coordinator,
            unique_id=f"waviot_{registrator_raw['modem_id']}_{self.validate_obis(registrator_raw['obis'])}_{registrator_raw['tariff_descriptor']}",
            name = registrator_raw['locality_name'],
            model = f"modem ID: {registrator_raw['modem_id']}"
        )
        self._registrator_raw = registrator_raw
        self._registrator_key: my_types.Registrator_key = my_types.Registrator_key(modem_id=registrator_raw['modem_id'],
                                                                                       channel_id=registrator_raw['channel_id'])
        self._update_state_attributes()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        _LOGGER.debug("_handle_coordinator_update WaviotRegistratorSensor")
        self._registrator_raw = self.coordinator.api.get_registrator_raw( self._registrator_key)
        self.coordinator.last_update_success = True
        super()._handle_coordinator_update()

    def _update_state_attributes(self):
        _LOGGER.debug("_update_state_attributes WaviotRegistratorSensor")
        self._attr_device_class = sensor.SensorDeviceClass.ENERGY
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_name = f'Показания "{self._registrator_raw["tariff_name"]}"'
        self._attr_extra_state_attributes = self._registrator_raw

    @property
    def native_value(self) -> int:
        """Return the value of the sensor."""
        return self._registrator_raw['last_value']

    @property
    def assumed_state(self) -> bool:
        return not self.coordinator.last_update_success

    @property
    def available(self) -> bool:
        return True

    #def __str__(self):
    #    return f"{self._registrator_raw.last_value}"

################################
class WaviotBalanceSensor(_WaviotBaseSensor):
    _attr_state_class = sensor.SensorStateClass.TOTAL_INCREASING
    _attr_device_class = sensor.SensorDeviceClass.ENERGY
    _attr_has_entity_name = True
    _attr_translation_key = "meter"


    def __init__(
        self,
        coordinator: WaviotDataUpdateCoordinator,
        balance_data: Dict[str, Any],
        balance_type: my_types.BALANCE_TYPES,
    ):
        super().__init__(
            coordinator = coordinator,
            unique_id = f"waviot_{balance_data['serial']}_{self.validate_obis(balance_data['obis'])}_balance_{balance_type}",
            name = balance_data['locality_name'],
            model = f"modem ID: {balance_data['modem_id']}"
        )
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self.balance = balance_data
        self._balance_type: my_types.BALANCE_TYPES  = balance_type
        self._registrator_key: my_types.Registrator_key = my_types.Registrator_key(
                                                                        modem_id=balance_data['modem_id'],
                                                                        channel_id=balance_data['channel_id']
                                                            )
        self._update_state_attributes()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        _LOGGER.debug("_handle_coordinator_update WaviotBalanceSensor")
        self.balance = self.coordinator.api.get_registrator_balance(self._registrator_key,self._balance_type)
        self.coordinator.last_update_success = True
        super()._handle_coordinator_update()

    def _update_state_attributes(self):
        _LOGGER.debug(" _update_state_attributes WaviotBalanceSensor")
        match self._balance_type:
            case "daily":
                self._attr_name = f'Текущие сутки, "{self.balance['tariff_name']}"'
            case "weekly":
                self._attr_name = f'Текущая неделя, "{self.balance['tariff_name']}"'
            case "monthly":
                self._attr_name = f'Текущий месяц, "{self.balance['tariff_name']}"'
        self._attr_extra_state_attributes = self.balance

    @property
    def native_value(self) -> float:
        """Return the value of the sensor."""
        return self.balance["diff"]

    @property
    def assumed_state(self) -> bool:
        return not self.coordinator.last_update_success

    @property
    def available(self) -> bool:
        return True

    #def __str__(self):
    #    return f"{self.balance.last_value}"
    ################################
        ################################
class WaviotBalanceMonetarySensor_v2(_WaviotBaseSensor):
        # _attr_state_class = sensor.SensorStateClass.TOTAL_INCREASING
        _attr_state_class = sensor.SensorStateClass.TOTAL
        _attr_device_class = sensor.SensorDeviceClass.MONETARY
        _attr_native_unit_of_measurement = "RUB"
        _attr_has_entity_name = True
        _attr_translation_key = "meter"

        def __init__(
                self,
                coordinator: WaviotDataUpdateCoordinator,
                registrator_data: dict[str, any],
                balance_type: my_types.BALANCE_TYPES,
        ):
            super().__init__(
                coordinator=coordinator,
                # unique_id = f"{const.DOMAIN}_{balance_data['serial']}_{self.validate_obis(balance_data['obis'])}_{balance_type}_balance_money",
                unique_id=f"waviot_{registrator_data['serial']}_{registrator_data['obis']}_mnt_bln_{balance_type}",
                name=registrator_data['locality_name'],
                model=f"modem ID: {registrator_data['modem_id']}"
            )
            #self.last_reset = None
            self._reg_data: dict[str, any] = registrator_data
            #self.balance = balance_data
            self._balance_type: my_types.BALANCE_TYPES = balance_type
            self._registrator_key: my_types.Registrator_key = my_types.Registrator_key(
                modem_id=self._reg_data['modem_id'],
                channel_id=self._reg_data['channel_id']
            )
            self._balance_dict_key =f"balance_{balance_type}"
            self._reg_data['tariff'] = 0.0
            match self._reg_data['tariff_id']:
                case 1:
                    if const.CONF_POWER_TARRIFF_1 in self.coordinator.config_entry.options:
                        self._reg_data['tariff'] = self.coordinator.config_entry.options[const.CONF_POWER_TARRIFF_1]
                case 2:
                    if const.CONF_POWER_TARRIFF_2 in self.coordinator.config_entry.options:
                        self._reg_data['tariff'] = self.coordinator.config_entry.options[const.CONF_POWER_TARRIFF_2]
                case 3:
                    if const.CONF_POWER_TARRIFF_3 in self.coordinator.config_entry.options:
                        self._reg_data['tariff'] = self.coordinator.config_entry.options[const.CONF_POWER_TARRIFF_3]
                case 4:
                    if const.CONF_POWER_TARRIFF_4 in self.coordinator.config_entry.options:
                        self._reg_data['tariff'] = self.coordinator.config_entry.options[const.CONF_POWER_TARRIFF_4]
            self._update_state_attributes()

        @callback
        def _handle_coordinator_update(self) -> None:
            """Handle data update."""
#            self.balance = self.coordinator.api.get_registrator_balance(self._registrator_key, self._balance_type)
            self._reg_data = self.coordinator.api.get_registrator_raw(self._registrator_key)
            self._reg_data['tariff'] = 0.0
            match self._reg_data['tariff_id']:
                case 1:
                    if const.CONF_POWER_TARRIFF_1 in self.coordinator.config_entry.options:
                        self._reg_data['tariff'] = self.coordinator.config_entry.options[const.CONF_POWER_TARRIFF_1]
                case 2:
                    if const.CONF_POWER_TARRIFF_2 in self.coordinator.config_entry.options:
                        self._reg_data['tariff'] = self.coordinator.config_entry.options[const.CONF_POWER_TARRIFF_2]
                case 3:
                    if const.CONF_POWER_TARRIFF_3 in self.coordinator.config_entry.options:
                        self._reg_data['tariff'] = self.coordinator.config_entry.options[const.CONF_POWER_TARRIFF_3]
                case 4:
                    if const.CONF_POWER_TARRIFF_4 in self.coordinator.config_entry.options:
                        self._reg_data['tariff'] = self.coordinator.config_entry.options[const.CONF_POWER_TARRIFF_4]
            self._update_state_attributes()
            self.coordinator.last_update_success = True
            super()._handle_coordinator_update()

        def _update_state_attributes(self):
            _LOGGER.debug(" _update_state_attributes WaviotBalanceMonetarySensor")
            match self._balance_type:
                case "daily":
                    self._attr_name = f'Cутки, "{self._reg_data['tariff_name']}"'
                case "weekly":
                    self._attr_name = f'Неделя,  "{self._reg_data['tariff_name']}"'
                case "monthly":
                    self._attr_name = f'Mесяц, "{self._reg_data['tariff_name']}"'
            balance_attr: dict = {}
            balance_attr['obis'] = self._reg_data['obis']
            balance_attr['tariff'] = self._reg_data['tariff']
            if self._balance_dict_key in self._reg_data:
                for key, val in self._reg_data[self._balance_dict_key].items():
                    balance_attr[key] = val
            self._attr_extra_state_attributes = balance_attr

        def get_tariff(self, indx: int) -> float:
            match indx:
                case 1:
                    if const.CONF_POWER_TARRIFF_1 in self.coordinator.config_entry.options:
                        return self.coordinator.config_entry.options[const.CONF_POWER_TARRIFF_1]
                    else:
                        return 0.0
                case 2:
                    if const.CONF_POWER_TARRIFF_2 in self.coordinator.config_entry.options:
                        return self.coordinator.config_entry.options[const.CONF_POWER_TARRIFF_2]
                    else:
                        return 0.0
                case 3:
                    if const.CONF_POWER_TARRIFF_3 in self.coordinator.config_entry.options:
                        return self.coordinator.config_entry.options[const.CONF_POWER_TARRIFF_3]
                    else:
                        return 0.0
                case 4:
                    if const.CONF_POWER_TARRIFF_4 in self.coordinator.config_entry.options:
                        return self.coordinator.config_entry.options[const.CONF_POWER_TARRIFF_4]
                    else:
                        return 0.0

            return 0,0

        @property
        def native_value(self) -> float:
            """Return the value of the sensor."""
            ret_val = 0.0
            if self._balance_dict_key in self._reg_data:
                if self._reg_data['tariff_id']==0:
                    for k,v in self._reg_data[self._balance_dict_key].items():
                        if isinstance(v, dict) and not (k == 0):
                            ret_val = ret_val + v['diff']*self.get_tariff(k)
                else:
                    ret_val = self._reg_data[self._balance_dict_key]['diff']*self.get_tariff(self._reg_data['tariff_id'])
           # if 'tariff' in self._reg_data:
           #     tariff = self._reg_data['tariff']
            return ret_val

        @property
        def assumed_state(self) -> bool:
            return not self.coordinator.last_update_success

        @property
        def available(self) -> bool:
            return True