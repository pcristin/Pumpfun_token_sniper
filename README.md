# PumpFun Token Parser

A real-time token monitoring and analysis tool for the Solana blockchain.

## Features

### Real-Time Token Monitoring
- WebSocket integration for instant token detection
- Automatic validation and risk assessment
- Real-time notifications of new token launches

### Trader Analytics
- Track and analyze top traders for any Solana token
- Detailed metrics including:
  - Token holdings with USD value
  - Transaction history and success rates
  - Trading patterns and activity timeline
  - Unique tokens traded
- Historical data storage for trend analysis
- Concurrent processing for efficient data gathering

### Risk Analysis
- Token contract validation
- Security score calculation
- Risk factor identification
- Automated risk assessment

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pumpfun-token-parser.git
cd pumpfun-token-parser
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### API Keys
- Helius API Key (Required for trader analytics)
  - Sign up at [Helius](https://helius.xyz)
  - Get your API key from the dashboard

### Environment Setup
The application uses the following configuration files:
- `config.py`: Global configuration settings
- `database/database.py`: Database configuration and models

## Usage

Run the application with your Helius API key:
```bash
python main.py --api-key YOUR_HELIUS_API_KEY
```

### Interactive Menu
The application provides an interactive menu with the following options:

1. **Monitor New Tokens (Real-time)**
   - Start real-time monitoring of new token launches
   - Automatically analyze traders for new tokens
   - Store analysis results in the database

2. **Analyze Specific Token**
   - Input a token address to analyze its traders
   - View detailed trader metrics including:
     - Wallet address
     - Token balance with USD value
     - Transaction statistics
     - Trading success rate
     - Last active timestamp

3. **Exit**
   - Gracefully shut down the application

### Example Output
```
Top Traders:
1. Wallet: AbC...XyZ
   Balance: $BONK 1,000,000.000000000 ($1,234.56)
   Total Transactions: 150
   Successful Trades: 120
   Failed Trades: 30
   Unique Tokens Traded: 45
   Last Active: 2024-01-13 12:34:56
```

## Database Integration

The application uses SQLAlchemy for database management with two main models:
- `Token`: Stores validated token information
- `TraderAnalysis`: Stores trader analytics data

### Data Storage
- Automatic database initialization
- Connection pooling for efficient access
- Automatic schema updates
- Transaction-based data storage

## Architecture

### Components
- `main.py`: Application entry point and menu interface
- `modules/`:
  - `pumpfun_parser.py`: Token monitoring and validation
  - `trader_analytics.py`: Trader analysis and metrics
  - `rug_check.py`: Risk assessment module
- `database/`: Database models and management
- `utils/`: Utility functions and logging

### Dependencies
- `aiohttp`: Async HTTP client for API calls
- `websockets`: WebSocket client for real-time data
- `sqlalchemy`: Database ORM
- `pandas`: Data analysis and processing
- Additional dependencies in `requirements.txt`

## Logging

Comprehensive logging system with:
- Error tracking
- Performance monitoring
- Activity logging
- Debug information

Logs are stored in the `logs/` directory with daily rotation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.