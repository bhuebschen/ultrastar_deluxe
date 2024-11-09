import asyncio
import logging

_LOGGER = logging.getLogger(__name__)


class UltraStarDeluxeConnection:
    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._reader = None
        self._writer = None
        self._event_listeners = {}
        self._lock = asyncio.Lock()
        self._reconnect_task = None

    async def connect(self):
        """Establish a persistent connection and start listening for events if not already connected."""
        if self._writer is None or self._writer.is_closing():
            try:
                await self._cleanup_connection()  # Ensure no old connection exists
                self._reader, self._writer = await asyncio.open_connection(self._ip, self._port)
                _LOGGER.info("Connected to UltraStar Deluxe")
                if self._reconnect_task is None or self._reconnect_task.done():
                    self._reconnect_task = asyncio.create_task(
                        self._listen_for_events())
            except Exception as e:
                _LOGGER.error(f"Failed to connect to UltraStar Deluxe: {e}")
                # Set reader and writer to None in case of failure
                self._reader, self._writer = None, None
                await self._schedule_reconnect()

    async def send_command(self, command):
        """Send a command without expecting a direct response."""
        async with self._lock:
            await self.connect()  # Ensure the connection is established
            if self._writer:
                try:
                    self._writer.write(f"{command}\n".encode())
                    await self._writer.drain()
                    _LOGGER.info(f"Command '{command}' sent successfully")
                    # Small delay to allow server to process
                    await asyncio.sleep(0.1)
                except Exception as e:
                    _LOGGER.error(f"Error sending command '{command}': {e}")
                    await self._schedule_reconnect()

    async def _listen_for_events(self):
        """Continuously listen for incoming messages and process them as events."""
        while self._reader and not self._writer.is_closing():
            try:
                async with self._lock:
                    if not self._reader:
                        _LOGGER.warning("No valid reader found")
                        break

                    response = await self._reader.readline()
                    if not response:
                        await self._schedule_reconnect()
                        break

                response_text = response.decode().strip()
                _LOGGER.debug(f"Received message: {response_text}")

                if response_text:
                    await self._process_event(response_text)
                else:
                    _LOGGER.debug("Ignoring empty or invalid response.")
            except (asyncio.IncompleteReadError, ConnectionResetError, BrokenPipeError) as e:
                await self._schedule_reconnect()
                break  # Exit the loop after reconnect attempt
            except Exception as e:
                _LOGGER.error(
                    f"Unexpected error while listening for events: {e}")
                break  # Exit on unexpected errors

    async def _process_event(self, response_text):
        """Process incoming events and notify listeners."""
        if ':' in response_text:
            command, data = response_text.split(":", 1)
            data = data.strip()
            _LOGGER.debug(
                f"Processing: {command}, {data}")
            if command in self._event_listeners:
                for callback in self._event_listeners[command]:
                    await callback(data)
            else:
                _LOGGER.warning(
                    f"No listener for event '{command}' with data '{data}'")
        else:
            _LOGGER.warning(
                f"Unexpected event format, ignoring: {response_text}")

    def register_event_listener(self, event, callback):
        """Register a listener for a specific event type."""
        if event not in self._event_listeners:
            self._event_listeners[event] = []
        self._event_listeners[event].append(callback)
        _LOGGER.info(f"Registered listener for event '{event}'")

    async def _schedule_reconnect(self):
        """Schedule a non-blocking reconnect task if not already scheduled."""
        if self._reconnect_task is None or self._reconnect_task.done():
            self._reconnect_task = asyncio.create_task(self._reconnect())

    async def _reconnect(self):
        """Attempt to reconnect with a delay."""
        await self._cleanup_connection()
        await asyncio.sleep(2)  # Wait a moment before reconnecting
        await self.connect()

    async def _cleanup_connection(self):
        """Clean up the existing connection before reconnecting."""
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
        self._reader, self._writer = None, None

    async def close(self):
        """Close the connection."""
        await self._cleanup_connection()
