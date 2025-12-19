# sensor.py - Fixed subscriptable error, modernized to use SensorEntity and CoordinatorEntity, added device_info

import logging
from datetime import datetime
from typing import Callable, List, Any, Dict
from homeassistant.components import sensor
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import (
    HomeAssistant,
    callback
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from . import WaviotDataUpdateCoordinator, const, waviot_api, waviot_client

_LOGGER = logging.getLogger(__name__)

################################
async def async_setup_entry(
            hass: HomeAssistant, entry: ConfigEntry,
            async_add_entities: Callable
):
    _LOGGER.debug("Setup %s ", entry.title)
    coordinator: WaviotDataUpdateCoordinator = hass.data[const.DOMAIN][entry.entry_id]
    sensors: List[WaviotRegistratorSensor] = []
    for key, registrator_raw in coordinator.api.registrators_raw.items():
        _LOGGER.debug('registrator_raw: %s', registrator_raw)
        sensors.append( WaviotRegistratorSensor( coordinator, registrator_raw))
    async_add_entities(sensors)
    sensors_daily_balances: List[WaviotBalanceSensor] = []
    for key, daily_balances_raw in coordinator.api.balances_daily_raw.items():
        _LOGGER.debug('daily_balances_raw: %s', daily_balances_raw)
        sensors_daily_balances.append( WaviotBalanceSensor( coordinator, daily_balances_raw,'daily'))
    async_add_entities( sensors_daily_balances)


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
class _WaviotRegistratorSensor(_WaviotBaseSensor):
    def __init__(
        self,
        coordinator: WaviotDataUpdateCoordinator,
       # registrator: waviot_api.Registrator,
        registrator_raw: Dict[str,Any],
        id_suffix: str = "",
    ):
        super().__init__(
            coordinator = coordinator,
            unique_id = f"{const.DOMAIN}_{registrator_raw['serial']}_{registrator_raw['id']}-{id_suffix}",
            name = registrator_raw['locality_name'],
            model = f"modem ID: {registrator_raw['modem_id']}"
        )
        #self.registrator: waviot_api.Registrator = registrator
        self._registrator_raw = registrator_raw
        self._registrator_key: waviot_api.Registrator_key = waviot_api.Registrator_key(modem_id=registrator_raw['modem_id'],
                                                                                       channel_id=registrator_raw['channel_id'])
        self._update_state_attributes()

    #async def async_update_value(
    #    self, values: list[waviot_client.UpdateValuePayload], return_response: bool = True
   # ) -> ServiceResponse:
    #    """nothing to do with RO value"""

    def _update_state_attributes(self):
        pass

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        _LOGGER.debug("Update WaviotRegistratorSensor")
        self.registrator = self.coordinator.api.get_registrator( self._registrator_key)
        self.coordinator.last_update_success = True
        super()._handle_coordinator_update()

    @property
    def assumed_state(self) -> bool:
        return not self.coordinator.last_update_success

    @property
    def available(self) -> bool:
        return True

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
            #unique_id = f"{const.DOMAIN}_{registrator_raw['serial']}_{registrator_raw['id']}-{id_suffix}",
            unique_id=f"waviot_{registrator_raw['modem_id']}_{registrator_raw['obis']}_{registrator_raw['tariff_descriptor']}-{id_suffix}",
            name = registrator_raw['locality_name'],
            model = f"modem ID: {registrator_raw['modem_id']}"
        )
        #self.registrator: waviot_api.Registrator = registrator
        self._registrator_raw = registrator_raw
        self._registrator_key: waviot_api.Registrator_key = waviot_api.Registrator_key(modem_id=registrator_raw['modem_id'],
                                                                                       channel_id=registrator_raw['channel_id'])
        self._update_state_attributes()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        _LOGGER.debug("Update WaviotRegistratorSensor")
        self._registrator_raw    = self.coordinator.api.get_registrator_raw( self._registrator_key)
        self.coordinator.last_update_success = True
        super()._handle_coordinator_update()

    def _update_state_attributes(self):
        _LOGGER.debug("Initialize WaviotRegistratorSensor")
        self._attr_device_class = sensor.SensorDeviceClass.ENERGY
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_name = self._registrator_raw['channel_id']
        self._attr_extra_state_attributes = self._registrator_raw

    @property
    def native_value(self) -> int:
        """Return the value of the sensor."""
       # return self.meter.value
        return self._registrator_raw['last_value']

    @property
    def assumed_state(self) -> bool:
        return not self.coordinator.last_update_success

    @property
    def available(self) -> bool:
        return True

    def __str__(self):
        return f"{self._registrator_raw.last_value}"

################################
class WaviotBalanceSensor(_WaviotBaseSensor):
    _attr_state_class = sensor.SensorStateClass.TOTAL_INCREASING
    _attr_has_entity_name = True
    #_attr_supported_features = 0
    _attr_translation_key = "meter"

    def __init__(
        self,
        coordinator: WaviotDataUpdateCoordinator,
        balance: Dict[str, Any],
        balance_type: const.BALANCE_TYPES,
        id_suffix: str = ''
    ):
        super().__init__(
            coordinator = coordinator,
            unique_id = f"{const.DOMAIN}_{balance['serial']}_{balance['obis']}_{balance_type}_balance",
            name = balance['locality_name'],
            model = f"modem ID: {balance['modem_id']}"
        )
        self.balance = balance
        self._balance_type: const.BALANCE_TYPES  = balance_type
        self._registrator_key: waviot_api.Registrator_key = waviot_api.Registrator_key(modem_id=balance['modem_id'],
                                                                                       channel_id=balance['channel_id'])
        self._update_state_attributes()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        _LOGGER.debug("Update WaviotRegistratorSensor")
        self.registrator = self.coordinator.api.get_balances(self._registrator_key,self._balance_type)
        self.coordinator.last_update_success = True
        super()._handle_coordinator_update()

    def _update_state_attributes(self):
        _LOGGER.debug("Initialize WaviotRegistratorSensor")
        self._attr_device_class = sensor.SensorDeviceClass.ENERGY
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_name = self.balance['channel_id']
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

    def __str__(self):
        return f"{self.balance.last_value}"