"""ChromaComfort integration."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_POLL_INTERVAL
from .ble import ChromaComfortBLE

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["fan", "light", "switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up ChromaComfort from a config entry."""
    mac = entry.data["device_mac"]
    poll_interval = entry.data.get("poll_interval", DEFAULT_POLL_INTERVAL)

    ble_client = ChromaComfortBLE(mac)

    if not await ble_client.connect():
        _LOGGER.error("Failed to connect to device during setup")
        return False

    async def async_update_data():
        """Fetch latest state (placeholder - improve with real status read if device supports)."""
        try:
            # Device may not support status read easily. For now return basic state.
            # You can extend this with notify or read_gatt_char if available.
            return {"available": True}
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="ChromaComfort",
        update_method=async_update_data,
        update_interval=timedelta(seconds=poll_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "ble_client": ble_client,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    data = hass.data[DOMAIN].get(entry.entry_id)
    if data:
        await data["ble_client"].disconnect()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok