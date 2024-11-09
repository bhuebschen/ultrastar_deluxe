import logging
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the UltraStar Deluxe sensors for the specific instance."""
    connection = hass.data[DOMAIN][config_entry.entry_id]["connection"]
    entry_id = config_entry.entry_id

    sensors = [
        UltraStarDeluxeSensor("get_version", connection,
                              entry_id, "UltraStar Deluxe Version"),
        UltraStarDeluxeSensor("current_song", connection,
                              entry_id, "Current Song"),
        UltraStarDeluxeSensor("lyric_line", connection,
                              entry_id, "Lyric Line"),
        UltraStarDeluxeSensor("points", connection, entry_id, "Points"),
        UltraStarDeluxeSensor("rating", connection, entry_id, "Rating"),
    ]

    # Register listeners for each sensor type
    for sensor in sensors:
        connection.register_event_listener(
            sensor._sensor_type, sensor.update_state)

    async_add_entities(sensors)


class UltraStarDeluxeSensor(SensorEntity):
    """Representation of a sensor to retrieve data from UltraStar Deluxe."""

    def __init__(self, sensor_type, connection, entry_id, name):
        """Initialize the sensor with a unique ID per instance."""
        self._connection = connection
        self._sensor_type = sensor_type
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{sensor_type}"
        self._entry_id = entry_id
        self._attr_state = None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "UltraStar Deluxe",
            "manufacturer": "UltraStar",
            "model": "Data Sensor",
            "sw_version": "1.0",
        }

    @property
    def state(self):
        """Return the current state of the sensor."""
        return self._attr_state

    async def async_update(self):
        """Fetch new state data for the sensor."""
        response = await self._connection.send_command(self._sensor_type)
        if response:
            self.update_state(response)

    async def update_state(self, data):
        """Callback to update the state of the sensor based on event data."""
        self._attr_state = data
        self.async_write_ha_state()
