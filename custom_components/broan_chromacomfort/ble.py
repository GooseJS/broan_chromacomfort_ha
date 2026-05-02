"""BLE client for ChromaComfort."""

import asyncio
import logging
from bleak import BleakClient, BleakError

from .const import CHAR_UUID

_LOGGER = logging.getLogger(__name__)

class ChromaComfortBLE:
    """BLE wrapper with reconnection logic."""

    def __init__(self, mac: str):
        self.mac = mac
        self.client = BleakClient(mac)
        self._lock = asyncio.Lock()

    async def connect(self) -> bool:
        """Connect with retry."""
        async with self._lock:
            if self.client.is_connected:
                return True
            try:
                await self.client.connect()
                _LOGGER.info("Connected to %s", self.mac)
                return True
            except BleakError as err:
                _LOGGER.error("Failed to connect to %s: %s", self.mac, err)
                return False

    async def disconnect(self):
        """Disconnect cleanly."""
        async with self._lock:
            if self.client.is_connected:
                try:
                    await self.client.disconnect()
                except Exception as err:
                    _LOGGER.warning("Error disconnecting: %s", err)

    async def send_command(self, cmd: bytes) -> bool:
        """Send command with auto-reconnect."""
        if not self.client.is_connected:
            if not await self.connect():
                return False

        try:
            await self.client.write_gatt_char(CHAR_UUID, cmd, response=False)
            return True
        except Exception as err:
            _LOGGER.error("Failed to send command: %s", err)
            # Try reconnect once
            await self.disconnect()
            if await self.connect():
                try:
                    await self.client.write_gatt_char(CHAR_UUID, cmd, response=False)
                    return True
                except Exception as retry_err:
                    _LOGGER.error("Retry failed: %s", retry_err)
            return False