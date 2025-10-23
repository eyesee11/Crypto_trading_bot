"""
📝 LOGGER CONFIGURATION - The Bot's Memory System

REAL-LIFE ANALOGY:
Think of this as the bot's detailed diary/journal. Just like how you might keep a diary
to remember what happened each day, the bot keeps logs of:
- Every order it places (like writing "Bought groceries for $50")
- Every error it encounters (like writing "Car broke down, needed mechanic")
- Every API call (like writing "Called bank to check balance")

WHY WE NEED THIS:
1. Debugging: When something goes wrong, logs tell us exactly what happened
2. Audit Trail: Prove what orders were placed and when
3. Learning: Review past actions to improve strategies
4. Compliance: Some regulations require keeping trade records

HOW IT WORKS:
- Creates a file called 'bot.log'
- Timestamps every entry (so you know WHEN it happened)
- Color-codes messages (INFO=green, ERROR=red, etc.)
- Automatically rotates logs (prevents file from getting too big)
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


class ColoredFormatter(logging.Formatter):
    """
    Add colors to console output for better readability.

    """
    
    # ANSI color codes (works in most terminals)
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan - detailed technical info
        'INFO': '\033[32m',       # Green - normal operations
        'WARNING': '\033[33m',    # Yellow - something unusual but not critical
        'ERROR': '\033[31m',      # Red - something went wrong
        'CRITICAL': '\033[35m',   # Magenta - severe error
        'RESET': '\033[0m'        # Reset to default color
    }
    
    def format(self, record):
        """
        Format the log message with colors.
        
        STEP-BY-STEP:
        1. Get the log level (INFO, ERROR, etc.)
        2. Choose appropriate color
        3. Add color codes around the message
        4. Return formatted string
        """
        # Get the original formatted message
        log_message = super().format(record)
        
        # Add color if this is a console handler
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        return f"{color}{log_message}{self.COLORS['RESET']}"


def setup_logger(name: str = 'BinanceBot', log_file: str = 'bot.log', level: str = 'INFO'):
    """
    Set up the logging system for the bot.
    
    PARAMETERS:
    - name: Logger name (like naming your diary)
    - log_file: Where to save logs (the actual diary file)
    - level: How detailed? (DEBUG=everything, INFO=important stuff, ERROR=only problems)
    
    REAL-WORLD EXAMPLE:
    Imagine you're setting up a security camera system:
    - name = "Front Door Camera"
    - log_file = Where video is saved
    - level = Recording quality (HD vs SD)
    
    WHAT THIS DOES:
    1. Creates a logger object (the "camera")
    2. Sets up file handler (saves to disk - like video storage)
    3. Sets up console handler (prints to screen - like live monitor)
    4. Adds timestamps and formatting (like date/time stamp on video)
    """
    
    # Create logger object
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate logs if logger already exists
    if logger.handlers:
        return logger
    
    # ============================================
    # FILE HANDLER - Saves to bot.log
    # ============================================
    # ANALOGY: Like a DVR recording security footage to a hard drive
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else '.'
    if log_dir != '.' and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # RotatingFileHandler: Automatically creates new file when size limit reached
    # ANALOGY: Like having multiple notebooks - when one fills up, start a new one
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB per file (like 100-page notebook)
        backupCount=5,               # Keep 5 old files (like keeping 5 old notebooks)
        encoding='utf-8'             # UTF-8 encoding for emoji support on Windows
    )
    file_handler.setLevel(logging.DEBUG)  # Save EVERYTHING to file
    
    # File format: Include all details (timestamp, level, message)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # ============================================
    # CONSOLE HANDLER - Prints to terminal
    # ============================================
    # ANALOGY: Like a live security monitor showing what's happening right now
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Only show important stuff on screen
    
    # Console format: Simpler, with colors
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'  # Shorter time format for console
    )
    console_handler.setFormatter(console_formatter)
    
    # Attach both handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log that logging is set up (meta!)
    logger.info(f"Logger '{name}' initialized - Logs saved to: {os.path.abspath(log_file)}")
    
    return logger


def log_order(logger, order_type: str, symbol: str, side: str, quantity: float, **kwargs):
    """
    Specialized function to log order details consistently.
    
    ANALOGY: Like having a pre-printed order form at a restaurant:
    - Date/Time: [automatically filled]
    - Table: [symbol like "BTCUSDT"]
    - Order: [BUY or SELL]
    - Quantity: [how much]
    - Special Instructions: [kwargs - extra details]
    
    WHY SEPARATE FUNCTION:
    - Ensures all orders logged the same way
    - Easy to search logs later ("show me all BUY orders")
    - Can add extra validation/formatting
    
    EXAMPLE USAGE:
    ```python
    log_order(logger, "MARKET", "BTCUSDT", "BUY", 0.01)
    # Output: "2025-10-23 10:30:45 - INFO - MARKET Order: BTCUSDT BUY 0.01"
    
    log_order(logger, "LIMIT", "ETHUSDT", "SELL", 0.5, price=2000)
    # Output: "2025-10-23 10:30:46 - INFO - LIMIT Order: ETHUSDT SELL 0.5 @ $2000"
    ```
    """
    extra_info = ' | '.join([f"{k}={v}" for k, v in kwargs.items()])
    message = f"{order_type.upper()} Order: {symbol} {side} {quantity}"
    
    if extra_info:
        message += f" | {extra_info}"
    
    logger.info(message)


def log_error(logger, error_message: str, exception: Exception = None):
    """
    Specialized function to log errors with full details.
    
    ANALOGY: Like an incident report at work:
    - What happened: [error_message]
    - Technical details: [exception traceback]
    - When: [timestamp - automatic]
    
    WHY THIS HELPS:
    - Captures full error details (not just "something broke")
    - Includes stack trace (shows WHERE in code error occurred)
    - Consistent error format makes debugging easier
    
    EXAMPLE:
    ```python
    try:
        result = 10 / 0
    except Exception as e:
        log_error(logger, "Division calculation failed", e)
    # Output: "ERROR - Division calculation failed: ZeroDivisionError: division by zero"
    # Plus full stack trace showing line numbers
    ```
    """
    if exception:
        logger.error(f"{error_message}: {type(exception).__name__}: {str(exception)}", exc_info=True)
    else:
        logger.error(error_message)


def log_success(logger, message: str, **details):
    """
    Log successful operations with details.
    
    ANALOGY: Like a success notification on your phone:
    - ✅ "Payment sent successfully!"
    - Details: Amount, Recipient, Transaction ID
    
    MAKES SUCCESS VISIBLE:
    - Easy to see what worked
    - Track successful orders vs failed ones
    - Helps verify bot is working correctly
    
    EXAMPLE:
    ```python
    log_success(logger, "Order executed", order_id=12345, price=30500, quantity=0.01)
    # Output: "SUCCESS - Order executed | order_id=12345 | price=30500 | quantity=0.01"
    ```
    """
    details_str = ' | '.join([f"{k}={v}" for k, v in details.items()])
    full_message = f"✅ SUCCESS - {message}"
    
    if details_str:
        full_message += f" | {details_str}"
    
    logger.info(full_message)


# ============================================
# EXAMPLE USAGE (for testing this module)
# ============================================
if __name__ == "__main__":
    """
    Test the logging system.
    
    WHAT THIS DOES:
    If you run this file directly (python logger_config.py), it will:
    1. Create a test logger
    2. Log different types of messages
    3. Show you how the output looks
    
    ANALOGY: Like doing a sound check before a concert
    """
    
    # Create test logger
    test_logger = setup_logger('TestBot', 'test_bot.log')
    
    # Test different log levels
    test_logger.debug("This is a debug message (very detailed)")
    test_logger.info("This is an info message (normal operation)")
    test_logger.warning("This is a warning (something unusual)")
    test_logger.error("This is an error message (something went wrong)")
    
    # Test specialized logging functions
    log_order(test_logger, "MARKET", "BTCUSDT", "BUY", 0.01)
    log_order(test_logger, "LIMIT", "ETHUSDT", "SELL", 0.5, price=2000)
    log_success(test_logger, "Order filled", order_id=12345, price=30500.50)
    
    # Test error logging
    try:
        # Intentional error for testing
        result = 10 / 0
    except Exception as e:
        log_error(test_logger, "Test error occurred", e)
    
    print("\n✅ Logging test complete! Check 'test_bot.log' file.")
