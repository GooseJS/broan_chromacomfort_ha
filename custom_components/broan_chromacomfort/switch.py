"""Switch platform for ChromaComfort (e.g. speaker / nightlight / etc.)."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up the switch platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    ble_client = data["ble_client"]
    coordinator = data["coordinator"]

    async_add_entities([ChromaComfortSwitch(coordinator, ble_client, entry)])


class ChromaComfortSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a ChromaComfort Switch."""

    _attr_has_entity_name = True
    _attr_name = "Aux Switch"   # Rename as needed (e.g. Speaker, Night Light)

    def __init__(self, coordinator, ble_client, entry):
        super().__init__(coordinator)
        self._ble = ble_client
        self._attr_unique_id = f"{entry.entry_id}_switch"
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
        """Turn the switch on."""
        self._is_on = True
        cmd = bytes([0x3A, 0x00, 0x00, 0x00, 0x05] + [0x00] * 12)
        if await self._ble.send_command(cmd):
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        self._is_on = False
        cmd = bytes([0x3A, 0x00, 0x00, 0x00, 0x06] + [0x00] * 12)
        if await self._ble.send_command(cmd):
            self.async_write_ha_state()