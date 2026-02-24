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
        sensors.append( WaviotBalanceSensor_v2 ( coord, registrator_raw, balance_type='daily'))
        sensors.append( WaviotBalanceMonetarySensor_v2 ( coord, registrator_raw, balance_type='daily'))
        ## месячные балансы ##
        sensors.append( WaviotBalanceSensor_v2 ( coord, registrator_raw, balance_type='monthly'))
        sensors.append( WaviotBalanceMonetarySensor_v2 ( coord, registrator_raw, balance_type='monthly'))
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
        #self._attr_available=False
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
    ):
        super().__init__(
            coordinator = coordinator,
            unique_id=
                (f"waviot_{registrator_raw['modem_id']}_{self.validate_obis(registrator_raw['obis'])}_{registrator_raw['tariff_descriptor']}").lower(),
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
class WaviotBalanceSensor_v2(_WaviotBaseSensor):
    # _attr_state_class = sensor.SensorStateClass.TOTAL_INCREASING
    _attr_state_class = sensor.SensorStateClass.TOTAL
    _attr_device_class = sensor.SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = "kWh"
    _attr_has_entity_name = True
    _attr_translation_key = "meter"

    def __init__(
                self,
                coordinator: WaviotDataUpdateCoordinator,
                registrator_data: dict[str, Any],
                balance_type: my_types.BALANCE_TYPES,
                uniq_id: str=None
        ):
            if uniq_id is None:
                uniq_id=f"waviot_{registrator_data['serial']}_{registrator_data['obis']}_balance_{balance_type}"

            super().__init__(
                coordinator=coordinator,
                unique_id=uniq_id.lower(),
                name=registrator_data['locality_name'],
                model=f"modem ID: {registrator_data['modem_id']}"
            )

            #self.last_reset = None
            self._reg_data: dict[str, Any] = registrator_data
            self._balance_type: my_types.BALANCE_TYPES = balance_type
            self._registrator_key: my_types.Registrator_key = my_types.Registrator_key(
                modem_id = self._reg_data['modem_id'],
                channel_id = self._reg_data['channel_id']
            )
            self._balance_dict_key = f"balance_{balance_type}"
            self._reg_data['tariff'] = self.get_tariff(self._reg_data['tariff_id'])
            self._update_state_attributes()

    @callback
    def _handle_coordinator_update(self) -> None:
            """Handle data update."""
#            self.balance = self.coordinator.api.get_registrator_balance(self._registrator_key, self._balance_type)
            self._reg_data = self.coordinator.api.get_registrator_raw(self._registrator_key)
            self._reg_data['tariff']=self.get_tariff(self._reg_data['tariff_id'])
            self._attr_available = False  # или self._attr_state = STATE_UNAVAILABLE
            #self.async_write_ha_state()
            _LOGGER.debug(f"self.available= {self.available}")
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
            balance_attr = {
                'obis':  self._reg_data['obis'],
                'tariff': self._reg_data['tariff'],
            }
            if self._balance_dict_key in self._reg_data:

                for key, val in self._reg_data[self._balance_dict_key].items():
                    _LOGGER.debug(f"init attr key: {key} value: {val} ")
                    balance_attr[key] = val

            _LOGGER.debug(f"balance_attr: {balance_attr}")
            self._attr_extra_state_attributes = balance_attr

    def get_tariff(self, indx: int) -> float:
            if (indx < 1) and (indx > 5):
                return 0.0
            tariff_key=const.CONF_TARIFFS_KEYS[indx-1]
            _LOGGER.debug(f"tariff_key: {tariff_key}")
            if tariff_key in self.coordinator.config_entry.options:
                _LOGGER.debug(f"tariff_key=: {self.coordinator.config_entry.options[tariff_key]}")
                return self.coordinator.config_entry.options[tariff_key]
            else:
                return 0.0

    @property
    def native_value(self) -> float:
            """Return the value of the sensor."""
            ret_val = self._reg_data[self._balance_dict_key]['diff']
            return ret_val

    @property
    def assumed_state(self) -> bool:
            return not self.coordinator.last_update_success

    @property
    def available(self) -> bool:
            return True

        # def __str__(self):
        #    return f"{self.balance.last_value}"

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
                registrator_data: dict[str, Any],
                balance_type: my_types.BALANCE_TYPES,
        ):
            super().__init__(
                coordinator=coordinator,
                # unique_id = f"{const.DOMAIN}_{balance_data['serial']}_{self.validate_obis(balance_data['obis'])}_{balance_type}_balance_money",
                unique_id=(f"waviot_{registrator_data['serial']}_{registrator_data['obis']}_monetary_balance_{balance_type}").lower(),
                name=registrator_data['locality_name'],
                model=f"modem ID: {registrator_data['modem_id']}"
            )
            #self._attr_available = False
            self._reg_data: dict[str, Any] = registrator_data
            #self.balance = balance_data
            self._balance_type: my_types.BALANCE_TYPES = balance_type
            self._registrator_key: my_types.Registrator_key = my_types.Registrator_key(
                modem_id=self._reg_data['modem_id'],
                channel_id=self._reg_data['channel_id']
            )
            self._balance_dict_key =f"balance_{balance_type}"
            self._reg_data['tariff']=self.get_tariff(self._reg_data['tariff_id'])
            self._update_state_attributes()

    @callback
    def _handle_coordinator_update(self) -> None:
            """Handle data update."""
#            self.balance = self.coordinator.api.get_registrator_balance(self._registrator_key, self._balance_type)
            self._reg_data = self.coordinator.api.get_registrator_raw(self._registrator_key)
            self._reg_data['tariff']=self.get_tariff(self._reg_data['tariff_id'])
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
            balance_attr = {
                    'obis':  self._reg_data['obis'],
                    'tariff':  self._reg_data['tariff'],
            }
            if self._balance_dict_key in self._reg_data:
                for key, val in self._reg_data[self._balance_dict_key].items():
                    balance_attr[key] = val
            self._attr_extra_state_attributes = balance_attr

    def get_tariff(self, indx: int) -> float:
            if (indx < 1) and (indx > 5):
                return 0.0
            tariff_key=const.CONF_TARIFFS_KEYS[indx-1]
            _LOGGER.debug(f"tariff_key: {tariff_key}")
            if tariff_key in self.coordinator.config_entry.options:
                _LOGGER.debug(f"tariff_key=: {self.coordinator.config_entry.options[tariff_key]}")
                return self.coordinator.config_entry.options[tariff_key]
            else:
                return 0.0

    @property
    def native_value(self) -> float:
            """Return the value of the sensor."""
            ret_val = 0.0
            if self._balance_dict_key in self._reg_data:
                if self._reg_data['tariff_id']==0: #если сумма тарифов
                    for k,v in self._reg_data[self._balance_dict_key].items():
                        if isinstance(v, dict) and not (k == 0):
                            ret_val = ret_val + v['diff']*self.get_tariff(k)
                else:
                    ret_val = self._reg_data[self._balance_dict_key]['diff']*self.get_tariff(self._reg_data['tariff_id'])
            return ret_val

    @property
    def assumed_state(self) -> bool:
            return not self.coordinator.last_update_success

    @property
    def available(self) -> bool:
            return True

        # def __str__(self):
        #    return f"{self.balance.last_value}"