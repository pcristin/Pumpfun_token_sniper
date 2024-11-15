# PumpFun Token Parser

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Logging](#logging)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Overview

PumpFun Token Parser is a Python-based application designed to monitor and analyze new token events in real-time via WebSocket connections. It integrates with the [RugCheck](https://rugcheck.xyz/) API to assess token risks and stores validated tokens into a structured database for further analysis or monitoring.

## Features

- **Real-Time Monitoring**: Connects to PumpFun's WebSocket to receive live token data.
- **Risk Analysis**: Utilizes the RugCheck API to evaluate the security and reliability of tokens.
- **Database Integration**: Stores validated tokens along with their risk profiles using SQLAlchemy.
- **Graceful Shutdown**: Handles system signals to ensure smooth termination without data loss.
- **Comprehensive Logging**: Implements a centralized logging system with color-coded console output for easy debugging and monitoring.

## Architecture

The application consists of the following core components:

1. **WebSocket Client (`new_pumpfun_parser.py`)**: Connects to the WebSocket, subscribes to new token events, and handles incoming messages.
2. **Risk Analyzer (`rug_check.py`)**: Interfaces with the RugCheck API to analyze the risks associated with each token.
3. **Database Manager (`database.py`)**: Manages database connections and operations using SQLAlchemy.
4. **Logging Configuration (`utils/logger_config.py`)**: Sets up centralized logging with file and console handlers.
5. **Main Application (`main.py`)**: Initializes and orchestrates the parser.

## Installation

### Prerequisites

- **Python 3.11**: Ensure you have Python 3.11 installed. You can download it from the [official website](https://www.python.org/downloads/).
- **requirements.txt**: Install the required packages using `pip install -r requirements.txt`.

### Clone the Repository

```bash
git clone https://github.com/yourusername/pumpfun-token-parser.git
cd pumpfun-token-parser
```

### Set Up Virtual Environment
```bash
python -m venv .venv
```
For Mac/Linux:
```bash
source .venv/bin/activate
```

For Windows:
```bash
.venv\Scripts\activate
```

### Install Requirements
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Configure .gitignore
Ensure your `.gitignore` includes the following to exclude sensitive files and directories:
```
*.db
*.log
*.json
*.csv
*.jsonl
```

## Configuration
### WebSocket URI
The application connects to PumpFun's WebSocket. By default, the URI is set in `main.py`:
```python
ws_uri = "wss://pumpportal.fun/api/data"
```
You can change this URI to connect to a different PumpFun instance or a local development environment.

### Database Configuration
The application uses SQLAlchemy to manage database connections. By default, it connects to a SQLite database file named `pumpfun_tokens.db` located in the root directory. You can modify the database URI in `database.py` to connect to a different database or remote server.
```python
engine = create_engine('sqlite:///tokens.db') # Default SQLite
```

For PostgreSQL:
```python
engine = create_engine('postgresql://user:password@localhost:5432/tokens')
```

Ensure you have the appropriate database driver installed, such as `psycopg2` for PostgreSQL:
```bash
pip install psycopg2-binary
```


### Logging Configuration

Logs are managed centrally via `utils/logger_config.py`. Logs are saved in the `./utils/logs/` directory with unique filenames based on the current date and time.

**Log Levels:**

- **DEBUG**: Detailed information, typically of interest only when diagnosing problems.
- **INFO**: Confirmation that things are working as expected.
- **WARNING**: An indication that something unexpected happened.
- **ERROR**: Due to a more serious problem, the software has not been able to perform some function.
- **CRITICAL**: A serious error, indicating that the program itself may be unable to continue running.

**Colored Console Output:**

- **DEBUG**: Cyan
- **INFO**: Green
- **WARNING**: Yellow
- **ERROR**: Red
- **CRITICAL**: Red with white background

## Usage

### Running the Application

Activate your virtual environment if not already active:
1) For Mac/Linux:
```bash
source .venv/bin/activate
```
2) For Windows:
```bash
.venv\Scripts\activate
```

Run the application:
```bash
python main.py
```

### Graceful Shutdown

To terminate the application gracefully, send a `SIGINT` signal (e.g., press `Ctrl+C` in the terminal). The application will:

1. Close the WebSocket connection.
2. Commit any pending database transactions.
3. Close the database session.
4. Save and finalize log files.

### Monitoring Logs

Logs are saved in the `./utils/logs/` directory. Each log file is named based on the current date and time (e.g., `12_13 15_11_24.log`).

**Console Output:**

The console displays logs with color-coding based on severity levels for easy monitoring during runtime.

## Logging

The application uses a centralized logging system configured in `utils/logger_config.py`. It handles both file and console logging with the following features:

- **File Logging**: Captures all logs (DEBUG and above) into timestamped log files for persistent storage and later analysis.
- **Console Logging**: Displays logs (INFO and above) in the terminal with color-coded messages for real-time monitoring.
- **Contextual Information**: Logs include token-specific information (`token_name`) when available, enhancing the traceability of events.

### Example Log Entries
```
2023-12-13 15:11:24,123 - DEBUG - (TOKEN1): Attempting to connect to WebSocket...
2023-12-13 15:11:25,456 - INFO - (TOKEN1): WebSocket connection established.
2023-12-13 15:11:26,789 - DEBUG - (TOKEN1): Received data: {'mint': '0xABC123...', 'name': 'TokenName', ...}
2023-12-13 15:11:27,012 - INFO - (TokenSymbol): Token Symbol has detected 2 risks
2023-12-13 15:11:28,345 - ERROR - (TokenSymbol): Token TOKENMINT failed security filters.
```
## Project Structure
```
pumpfun-token-parser/
├── main.py
├── new_pumpfun_parser.py
├── rug_check.py
├── database.py
├── utils/
│   └── logger_config.py
│   └── logs/
│       └── *.log
| LICENSE
| README.md
```


## Contributing

Contributions are welcome! Please follow the steps below to contribute:

1. **Fork the Repository**

2. **Create a New Branch**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. **Make Your Changes**

4. **Commit Your Changes**

   ```bash
   git commit -m "Add some feature"
   ```

5. **Push to Your Fork**

   ```bash
   git push origin feature/YourFeatureName
   ```

6. **Open a Pull Request**

   Describe your changes and submit a pull request for review.

## License

Distributed under the [MIT License](./LICENSE). See `LICENSE` for more information.

---

🔒 **Security Notice:** Always ensure that sensitive information, such as API keys or database credentials, are **not** hard-coded and are excluded from version control using `.gitignore`.

---

© 2024 PumpFun Token Parser. All rights reserved.