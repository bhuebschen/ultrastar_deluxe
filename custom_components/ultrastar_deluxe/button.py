import logging
from homeassistant.components.button import ButtonEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the UltraStar Deluxe buttons for the specific instance."""
    connection = hass.data[DOMAIN][config_entry.entry_id]["connection"]
    entry_id = config_entry.entry_id

    async_add_entities([
        UltraStarDeluxeButton("restart", connection, entry_id),
        UltraStarDeluxeButton("shutdown", connection, entry_id),
        UltraStarDeluxeButton("home", connection, entry_id),
    ])


class UltraStarDeluxeButton(ButtonEntity):
    """Representation of a button to send commands to UltraStar Deluxe."""

    def __init__(self, command, connection, entry_id):
        """Initialize the button with a unique ID per instance."""
        self._entry_id = entry_id
        self._connection = connection
        self._command = command
        self._attr_name = f"UltraStar Deluxe {command.capitalize()}"
        # Eindeutige ID pro Button
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{command}"

    @property
    def unique_id(self):
        """Return a unique ID for each button."""
        return self._attr_unique_id

    @property
    def device_info(self):
        """Return device information to associate the button with the UltraStar Deluxe device."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "UltraStar Deluxe",
            "manufacturer": "UltraStar",
            "model": "Control Button",  # Allgemeinere Bezeichnung für die Buttons
            "sw_version": "1.0",  # Falls eine Version verfügbar ist, hier dynamisch setzen
        }

    async def async_press(self):
        """Handle the button press, sending the command to the instance."""
        _LOGGER.debug(f"Sending {self._command} command to UltraStar Deluxe")
        await self._connection.send_command(self._command)
