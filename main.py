import asyncio
from modules.pumpfun_parser import PumpFunParser
import sys

from utils.logger_config import logger  # Centralized logger

async def main():
    ws_uri = "wss://pumpportal.fun/api/data"
    parser = PumpFunParser(ws_uri)
    await parser.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        logger.info("Shutting down.")
        sys.exit()