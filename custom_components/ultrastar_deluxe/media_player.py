import logging
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import (
    MediaPlayerEntityFeature,
)
from homeassistant.const import STATE_IDLE, STATE_PLAYING, STATE_PAUSED
from .const import DOMAIN, CONF_IP

_LOGGER = logging.getLogger(__name__)

SUPPORT_ULTRASTAR_DELUXE = (
    MediaPlayerEntityFeature.PLAY |
    MediaPlayerEntityFeature.STOP |
    MediaPlayerEntityFeature.PAUSE |
    MediaPlayerEntityFeature.VOLUME_SET |
    MediaPlayerEntityFeature.VOLUME_STEP |
    MediaPlayerEntityFeature.NEXT_TRACK |
    MediaPlayerEntityFeature.PREVIOUS_TRACK
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the UltraStar Deluxe media player platform."""
    connection = hass.data[DOMAIN][config_entry.entry_id]["connection"]
    entry_id = config_entry.entry_id
    name = f"UltraStar Deluxe [{config_entry.data[CONF_IP]}]"

    media_player = UltraStarDeluxeMediaPlayer(name, connection, entry_id)
    # Register listener for state updates
    connection.register_event_listener("get_state", media_player.update_state)
    async_add_entities([media_player])


class UltraStarDeluxeMediaPlayer(MediaPlayerEntity):
    def __init__(self, name, connection, entry_id):
        self._name = name
        self._connection = connection
        self._entry_id = entry_id
        self._state = STATE_IDLE
        self._volume = 0.5

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def supported_features(self):
        return SUPPORT_ULTRASTAR_DELUXE

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self._entry_id}_media_player"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "UltraStar Deluxe",
            "manufacturer": "UltraStar",
            "model": "Media Player",
            "sw_version": "1.0",
        }

    @property
    def volume_level(self):
        return self._volume

    async def async_update(self):
        """Fetch state from the device."""
        new_state = await self._connection.send_command("get_state")
        if new_state:
            self.update_state(new_state)

    async def update_state(self, state):
        """Callback to update the state of the media player based on event data."""
        if state == "playing":
            self._state = STATE_PLAYING
        elif state == "paused":
            self._state = STATE_PAUSED
        elif state == "stop":
            self._state = STATE_IDLE
        else:
            _LOGGER.warning(f"Unknown state received: {state}")
            self._state = STATE_IDLE
        self.async_write_ha_state()

    async def async_media_play(self):
        await self._connection.send_command("play")
        self._state = STATE_PLAYING
        self.async_write_ha_state()

    async def async_media_pause(self):
        await self._connection.send_command("pause")
        self._state = STATE_PAUSED
        self.async_write_ha_state()

    async def async_media_stop(self):
        await self._connection.send_command("stop")
        self._state = STATE_IDLE
        self.async_write_ha_state()

    async def async_set_volume_level(self, volume):
        self._volume = volume
        await self._connection.send_command(f"set_volume {int(volume * 100)}")
        self.async_write_ha_state()

    async def async_volume_up(self):
        await self._connection.send_command("volume_up")
        self._volume = min(1.0, self._volume + 0.1)
        self.async_write_ha_state()

    async def async_volume_down(self):
        await self._connection.send_command("volume_down")
        self._volume = max(0.0, self._volume - 0.1)
        self.async_write_ha_state()

    async def async_media_next_track(self):
        await self._connection.send_command("next")

    async def async_media_previous_track(self):
        await self._connection.send_command("previous")
