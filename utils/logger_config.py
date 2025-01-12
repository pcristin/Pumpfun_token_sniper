import logging
import colorlog
import os
from datetime import datetime

# Ensure the logs directory exists
log_dir = './utils/logs'
os.makedirs(log_dir, exist_ok=True)

# Generate a unique log file name based on the current time and date
log_filename = datetime.now().strftime("%H_%M %d_%m_%y") + '.log'
log_filepath = os.path.join(log_dir, log_filename)

class CustomFormatter(logging.Formatter):
    """
    Custom formatter to handle optional 'module_name' and 'address' in log records.
    If 'module_name' or 'address' is not provided, they default to 'N/A'.
    """
    def format(self, record):
        if not hasattr(record, 'module_name'):
            record.module_name = 'N/A'
        if not hasattr(record, 'address'):
            record.address = 'N/A'
        return super().format(record)

# Set up the main logger
logger = logging.getLogger('pumpfun_logger')
logger.setLevel(logging.DEBUG)

# Prevent adding multiple handlers if logger_config is imported multiple times
if not logger.hasHandlers():
    # Create a file handler
    file_handler = logging.FileHandler(log_filepath)
    file_handler.setLevel(logging.DEBUG)

    # Create a console handler with colorlog
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Set to INFO level

    # Define log formats
    file_formatter = CustomFormatter('%(asctime)s - %(levelname)s - [%(module_name)s] - (%(address)s): %(message)s')
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - [%(module_name)s] - (%(address)s): %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    # Assign formatters to handlers
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
