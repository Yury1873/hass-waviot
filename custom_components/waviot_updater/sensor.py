# sensor.py - Fixed subscriptable error, modernized to use SensorEntity and CoordinatorEntity, added device_info

import logging
from typing import Callable, List
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

SENSOR_TYPES = {
    "battery": {
        "name": "Battery Voltage",
        "unit": "V",
        "device_class": "voltage",
    },
    "temperature": {
        "name": "Temperature",
        "unit": "°C",
        "device_class": "temperature",
    },
    "latest": {
        "name": "Total Energy",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "last_update": {
        "name": "Last Reading",
        "unit": None,
        "device_class": "timestamp",
    },
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable
):
    _LOGGER.debug("Setup %s ", entry.title)
    coordinator: WaviotDataUpdateCoordinator = hass.data[const.DOMAIN][entry.entry_id]
    sensors: List[WaviotMeterSensor] = []
    for modem in coordinator.api.modems:
        for registrator_id, registrator_meta in modem.registrators.items():
            _LOGGER.debug('registrator_meta:')
            _LOGGER.debug(registrator_meta)
            sensors.append(
                WaviotMeterSensor(
                            coordinator,
                            modem,
                            waviot_api.Registrator(modem.modem_id, registrator_meta)
                )
            )
    #async_add_entities(
     #   WaviotMeterSensor(coordinator, m) for m in coordinator.api.modems
    #)
    async_add_entities(sensors)

class _WaviotBaseSensor(
    CoordinatorEntity[WaviotDataUpdateCoordinator], sensor.SensorEntity
):
    def __init__(
        self,
        coordinator: WaviotDataUpdateCoordinator,
        modem_id: str,
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

class _WaviotMeterSensor(_WaviotBaseSensor):
    def __init__(
        self,
        coordinator: WaviotDataUpdateCoordinator,
        modem: waviot_api.Modem,
        registrator: waviot_api.Registrator,
        id_suffix: str = "",
    ):
        super().__init__(
            coordinator,
            registrator.modem_id,
            f"{const.DOMAIN}_{registrator.modem_id}_{registrator.registrator_id}",
            modem.locality,
            f"modem ID: {modem.modem_id}"
        )
        self.registrator = registrator
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
      #?  ind = self.api.find_ind(self.meter.id)
     #?  if ind is not None:
        #?        self.meter = ind
        #?   _LOGGER.debug("[%s] New indication %s", self.entity_id, self.meter)
        #? self._update_state_attributes()
        #?else:
            #?_LOGGER.warning(
            #?"[%s] Indication %s not found", self.entity_id, self.meter.id
            #?)
        super()._handle_coordinator_update()

    @property
    def assumed_state(self) -> bool:
        return not self.coordinator.last_update_success

    @property
    def available(self) -> bool:
        return True


class WaviotMeterSensor(_WaviotMeterSensor):
    _attr_state_class = sensor.SensorStateClass.TOTAL_INCREASING
    _attr_has_entity_name = True
    #_attr_supported_features = 0
    _attr_translation_key = "meter"

    def __init__(
        self,
        coordinator: WaviotDataUpdateCoordinator,
        modem: waviot_api.Modem,
        registrator: waviot_api.Registrator,
        diag: bool = False
    ):
        super().__init__(coordinator,modem, registrator,registrator.registrator_id)
        if diag:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    def _update_state_attributes(self):
        #if not self.meter.auto:
            #self._attr_supported_features = const.PescEntityFeature.MANUAL
        _LOGGER.debug("Initialize WaviotMeterSensor")
        #subservice = self.api.subservice(self.meter.meter.subservice_id)
        #utility = "" if subservice is None else subservice["utility"]
        #if utility == pesc_client.SubserviceUtility.ELECTRICITY:
        self._attr_device_class = sensor.SensorDeviceClass.ENERGY
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
#        self._attr_name = self.registrator['channel_id']
        self._attr_name = self.registrator.channel_id

        self._attr_extra_state_attributes = {
            "type": "self.meter.account.type",
            "date": "self.meter.date.isoformat()",
            "name": "self.meter.name",
            #"scale_id": self.meter.scale_id,
            #"meter_id": self.meter.meter.id,
            #"serial": self.meter.meter.serial,
            #"account_id": str(self.meter.account.id),
            #"tenancy": self.meter.account.tenancy,
            #"address": self.meter.account.address,
        }

    @property
    def native_value(self) -> int:
        """Return the value of the sensor."""
       # return self.meter.value
        return self.registrator.last_value

    #def __str__(self):
    #    return f"{self.meter.value}"

    #async def async_update_value(
    #    self, values: list[pesc_client.UpdateValuePayload], return_response: bool = True
   # ) -> ServiceResponse:
   #     _LOGGER.debug("[%s]: Updating "%s" to %s", self.entity_id, self.name, values)

#        if self.meter.auto:
 #           msg = "Показания передаются в автоматическом режиме"
  #          if not return_response:
 #               raise HomeAssistantError(msg)
 #           return {"code": -2, "message": msg}
#
#        for value in values:
#            if value["scaleId"] == self.meter.scale_id and value["value"] < self.state:
#                msg = f"Новое значение {value['value']} меньше предыдущего {self.meter.value}"
#                if not return_response:
#                    raise HomeAssistantError(msg)
#                return {"code": -3, "message": msg, "values": values}

#        res = await self.relogin_and_update_(values, return_response, False)
 #       await self.async_update()
  #      return res

   # async def relogin_and_update_(
   #     self,
   #     values: list[pesc_client.UpdateValuePayload],
   #     return_response: bool,
   #     do_relogin: bool,
   # ) -> ServiceResponse:
   #     try:
   #         await self.coordinator._relogin(do_relogin)
   #         payload = await self.api.async_update_value(self.meter, values)
   #         _LOGGER.debug('[%s] Update "%s" success', self.entity_id, self.name)
   #         return {
   #             "code": 0,
   #             "message": "Операция выполнена успешно",
   #             "payload": payload,
   #         }
   #     except pesc_client.ClientAuthError as err:
   #         if not do_relogin:
   #             return await self.relogin_and_update_(values, return_response, True)
   #         if not return_response:
   #             raise ConfigEntryAuthFailed from err
   #         return {"code": err.code, "message": err.message}
   #     except pesc_client.ClientError as err:
   #         if not return_response:
   #             raise HomeAssistantError(f"Ошибка вызова API: {err}") from err
   #         return {"code": err.code, "message": err.message}





#class WaviotSensor_old(CoordinatorEntity, sensor.SensorEntity):
#    """Representation of a WAVIoT sensor."""
#    _attr_has_entity_name = True
#
#    def __init__(self, coordinator, sensor_type, meta):
#        """Initialize the sensor."""
#        super().__init__(coordinator)
#        self.sensor_type = sensor_type
#        self.meta = meta
#        self._attr_name = meta["name"]
#        self._attr_unique_id = f"{coordinator.modem_id}_{sensor_type}"
#        self._attr_device_class = meta.get("device_class")
#        self._attr_native_unit_of_measurement = meta.get("unit")
#        self._attr_state_class = meta.get("state_class")
#        self._attr_device_info = {
 #           "identifiers": {(const.DOMAIN, coordinator.modem_id)},
 #           "name": f"WAVIoT Modem {coordinator.modem_id}",
 #           "model": "Modem",
 #           "manufacturer": "WAVIoT",
 #       }

 #   @property
 #   def native_value(self):
 #       """Return the state of the sensor."""
 #       return self.coordinator.data.get(self.sensor_type)
