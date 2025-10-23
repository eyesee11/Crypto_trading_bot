"""
⚙️ CONFIGURATION - The Bot's ID Card and Connection Settings

REAL-LIFE ANALOGY:
Think of this file as your bot's "wallet and ID card":
- API Key = Your username/email
- API Secret = Your password
- Testnet flag = "Practice mode" vs "Real money mode"
- Client = Your connection to the bank (Binance)

WHY THIS FILE EXISTS:
1. Security: Keep API keys in one secure place (not scattered in code)
2. Flexibility: Easily switch between testnet and production
3. Reusability: All files use same configuration
4. Safety: Load from .env file (never commit secrets to GitHub)

HOW IT WORKS:
1. Load environment variables from .env file
2. Create Binance client with those credentials
3. Export functions that other files can use
"""

import os
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv
from typing import Optional

from logger_config import setup_logger

# Initialize logger for this module
logger = setup_logger('Config')

# ============================================
# STEP 1: Load Environment Variables
# ============================================
# ANALOGY: Opening your wallet to get your credit card info

# Load .env file (contains API_KEY and API_SECRET)
load_dotenv()

# Read configuration from environment
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
USE_TESTNET = os.getenv('BINANCE_TESTNET', 'True').lower() == 'true'
TESTNET_URL = os.getenv('BINANCE_TESTNET_URL', 'https://testnet.binancefuture.com')

# ============================================
# STEP 2: Validate Configuration
# ============================================
# ANALOGY: Checking that your credit card isn't expired before shopping

if not API_KEY or not API_SECRET:
    logger.error("❌ API credentials not found!")
    logger.error("Please create a .env file with BINANCE_API_KEY and BINANCE_API_SECRET")
    logger.error("See .env.example for template")
    raise ValueError("Missing API credentials - Cannot proceed without API keys")

# Warn if using production (real money!)
if not USE_TESTNET:
    logger.warning("⚠️  WARNING: PRODUCTION MODE - REAL MONEY AT RISK!")
    logger.warning("⚠️  Make sure you know what you're doing!")
else:
    logger.info("✅ Testnet mode enabled - Safe to practice!")


# ============================================
# STEP 3: Create Binance Client
# ============================================
# ANALOGY: Logging into your bank's website with username/password

def get_client() -> Client:
    """
    Create and return a configured Binance client.
    
    WHAT THIS DOES:
    Creates a connection to Binance API (like logging into a website).
    
    WHY A FUNCTION:
    - Can create multiple clients if needed
    - Easy to mock/test
    - Handles errors in one place
    
    REAL-WORLD EXAMPLE:
    Like calling your bank and providing credentials:
    - Bank: "Please enter your account number" (API_KEY)
    - You: "123456"
    - Bank: "Please enter your PIN" (API_SECRET)
    - You: "****"
    - Bank: "Access granted! How can I help?"
    
    RETURNS:
    - Client object that can place orders, check balances, etc.
    """
    try:
        # Create client with credentials
        client = Client(
            api_key=API_KEY,
            api_secret=API_SECRET,
            testnet=USE_TESTNET  # True = fake money, False = real money
        )
        
        # If testnet, set custom URL
        if USE_TESTNET:
            # Override URLs for testnet
            client.API_URL = TESTNET_URL
            client.FUTURES_URL = TESTNET_URL
            logger.info(f"📡 Connected to Binance Testnet: {TESTNET_URL}")
        else:
            logger.info("📡 Connected to Binance PRODUCTION")
        
        return client
        
    except BinanceAPIException as e:
        logger.error(f"❌ Failed to create Binance client: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error creating client: {e}")
        raise


# ============================================
# STEP 4: Helper Functions
# ============================================

def test_connection() -> bool:
    """
    Test if API credentials work.
    
    ANALOGY: Like checking if your credit card works before shopping:
    - Swipe card at ATM
    - If balance shows = card works ✅
    - If "invalid card" = something wrong ❌
    
    WHAT THIS DOES:
    1. Create client
    2. Try to fetch account info (simple API call)
    3. If successful = credentials work
    4. If error = credentials invalid or network issue
    
    RETURNS:
    - True if connection successful
    - False if connection failed
    
    EXAMPLE USAGE:
    ```python
    if test_connection():
        print("✅ Ready to trade!")
    else:
        print("❌ Check your API keys")
    ```
    """
    try:
        client = get_client()
        
        # Try to get account info (simple test call)
        # ANALOGY: Like asking "What's my balance?" to verify card works
        account_info = client.futures_account()
        
        # If we get here, connection works!
        logger.info("✅ Connection test successful!")
        logger.info(f"📊 Account balance: {account_info.get('totalWalletBalance', 'N/A')} USDT")
        
        return True
        
    except BinanceAPIException as e:
        logger.error(f"❌ Connection test failed: {e.message}")
        logger.error("💡 Check: API keys correct? Testnet flag correct? Internet working?")
        return False
        
    except Exception as e:
        logger.error(f"❌ Connection test failed: {str(e)}")
        return False


def get_account_balance() -> Optional[dict]:
    """
    Get current account balance.
    
    ANALOGY: Like checking your bank balance:
    - Open banking app
    - Click "View Balance"
    - See: $1,234.56 available
    
    RETURNS:
    - Dictionary with balance info if successful
    - None if error
    
    EXAMPLE OUTPUT:
    {
        'asset': 'USDT',
        'balance': '10000.00',
        'available': '9500.00',
        'inOrder': '500.00'
    }
    
    USAGE:
    ```python
    balance = get_account_balance()
    if balance:
        print(f"You have {balance['available']} USDT available")
    ```
    """
    try:
        client = get_client()
        account = client.futures_account()
        
        # Find USDT balance (most common trading currency)
        for asset in account.get('assets', []):
            if asset['asset'] == 'USDT':
                logger.info(f"💰 Balance: {asset['walletBalance']} USDT")
                return asset
        
        logger.warning("⚠️  USDT balance not found")
        return None
        
    except Exception as e:
        logger.error(f"❌ Failed to get balance: {str(e)}")
        return None


def get_symbol_info(symbol: str) -> Optional[dict]:
    """
    Get trading rules for a symbol (min quantity, price precision, etc.)
    
    ANALOGY: Like reading product specifications before buying:
    - Min order: 0.001 BTC (like "Minimum purchase: 2 items")
    - Price step: 0.01 (like "Prices in $0.01 increments")
    - Max quantity: 1000 BTC (like "Maximum 10 per customer")
    
    WHY THIS MATTERS:
    - Can't buy 0.0001 BTC if minimum is 0.001
    - Can't set price to $30123.456 if only 2 decimals allowed
    - Prevents "invalid quantity" errors
    
    PARAMETERS:
    - symbol: Trading pair like "BTCUSDT" or "ETHUSDT"
    
    RETURNS:
    - Dictionary with symbol rules if found
    - None if symbol doesn't exist
    
    EXAMPLE OUTPUT:
    {
        'symbol': 'BTCUSDT',
        'status': 'TRADING',
        'minQty': '0.001',
        'maxQty': '1000',
        'stepSize': '0.001',
        'pricePrecision': 2
    }
    """
    try:
        client = get_client()
        exchange_info = client.futures_exchange_info()
        
        # Search for our symbol in list of all symbols
        for symbol_data in exchange_info['symbols']:
            if symbol_data['symbol'] == symbol:
                logger.debug(f"📋 Found info for {symbol}")
                return symbol_data
        
        logger.warning(f"⚠️  Symbol {symbol} not found")
        return None
        
    except Exception as e:
        logger.error(f"❌ Failed to get symbol info: {str(e)}")
        return None


def get_current_price(symbol: str) -> Optional[float]:
    """
    Get current market price for a symbol.
    
    ANALOGY: Like checking the price tag in a store:
    - Walk to item
    - Look at price tag
    - See: "$29.99"
    
    WHY WE NEED THIS:
    - Before placing limit order, check current price
    - Calculate potential profit/loss
    - Validate user input (e.g., "price too far from market")
    
    PARAMETERS:
    - symbol: Trading pair like "BTCUSDT"
    
    RETURNS:
    - Current price as float (e.g., 30500.50)
    - None if error
    
    EXAMPLE:
    ```python
    current_price = get_current_price("BTCUSDT")
    print(f"Bitcoin is currently ${current_price}")
    # Output: Bitcoin is currently $30500.50
    ```
    """
    try:
        client = get_client()
        ticker = client.futures_symbol_ticker(symbol=symbol)
        price = float(ticker['price'])
        
        logger.debug(f"💵 Current price for {symbol}: ${price}")
        return price
        
    except Exception as e:
        logger.error(f"❌ Failed to get price for {symbol}: {str(e)}")
        return None


# ============================================
# CONFIGURATION CONSTANTS
# ============================================
# These are used throughout the bot for validation and settings

# Order size limits (to prevent accidents)
MIN_ORDER_USD = 5.0      # Minimum order value in USD (Binance requirement)
MAX_ORDER_USD = 100000.0  # Maximum order value (safety limit)

# Price deviation limits (prevent accidentally placing order at crazy price)
MAX_PRICE_DEVIATION = 0.10  # 10% from current price (safety check)

# Timing
DEFAULT_TIMEOUT = 30  # Seconds to wait for API response

# Rate limiting (to avoid getting banned by Binance)
MAX_REQUESTS_PER_MINUTE = 1200  # Binance limit
WEIGHT_PER_MINUTE = 2400        # Binance weight limit


# ============================================
# EXAMPLE USAGE & TESTING
# ============================================
if __name__ == "__main__":
    """
    Test the configuration and connection.
    
    WHAT THIS DOES:
    If you run this file directly (python config.py), it will:
    1. Load API credentials
    2. Test connection to Binance
    3. Show account balance
    4. Show current BTC price
    
    ANALOGY: Like doing a system check before starting work
    """
    
    print("\n" + "="*50)
    print("🔧 TESTING BINANCE CONFIGURATION")
    print("="*50 + "\n")
    
    # Test 1: Connection
    print("Test 1: Testing API connection...")
    if test_connection():
        print("✅ Connection successful!\n")
    else:
        print("❌ Connection failed - Check your .env file\n")
        exit(1)
    
    # Test 2: Balance
    print("Test 2: Checking account balance...")
    balance = get_account_balance()
    if balance:
        print(f"✅ Balance: {balance['walletBalance']} USDT\n")
    else:
        print("❌ Could not fetch balance\n")
    
    # Test 3: Get BTC price
    print("Test 3: Getting current BTC price...")
    btc_price = get_current_price("BTCUSDT")
    if btc_price:
        print(f"✅ BTC Price: ${btc_price:,.2f}\n")
    else:
        print("❌ Could not fetch BTC price\n")
    
    # Test 4: Symbol info
    print("Test 4: Getting BTCUSDT trading rules...")
    symbol_info = get_symbol_info("BTCUSDT")
    if symbol_info:
        print(f"✅ Symbol: {symbol_info['symbol']}")
        print(f"   Status: {symbol_info['status']}")
        print(f"   Price Precision: {symbol_info['pricePrecision']}")
        print(f"   Quantity Precision: {symbol_info['quantityPrecision']}\n")
    else:
        print("❌ Could not fetch symbol info\n")
    
    print("="*50)
    print("✅ Configuration test complete!")
    print("="*50)
