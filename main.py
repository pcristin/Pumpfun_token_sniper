import asyncio
import argparse
from modules.pumpfun_parser import PumpFunParser
from modules.trader_analytics import TraderAnalytics
import sys

from utils.logger_config import logger
from config import (
    WEBSOCKET_URI,
    DEFAULT_MIN_TRANSACTIONS
)

async def monitor_new_tokens(ws_uri: str, trader_analytics: TraderAnalytics | None = None):
    """Monitor new tokens in real-time with optional trader analytics."""
    if trader_analytics:
        async with trader_analytics as ta:
            parser = PumpFunParser(ws_uri, trader_analytics=ta)
            await parser.run()
    else:
        parser = PumpFunParser(ws_uri)
        await parser.run()

def print_trader_info(trader):
    """Print trader information in a formatted way."""
    balance = trader.get("balance", 0)
    balance_usd = trader.get("balance_usd", 0)
    decimals = trader.get("decimals", 9)
    symbol = trader.get("symbol", "UNKNOWN")
    
    print(f"\nWallet: {trader['wallet']}")
    print(f"Balance: ${symbol} {balance:,.{decimals}f} (${balance_usd:,.2f})")
    print(f"Total Transactions: {trader['total_transactions']}")
    print(f"Successful Trades: {trader['successful_trades']}")
    print(f"Failed Trades: {trader['failed_trades']}")
    print(f"Unique Tokens Traded: {trader['unique_tokens_traded']}")
    if trader.get("last_active"):
        print(f"Last Active: {trader['last_active'].strftime('%Y-%m-%d %H:%M:%S')}")

async def analyze_specific_token(token_address: str, api_key: str):
    """Analyze traders for a specific token."""
    async with TraderAnalytics(api_key) as analytics:
        print(f"\nAnalyzing traders for token: {token_address}")
        traders = await analytics.get_top_traders(token_address)
        
        if not traders:
            print("No traders found for this token.")
            return
            
        print("\nTop Traders:")
        for i, trader in enumerate(traders, 1):
            print(f"\n{i}.", end="")
            print_trader_info(trader)
            
        analytics.store_trader_analysis(token_address, traders)
        print("\nTrader analysis completed and stored in database.")

def print_menu():
    """Print the main menu options."""
    print("\nPumpFun Token Parser - Main Menu")
    print("-" * 40)
    print("1. Monitor New Tokens (Real-time)")
    print("2. Analyze Specific Token")
    print("3. Exit")
    return input("\nSelect an option (1-3): ").strip()

async def main():
    parser = argparse.ArgumentParser(description="PumpFun Token Parser")
    parser.add_argument("--api-key", required=False, help="Helius API key (optional)")
    args = parser.parse_args()

    try:
        # Initialize trader analytics with Helius API key if provided
        trader_analytics = None
        if args.api_key:
            trader_analytics = TraderAnalytics(api_key=args.api_key)

        while True:
            try:
                choice = print_menu()
                
                if choice == "1":
                    logger.info("Starting real-time token monitoring...")
                    try:
                        await monitor_new_tokens(WEBSOCKET_URI, trader_analytics)
                    except KeyboardInterrupt:
                        logger.info("Monitoring stopped by user.")
                        continue  # Return to menu instead of exiting completely
                    except Exception as e:
                        logger.error(f"Error during monitoring: {str(e)}")
                
                elif choice == "2":
                    if not trader_analytics:
                        print("\nError: Trader analytics requires a Helius API key. Please restart the application with --api-key.")
                        continue
                        
                    token_address = input("\nEnter token address to analyze: ").strip()
                    if token_address:
                        logger.info(f"Analyzing token: {token_address}")
                        await analyze_specific_token(token_address, args.api_key)
                    else:
                        logger.warning("No token address provided.")
                
                elif choice == "3":
                    logger.info("Exiting application...")
                    break
                
                else:
                    print("\nInvalid option. Please try again.")
                    
            except KeyboardInterrupt:
                logger.info("Received interrupt signal. Exiting application...")
                break  # Exit the main loop on Ctrl+C
                
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        logger.info("Application shutdown complete.")
        sys.exit()