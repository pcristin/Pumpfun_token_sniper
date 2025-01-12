import aiohttp
import asyncio

from utils.logger_config import logger  # Centralized logger

class RugCheck:
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()
    
    async def __make_request(self, base_url: str, token_address: str):
        while True:
            async with self.session.get(f'{base_url}/{token_address}/report') as response:
                if response.status == 429:
                    logger.warning("Rate limit exceeded", extra={'token_name': token_address})
                    await asyncio.sleep(10)
                    continue
                elif response.status in (200, 400):
                    return await response.json()
                else:
                    logger.error(f"Unexpected status code: {response.status}", extra={'token_name': token_address})
                    raise Exception(f"Unexpected status code: {response.status}")

    async def analyze_token(self, token_address: str):
        logger.debug(f"Analyzing token: {token_address}", extra={'token_name': token_address})
        token_data = await self.__make_request('https://api.rugcheck.xyz/v1/tokens', token_address)
        if "error" in token_data:
            logger.error(f"Token {token_address} not found", extra={'token_name': token_address})
            return None
        if "risks" not in token_data:
            symbol = token_data.get('tokenMeta', {}).get('symbol', 'Unknown')
            logger.info(f"Token {symbol} has no risks", extra={'token_name': symbol})
        else:
            symbol = token_data.get('tokenMeta', {}).get('symbol', 'Unknown')
            risk_count = len(token_data.get('risks'))
            if risk_count > 3:
                logger.error(f"Token {symbol} has {risk_count} risks", extra={'token_name': symbol})
            elif risk_count > 1 and risk_count <= 3:
                logger.warning(f"Token {symbol} has {risk_count} risks", extra={'token_name': symbol})
            for risk in token_data.get('risks'):
                logger.debug(f"Risk: {risk.get('name', 'N/A')}", extra={'token_name': symbol})
                logger.debug(f"Description: {risk.get('description', 'N/A')}", extra={'token_name': symbol})
                logger.debug(f"Level: {risk.get('level', 'N/A')}", extra={'token_name': symbol})
        return token_data