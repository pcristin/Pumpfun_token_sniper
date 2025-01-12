import asyncio
import aiohttp
import questionary
from typing import Union

from utils.logger_config import logger

class SolSniffer:
    module_name = "SolSniffer"
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()

    async def __make_request(self, base_url: str, params: Union[dict, None] = None):
        self.session.headers.update({
            "accept": "*/*",
            "Content-Type": "application/json",
            "Host": "solsniffer.com"
        })
        while True:
            async with self.session.get(f'{base_url}', params=params) as response:
                if response.status == 429:
                    logger.warning("Rate limit exceeded", extra={'module_name': self.module_name})
                    await asyncio.sleep(10)
                    continue
                elif response.status in (200, 400, 404):
                    return await response.json()
                else:
                    logger.error(f"Unexpected status code: {response.status}", extra={'module_name': self.module_name})
                    raise Exception(f"Unexpected status code: {response.status}")

    async def analyze_wallets(self):
        # Get number of wallets to analyze
        while True:
            try:
                number_of_wallets = int(questionary.text(
                    "Enter the number of wallets to analyze (max 100)",
                ).ask())
                if number_of_wallets > 100:
                    logger.error("Number of wallets is too high, please enter a number less than or equal to 100", extra={'module_name': self.module_name})
                    continue
                else:
                    break
            except ValueError:
                logger.error("Invalid number of wallets. Please enter a number.", extra={'module_name': self.module_name})
                continue
        
        # Get interval
        interval_asked = questionary.select(
            "Select interval",
            choices=["Day", "7 Days", "30 Days"]
        ).ask()
        interval_mapping = {
            "Day": "day",
            "7 Days": "week",
            "30 Days": "month"
        }
        interval = interval_mapping.get(interval_asked)

        # Get wallets
        wallets = await self.__make_request(base_url=f"https://solsniffer.com/api/v1/sniffWallet/wallets", 
                                            params={"limit": number_of_wallets, "interval": interval})
        for wallet in wallets.get('wallets'):
            logger.info(f"Analyzing wallet: {wallet['address']}", extra={'module_name': self.module_name, 'address': wallet['address']})
            # TODO: Add analysis logic here