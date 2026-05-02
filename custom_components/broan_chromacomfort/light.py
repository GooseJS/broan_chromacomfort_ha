"""Light platform for ChromaComfort."""

from homeassistant.components.light import LightEntity, ColorMode, LightEntityFeature
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

    async_add_entities([ChromaComfortLight(coordinator, ble_client, entry)])


class ChromaComfortLight(CoordinatorEntity, LightEntity):
    """Representation of a ChromaComfort Light."""

    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature(0)   # No extra features for now
    _attr_has_entity_name = True
    _attr_name = "Light"

    def __init__(self, coordinator, ble_client, entry):
        super().__init__(coordinator)
        self._ble = ble_client
        self._attr_unique_id = f"{entry.entry_id}_light"
        self._is_on = False
        self._brightness = 255

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Broan",
            "model": "ChromaComfort",
        }

    @property
    def is_on(self) -> bool | None:
        return self._is_on

    @property
    def brightness(self) -> int | None:
        return self._brightness if self._is_on else None

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        self._brightness = kwargs.get("brightness", self._brightness)
        self._is_on = True

        cmd = bytes([0x3A, 0x00, 0x00, 0x00, 0x03] + [0x00] * 12)
        if await self._ble.send_command(cmd):
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        self._is_on = False
        cmd = bytes([0x3A, 0x00, 0x00, 0x00, 0x04] + [0x00] * 12)
        if await self._ble.send_command(cmd):
            self.async_write_ha_state()