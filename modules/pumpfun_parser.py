import asyncio
import json
import signal

from modules.rug_check import RugCheck
from database.database import DatabaseManager
from websockets.exceptions import ConnectionClosedError
from websockets.asyncio.client import connect

from utils.logger_config import logger

class PumpFunParser:
    def __init__(self, ws_uri: str, reconnect_delay: int = 30, ping_interval: int = 45):
        self.ws_uri = ws_uri
        self.reconnect_delay = reconnect_delay
        self.ping_interval = ping_interval
        self.rug_check = RugCheck()
        self.db_manager = DatabaseManager()
        self.ws = None
        self.shutdown_event = asyncio.Event()
        self.token_list = []
    
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.ws and not self.ws.close_code:
            await self.ws.close()
        self.db_manager.close()

    async def handle_message(self, message: str):
        data = json.loads(message)
        logger.debug(f"Received data: {data}", extra={'module_name': 'PumpFun', 'token_name': data.get('name', 'N/A')})
        
        mint = data.get('mint')
        if mint:
            token_data = await self.rug_check.analyze_token(mint)
            if not token_data or not await self.passes_security_filters(token_data):
                logger.error(f"Token {mint} failed security filters.", extra={'module_name': 'PumpFun','token_name': data.get('name', 'N/A')})
                return
            self.db_manager.store_token(token_data)

    async def subscribe(self, ws):
        payload = {"method": "subscribeNewToken"}
        await ws.send(json.dumps(payload))
        logger.info("Subscribed to new token events.")

    async def listen(self):
        while not self.shutdown_event.is_set():
            try:
                logger.debug("Attempting to connect to WebSocket...")
                async with connect(
                    self.ws_uri, ping_interval=self.ping_interval
                ) as ws:
                    self.ws = ws
                    logger.info("WebSocket connection established.")
                    await self.subscribe(ws)
                    async for message in ws:
                        await self.handle_message(message)  # type: ignore
                        if self.shutdown_event.is_set():
                            logger.warning("Shutdown event detected. Breaking out of message loop.")
                            break
            except (ConnectionClosedError, ConnectionRefusedError) as e:
                logger.error(f"WebSocket error: {e}")
                if not self.shutdown_event.is_set():
                    logger.warning(f"Reconnecting in {self.reconnect_delay} seconds...")
                    await asyncio.sleep(self.reconnect_delay)
            except Exception as e:
                logger.exception(f"An unexpected error occurred: {e}")
                if not self.shutdown_event.is_set():
                    logger.warning(f"Reconnecting in {self.reconnect_delay} seconds...")
                    await asyncio.sleep(self.reconnect_delay)
            finally:
                self.ws = None
                logger.info("WebSocket connection closed.")

    def handle_signal(self, signum, frame):
        logger.warning(f"Received shutdown signal: {signum}")
        self.shutdown_event.set()
        if self.ws:
            asyncio.create_task(self.ws.close())

    async def run(self):
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self.handle_signal, sig, None)
        
        async with self.rug_check:
            await self.listen()

    async def passes_security_filters(self, token_data):
        if token_data.get('score', None) <= 5000:
            return True
        return False

