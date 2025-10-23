"""
Binance Futures Trading Bot

A comprehensive CLI-based trading bot for Binance USDT-M Futures.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

# Make key functions easily importable
from .config import get_client, test_connection, get_account_balance
from .validator import validate_order
from .logger_config import setup_logger

__all__ = [
    'get_client',
    'test_connection',
    'get_account_balance',
    'validate_order',
    'setup_logger'
]
