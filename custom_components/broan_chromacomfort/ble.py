"""BLE client for ChromaComfort - Improved debugging."""

import logging
from bleak import BleakClient

_LOGGER = logging.getLogger(__name__)

class ChromaComfortBLE:
    """BLE wrapper."""

    def __init__(self, mac: str):
        self.mac = mac
        self.client = BleakClient(mac)

    async def connect(self) -> bool:
        if self.client.is_connected:
            return True
        try:
            _LOGGER.info("Connecting to %s...", self.mac)
            await self.client.connect()
            _LOGGER.info("✅ Successfully connected to %s", self.mac)
            return True
        except Exception as err:
            _LOGGER.error("❌ Connection failed to %s: %s", self.mac, err)
            return False

    async def disconnect(self):
        if self.client.is_connected:
            try:
                await self.client.disconnect()
                _LOGGER.info("Disconnected from %s", self.mac)
            except Exception as err:
                _LOGGER.warning("Disconnect error: %s", err)

    async def send_command(self, cmd: bytes) -> bool:
        """Send command with service/characteristic discovery."""
        if not self.client.is_connected:
            if not await self.connect():
                return False

        try:
            # Log all services for debugging
            _LOGGER.debug("Services found: %s", [s.uuid for s in self.client.services])

            # Try to find the characteristic
            char_uuid = None
            for service in self.client.services:
                for char in service.characteristics:
                    if "fff3" in char.uuid.lower():
                        char_uuid = char.uuid
                        _LOGGER.info("Found target characteristic: %s", char_uuid)
                        break
                if char_uuid:
                    break

            if not char_uuid:
                _LOGGER.error("❌ Target characteristic (fff3) not found on this device!")
                return False

            await self.client.write_gatt_char(char_uuid, cmd, response=False)
            _LOGGER.info("✅ Command sent successfully")
            return True

        except Exception as err:
            _LOGGER.error("❌ Failed to send command: %s", err)
            return False