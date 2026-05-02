"""Fan platform for ChromaComfort."""

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    data = hass.data[DOMAIN][entry.entry_id]
    ble_client = data["ble_client"]
    coordinator = data["coordinator"]

    async_add_entities([ChromaComfortFan(coordinator, ble_client, entry)])


class ChromaComfortFan(CoordinatorEntity, FanEntity):
    """Representation of a ChromaComfort Fan."""

    _attr_supported_features = FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
    _attr_has_entity_name = True
    _attr_name = "Fan"

    def __init__(self, coordinator, ble_client, entry):
        super().__init__(coordinator)
        self._ble = ble_client
        self._attr_unique_id = f"{entry.entry_id}_fan"
        self._is_on = False

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Broan",
            "model": "ChromaComfort",
        }

    @property
    def is_on(self) -> bool | None:
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the fan on."""
        self._is_on = True
        cmd = bytes([0x3A, 0x00, 0x00, 0x00, 0x01] + [0x00] * 12)
        if await self._ble.send_command(cmd):
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the fan off."""
        self._is_on = False
        cmd = bytes([0x3A, 0x00, 0x00, 0x00, 0x02] + [0x00] * 12)
        if await self._ble.send_command(cmd):
            self.async_write_ha_state()