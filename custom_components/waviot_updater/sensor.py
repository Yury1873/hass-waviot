# sensor.py - Fixed subscriptable error, modernized to use SensorEntity and CoordinatorEntity, added device_info

import logging
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
        sensors.append( WaviotRegistratorSensor( coord, registrator_raw))

    for vl in coord.api.get_balances(balance_type='daily').values():
        _LOGGER.debug('daily_balances_raw: %s', vl)
        sensors.append( WaviotBalanceSensor( coord, balance_data=vl, balance_type='daily'))

    for vl in coord.api.get_balances(balance_type='monthly').values():
        _LOGGER.debug('monthly_balances_raw: %s', vl)
        sensors.append( WaviotBalanceSensor( coord, balance_data=vl, balance_type='monthly'))
    async_add_entities( sensors)

################################
class _WaviotBaseSensor(
    CoordinatorEntity[WaviotDataUpdateCoordinator], sensor.SensorEntity
):
    def __init__(
        self,
        coordinator: WaviotDataUpdateCoordinator,
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
            unique_id=f"waviot_{registrator_raw['modem_id']}_{registrator_raw['obis']}_{registrator_raw['tariff_descriptor']}-{id_suffix}",
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
        self._attr_name = f'Показания "{self._registrator_raw["tariff"]}"'
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
    _attr_has_entity_name = True
    #_attr_supported_features = 0
    _attr_translation_key = "meter"

    def __init__(
        self,
        coordinator: WaviotDataUpdateCoordinator,
        balance_data: Dict[str, Any],
        balance_type: my_types.BALANCE_TYPES,
    ):
        super().__init__(
            coordinator = coordinator,
            unique_id = f"{const.DOMAIN}_{balance_data['serial']}_{balance_data['obis']}_{balance_type}_balance",
            name = balance_data['locality_name'],
            model = f"modem ID: {balance_data['modem_id']}"
        )
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
        self._attr_device_class = sensor.SensorDeviceClass.ENERGY
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        match self._balance_type:
            case "daily":
                self._attr_name = f'Текущие сутки, "{self.balance['tariff']}"'
            case "weekly":
                self._attr_name = f'Текущая неделя, "{self.balance['tariff']}"'
            case "monthly":
                self._attr_name = f'Текущий месяц, "{self.balance['tariff']}"'
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