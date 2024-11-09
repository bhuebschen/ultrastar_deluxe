import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_IP, CONF_PORT


class UltraStarDeluxeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="UltraStar Deluxe", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_IP): str,
            vol.Required(CONF_PORT): int,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)