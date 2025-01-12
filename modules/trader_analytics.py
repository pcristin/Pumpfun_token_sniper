import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

from database.database import DatabaseManager
from utils.logger_config import logger
from config import (
    API_ENDPOINTS,
    DEFAULT_HEADERS,
    DEFAULT_MIN_TRANSACTIONS,
    TOP_HOLDERS_LIMIT,
    ANALYSIS_TIMEFRAME_DAYS,
    HELIUS_PAGE_SIZE
)

class TraderAnalytics:
    def __init__(self, api_key: Optional[str] = None):
        if not api_key:
            raise ValueError("Helius API key is required for trader analytics")
        self.api_key = api_key
        self.base_url = f"{API_ENDPOINTS['HELIUS']['BASE_URL']}{api_key}"
        self.db_manager = DatabaseManager()
        self.headers = DEFAULT_HEADERS.copy()
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=10)

    async def __aenter__(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        self.executor.shutdown(wait=False)
        self.db_manager.close()

    @lru_cache(maxsize=100)
    async def get_token_holders(self, token_address: str) -> List[Dict]:
        """Get token holders using Helius API with caching."""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

        holders = []
        token_metadata = {
            "decimals": 9,  # Default to 9 decimals for SPL tokens
            "symbol": "UNKNOWN"  # Default symbol
        }
        
        try:
            # First get token metadata
            metadata_payload = {
                "jsonrpc": "2.0",
                "id": "token-sniper",
                "method": "getTokenMetadata",
                "params": [token_address]
            }

            async with self.session.post(self.base_url, json=metadata_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "error" in data:
                        logger.error(f"API error getting token metadata: {data['error']}", 
                                   extra={'module_name': 'TraderAnalytics'})
                    else:
                        result = data.get("result", {})
                        token_metadata.update({
                            "decimals": result.get("decimals", 9),
                            "symbol": result.get("symbol", "UNKNOWN")
                        })

            # Now get token accounts
            accounts_payload = {
                "jsonrpc": "2.0",
                "id": "token-sniper",
                "method": "getProgramAccounts",
                "params": [
                    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                    {
                        "encoding": "jsonParsed",
                        "filters": [
                            {
                                "dataSize": 165
                            },
                            {
                                "memcmp": {
                                    "offset": 0,
                                    "bytes": token_address
                                }
                            }
                        ]
                    }
                ]
            }

            async with self.session.post(self.base_url, json=accounts_payload) as accounts_response:
                if accounts_response.status == 200:
                    accounts_data = await accounts_response.json()
                    if "error" in accounts_data:
                        logger.error(f"API error getting accounts: {accounts_data['error']}", 
                                   extra={'module_name': 'TraderAnalytics'})
                        return []
                    
                    accounts = accounts_data.get("result", [])
                    
                    # Process accounts in parallel using ThreadPoolExecutor
                    def process_account(account):
                        parsed_data = account.get("account", {}).get("data", {}).get("parsed", {})
                        info = parsed_data.get("info", {})
                        
                        if parsed_data.get("type") == "account":
                            owner = info.get("owner")
                            amount = info.get("tokenAmount", {})
                            
                            if owner and amount and amount.get("uiAmount", 0) > 0:
                                return {
                                    "owner": owner,
                                    "amount": amount.get("uiAmount", 0),
                                    "decimals": token_metadata["decimals"],
                                    "symbol": token_metadata["symbol"]
                                }
                        return None

                    # Process accounts in parallel
                    loop = asyncio.get_event_loop()
                    processed_accounts = await loop.run_in_executor(
                        self.executor,
                        lambda: list(filter(None, map(process_account, accounts)))
                    )
                    
                    holders.extend(processed_accounts)

        except Exception as e:
            logger.error(f"Error fetching token holders: {str(e)}", 
                       extra={'module_name': 'TraderAnalytics'})
            return []

        # Sort holders by amount and return top holders
        holders.sort(key=lambda x: x.get("amount", 0), reverse=True)
        return holders[:TOP_HOLDERS_LIMIT]

    async def get_token_price(self, token_address: str) -> float:
        """Get token price in USD."""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

        try:
            # Using Helius API for price info
            price_payload = {
                "jsonrpc": "2.0",
                "id": "token-sniper",
                "method": "getAssetPricing",
                "params": [token_address]
            }

            async with self.session.post(self.base_url, json=price_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "error" in data:
                        logger.error(f"API error getting token price: {data['error']}", 
                                   extra={'module_name': 'TraderAnalytics'})
                        return 0
                    
                    result = data.get("result", {})
                    return result.get("price", 0)
        except Exception as e:
            logger.error(f"Error fetching token price: {str(e)}", 
                       extra={'module_name': 'TraderAnalytics'})
        return 0

    async def analyze_wallet_transactions(self, wallet_address: str, 
                                        start_time: Optional[datetime] = None) -> Dict:
        """Analyze transactions for a specific wallet."""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

        if not start_time:
            start_time = datetime.now() - timedelta(days=ANALYSIS_TIMEFRAME_DAYS)

        try:
            # Get signatures for address
            signatures_payload = {
                "jsonrpc": "2.0",
                "id": "token-sniper",
                "method": API_ENDPOINTS["HELIUS"]["METHODS"]["GET_SIGNATURES"],
                "params": [
                    wallet_address,
                    {
                        "limit": 100
                    }
                ]
            }

            async with self.session.post(self.base_url, json=signatures_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "error" in data:
                        logger.error(f"API error: {data['error']}", 
                                   extra={'module_name': 'TraderAnalytics'})
                        return {}
                        
                    signatures = data.get("result", [])
                    
                    # Get transaction details concurrently
                    async def get_transaction(sig):
                        tx_payload = {
                            "jsonrpc": "2.0",
                            "id": "token-sniper",
                            "method": API_ENDPOINTS["HELIUS"]["METHODS"]["GET_TRANSACTION"],
                            "params": [
                                sig.get("signature"),
                                {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}
                            ]
                        }
                        
                        if not self.session:
                            self.session = aiohttp.ClientSession(headers=self.headers)

                        async with self.session.post(self.base_url, json=tx_payload) as tx_response:
                            if tx_response.status == 200:
                                tx_data = await tx_response.json()
                                if not "error" in tx_data:
                                    return tx_data.get("result", {})
                            return None

                    # Process transactions concurrently
                    tasks = [get_transaction(sig) for sig in signatures[:10]]
                    transactions = await asyncio.gather(*tasks)
                    transactions = [tx for tx in transactions if tx is not None]
                    
                    return self._process_wallet_transactions(transactions)
                else:
                    logger.error(f"Failed to get wallet transactions: {response.status}", 
                               extra={'module_name': 'TraderAnalytics'})
                    return {}
        except Exception as e:
            logger.error(f"Error analyzing wallet: {str(e)}", 
                       extra={'module_name': 'TraderAnalytics'})
            return {}

    def _process_wallet_transactions(self, transactions: List[Dict]) -> Dict:
        """Process wallet transactions to extract meaningful metrics."""
        metrics = {
            "total_transactions": len(transactions),
            "successful_trades": 0,
            "failed_trades": 0,
            "unique_tokens_traded": set(),
            "last_active": None
        }

        for tx in transactions:
            if not tx.get("meta", {}).get("err"):
                metrics["successful_trades"] += 1
            else:
                metrics["failed_trades"] += 1

            # Update last active timestamp
            block_time = tx.get("blockTime")
            if block_time:
                timestamp = datetime.fromtimestamp(block_time)
                if not metrics["last_active"] or timestamp > metrics["last_active"]:
                    metrics["last_active"] = timestamp

            # Track unique tokens from token transfers
            for ix in tx.get("meta", {}).get("innerInstructions", []):
                if "tokenTransfers" in ix:
                    for transfer in ix["tokenTransfers"]:
                        if "mint" in transfer:
                            metrics["unique_tokens_traded"].add(transfer["mint"])

        metrics["unique_tokens_traded"] = len(metrics["unique_tokens_traded"])
        return metrics

    async def get_top_traders(self, token_address: str, min_transactions: int = DEFAULT_MIN_TRANSACTIONS) -> List[Dict]:
        """Identify top traders for a specific token based on transaction history."""
        holders = await self.get_token_holders(token_address)
        token_price = await self.get_token_price(token_address)
        
        # Get the first holder to access token metadata
        first_holder = holders[0] if holders else None
        symbol = first_holder.get("symbol", "UNKNOWN") if first_holder else "UNKNOWN"
        
        # Process holders concurrently
        async def process_holder(holder):
            wallet = holder.get("owner")
            if not wallet:
                return None

            analysis = await self.analyze_wallet_transactions(wallet)
            if analysis.get("total_transactions", 0) >= min_transactions:
                amount = holder.get("amount", 0)
                return {
                    "wallet": wallet,
                    "balance": amount,
                    "balance_usd": amount * token_price if token_price else 0,
                    "decimals": holder.get("decimals", 9),
                    "symbol": symbol,
                    **analysis
                }
            return None

        # Process all holders concurrently
        tasks = [process_holder(holder) for holder in holders[:TOP_HOLDERS_LIMIT]]
        traders = await asyncio.gather(*tasks)
        top_traders = [trader for trader in traders if trader is not None]

        return sorted(top_traders, 
                     key=lambda x: (x.get("successful_trades", 0), x.get("balance", 0)), 
                     reverse=True)

    def store_trader_analysis(self, token_address: str, trader_data: List[Dict]):
        """Store trader analysis results in the database."""
        timestamp = datetime.now()
        for trader in trader_data:
            self.db_manager.store_trader_analysis({
                "token_address": token_address,
                "wallet_address": trader["wallet"],
                "balance": trader["balance"],
                "total_transactions": trader["total_transactions"],
                "successful_trades": trader["successful_trades"],
                "failed_trades": trader["failed_trades"],
                "unique_tokens_traded": trader["unique_tokens_traded"],
                "last_active": trader["last_active"],
                "analyzed_at": timestamp
            }) 