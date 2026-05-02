"""Config flow for ChromaComfort."""

import voluptuous as vol
import re

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, DEFAULT_POLL_INTERVAL


class ChromaComfortConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            device_mac = user_input["device_mac"].upper().replace(":", "")
            poll_interval = user_input.get("poll_interval", DEFAULT_POLL_INTERVAL)

            if not re.fullmatch(r"([0-9A-Fa-f]{12})", device_mac):
                errors["device_mac"] = "invalid_mac"
            elif poll_interval < 1 or poll_interval > 300:
                errors["poll_interval"] = "invalid_poll_interval"
            else:
                # Format MAC nicely
                formatted_mac = ":".join(device_mac[i:i+2] for i in range(0, 12, 2))
                return self.async_create_entry(
                    title=f"ChromaComfort {formatted_mac[-8:]}",
                    data={"device_mac": formatted_mac, "poll_interval": poll_interval},
                )

        data_schema = vol.Schema({
            vol.Required("device_mac"): str,
            vol.Optional("poll_interval", default=DEFAULT_POLL_INTERVAL): vol.All(int, vol.Range(min=1, max=300)),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )