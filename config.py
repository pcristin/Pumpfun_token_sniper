"""
Global configuration settings for the PumpFun Token Parser application.
"""

# WebSocket Configuration
WEBSOCKET_URI = "wss://pumpportal.fun/api/data"
WEBSOCKET_RECONNECT_DELAY = 30  # seconds
WEBSOCKET_PING_INTERVAL = 45    # seconds

# Database Configuration
DATABASE_URL = "sqlite:///database/tokens.db"

# Token Security Settings
MAX_SECURITY_SCORE = 5000  # Maximum security score for token validation

# Trader Analytics Configuration
DEFAULT_MIN_TRANSACTIONS = 5     # Minimum transactions for trader analysis
TOP_HOLDERS_LIMIT = 20          # Number of top holders to analyze
ANALYSIS_TIMEFRAME_DAYS = 7     # Default timeframe for transaction analysis
HELIUS_PAGE_SIZE = 1000        # Maximum number of token accounts per page

# Logging Configuration
LOG_DIR = "./utils/logs"
LOG_LEVELS = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red,bg_white"
}

# API Configuration
API_ENDPOINTS = {
    "HELIUS": {
        "BASE_URL": "https://mainnet.helius-rpc.com/?api-key=",
        "METHODS": {
            "TOKEN_ACCOUNTS": "getTokenAccountsByOwner",
            "GET_SIGNATURES": "getSignaturesForAddress",
            "GET_TRANSACTION": "getTransaction"
        }
    }
}

# HTTP Headers
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
} 