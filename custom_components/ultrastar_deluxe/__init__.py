import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_IP, CONF_PORT
from .connection import UltraStarDeluxeConnection

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ip = entry.data[CONF_IP]
    port = entry.data[CONF_PORT]

    # Initialisiere das DOMAIN-Dictionary, falls es noch nicht existiert
    hass.data.setdefault(DOMAIN, {})

    # Initialisiere die persistente Verbindung und speichere sie unter entry_id
    connection = UltraStarDeluxeConnection(ip, port)
    await connection.connect()
    hass.data[DOMAIN][entry.entry_id] = {"connection": connection}

    # Weiterleiten an die media_player-, button- und sensor-Plattformen
    await hass.config_entries.async_forward_entry_setups(entry, ["media_player", "button", "sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Schließe die Verbindung beim Entladen
    await hass.data[DOMAIN][entry.entry_id]["connection"].close()
    hass.data[DOMAIN].pop(entry.entry_id)

    # Entlade Plattformen
    await hass.config_entries.async_unload_platforms(entry, ["media_player", "button", "sensor"])

    # Entferne `DOMAIN`-Eintrag, falls keine Instanzen mehr vorhanden sind
    if not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)

    return True
