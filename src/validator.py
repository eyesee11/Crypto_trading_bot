"""
🛡️ VALIDATOR - The Bot's Safety Inspector

REAL-LIFE ANALOGY:
Think of this as a safety inspector at an airport:
- TSA checks your luggage before you board (validator checks orders before sending)
- "No liquids over 3oz" (minimum quantity requirements)
- "Valid passport required" (valid symbol required)
- "No weapons" (reasonable price limits)

WHY VALIDATION IS CRITICAL:
1. Prevent Costly Mistakes: Stop order for $30M instead of $30
2. API Errors: Binance rejects invalid orders (wastes time, counts against rate limits)
3. User Experience: Give helpful error messages instead of cryptic API errors
4. Safety: Prevent accidentally placing orders at absurd prices

HOW IT WORKS:
Before placing any order, we check:
✓ Symbol exists on Binance
✓ Quantity is within allowed range
✓ Price is reasonable (not 10x away from market)
✓ Sufficient balance available
✓ Order size meets minimum requirements
"""

import re
from typing import Tuple, Optional
from decimal import Decimal, ROUND_DOWN

from .logger_config import setup_logger
from .config import get_symbol_info, get_current_price, get_account_balance, MIN_ORDER_USD, MAX_ORDER_USD, MAX_PRICE_DEVIATION

# Initialize logger
logger = setup_logger('Validator')


# ============================================
# SYMBOL VALIDATION
# ============================================

def validate_symbol(symbol: str) -> Tuple[bool, str]:
    """
    Check if trading symbol is valid and tradeable.
    
    ANALOGY: Like checking if a product exists in a store:
    - "Do you have iPhone 15?" → "Yes, in stock" ✅
    - "Do you have iPhone 99?" → "No such product" ❌
    
    WHAT WE CHECK:
    1. Format: Must be like "BTCUSDT" (uppercase, no spaces)
    2. Exists: Symbol must exist on Binance
    3. Status: Must be actively trading (not delisted/maintenance)
    
    PARAMETERS:
    - symbol: Trading pair string (e.g., "BTCUSDT", "ETHUSDT")
    
    RETURNS:
    - (True, "Valid") if symbol is good
    - (False, "Error message") if symbol has issues
    
    EXAMPLE:
    ```python
    is_valid, message = validate_symbol("BTCUSDT")
    if is_valid:
        print("✅ Symbol is valid!")
    else:
        print(f"❌ Error: {message}")
    ```
    """
    
    # Check 1: Basic format
    # ANALOGY: Like checking if email has @ symbol
    if not symbol or not isinstance(symbol, str):
        return False, "Symbol must be a non-empty string"
    
    # Convert to uppercase (Binance uses uppercase)
    symbol = symbol.upper()
    
    # Check format (letters and numbers only, no spaces/special chars)
    if not re.match(r'^[A-Z0-9]+$', symbol):
        return False, f"Invalid symbol format: {symbol}. Use format like 'BTCUSDT'"
    
    # Check 2: Symbol exists on Binance
    # ANALOGY: Like checking if item is in store catalog
    symbol_info = get_symbol_info(symbol)
    
    if not symbol_info:
        return False, f"Symbol '{symbol}' not found on Binance Futures. Check spelling?"
    
    # Check 3: Trading status
    # ANALOGY: Like checking if store is open
    status = symbol_info.get('status')
    if status != 'TRADING':
        return False, f"Symbol '{symbol}' is not currently tradeable (Status: {status})"
    
    logger.debug(f"✅ Symbol validation passed: {symbol}")
    return True, "Valid"


# ============================================
# QUANTITY VALIDATION
# ============================================

def validate_quantity(symbol: str, quantity: float) -> Tuple[bool, str]:
    """
    Check if order quantity meets requirements.
    
    ANALOGY: Like checking if your order meets store requirements:
    - "Minimum 2 items" (minQty)
    - "Maximum 10 per customer" (maxQty)
    - "Must buy in multiples of 0.5" (stepSize)
    
    BINANCE RULES:
    - minQty: Can't order less than this
    - maxQty: Can't order more than this
    - stepSize: Quantity must be multiple of this (e.g., 0.001 steps)
    
    REAL EXAMPLE:
    For BTCUSDT:
    - minQty: 0.001 BTC ($30 at $30,000/BTC)
    - maxQty: 1000 BTC ($30M at $30,000/BTC)
    - stepSize: 0.001 BTC (can't buy 0.0015, must be 0.001 or 0.002)
    
    PARAMETERS:
    - symbol: Trading pair (e.g., "BTCUSDT")
    - quantity: Amount to trade (e.g., 0.01)
    
    RETURNS:
    - (True, "Valid") if quantity is acceptable
    - (False, "Error message") if quantity has issues
    """
    
    # Check 1: Positive number
    # ANALOGY: Can't buy -5 apples or 0 apples
    if quantity <= 0:
        return False, f"Quantity must be positive (got {quantity})"
    
    # Check 2: Get symbol rules
    symbol_info = get_symbol_info(symbol)
    if not symbol_info:
        return False, f"Could not fetch rules for {symbol}"
    
    # Extract quantity filters
    # ANALOGY: Reading the product label for specifications
    filters = {f['filterType']: f for f in symbol_info.get('filters', [])}
    lot_size = filters.get('LOT_SIZE', {})
    
    min_qty = float(lot_size.get('minQty', 0))
    max_qty = float(lot_size.get('maxQty', float('inf')))
    step_size = float(lot_size.get('stepSize', 0))
    
    # Check 3: Minimum quantity
    if quantity < min_qty:
        return False, f"Quantity {quantity} below minimum {min_qty} for {symbol}"
    
    # Check 4: Maximum quantity
    if quantity > max_qty:
        return False, f"Quantity {quantity} exceeds maximum {max_qty} for {symbol}"
    
    # Check 5: Step size compliance
    # ANALOGY: Like "eggs sold in dozens only" - can't buy 13 eggs
    if step_size > 0:
        # Use Decimal for precise arithmetic
        qty_decimal = Decimal(str(quantity))
        step_decimal = Decimal(str(step_size))
        
        # Check if quantity is a valid multiple of step size
        remainder = qty_decimal % step_decimal
        if remainder != 0:
            # Round down to nearest valid quantity
            valid_qty = float((qty_decimal - remainder).quantize(step_decimal, rounding=ROUND_DOWN))
            return False, f"Quantity {quantity} not valid. Must be multiple of {step_size}. Try {valid_qty}"
    
    logger.debug(f"✅ Quantity validation passed: {quantity} {symbol}")
    return True, "Valid"


# ============================================
# PRICE VALIDATION
# ============================================

def validate_price(symbol: str, price: float, order_type: str = "LIMIT") -> Tuple[bool, str]:
    """
    Check if order price is reasonable.
    
    ANALOGY: Like checking if a price makes sense:
    - Buying iPhone for $10? → Probably a scam ❌
    - Buying iPhone for $10,000? → Overpaying! ❌
    - Buying iPhone for $999? → Reasonable ✅
    
    WHAT WE CHECK:
    1. Positive price (can't sell for $-50)
    2. Price precision (Binance only allows certain decimal places)
    3. Within reasonable range of market price (prevents fat-finger errors)
    
    REAL EXAMPLE:
    If BTC is $30,000:
    - $31,000 = OK (3.3% above market) ✅
    - $35,000 = OK (16.7% above market) ✅
    - $50,000 = WARNING (66% above market) ⚠️
    - $300,000 = ERROR (900% above market) ❌
    
    PARAMETERS:
    - symbol: Trading pair
    - price: Target price for order
    - order_type: "LIMIT", "STOP", etc. (for context in messages)
    
    RETURNS:
    - (True, "Valid") if price is reasonable
    - (False, "Error message") if price is problematic
    """
    
    # Check 1: Positive price
    if price <= 0:
        return False, f"Price must be positive (got {price})"
    
    # Check 2: Get current market price for comparison
    current_price = get_current_price(symbol)
    if not current_price:
        # Can't validate against market, but allow order
        logger.warning(f"⚠️  Could not fetch current price for {symbol}. Skipping market comparison.")
        return True, "Valid (market price unavailable)"
    
    # Check 3: Price deviation from market
    # ANALOGY: Like checking if sale price is realistic
    deviation = abs(price - current_price) / current_price
    
    # For STOP_LIMIT orders, allow larger deviation (limit price compared to stop, not market)
    # For regular LIMIT orders, keep strict validation
    max_deviation = 0.30 if order_type == "STOP_LIMIT" else MAX_PRICE_DEVIATION  # 30% for stop-limit, 10% for limit
    
    if deviation > max_deviation:
        # Price is too far away from market - likely a mistake
        percentage = deviation * 100
        return False, (
            f"Price ${price:,.2f} is {percentage:.1f}% away from market price ${current_price:,.2f}. "
            f"This seems unusual. Current market: ${current_price:,.2f}"
        )
    
    # Check 4: Price precision
    # ANALOGY: Like store only accepting prices like $19.99, not $19.995
    symbol_info = get_symbol_info(symbol)
    if symbol_info:
        price_precision = symbol_info.get('pricePrecision', 2)
        
        # Count decimal places in price
        price_str = f"{price:.10f}".rstrip('0')
        if '.' in price_str:
            decimals = len(price_str.split('.')[1])
            if decimals > price_precision:
                return False, (
                    f"Price has too many decimal places. "
                    f"{symbol} allows {price_precision} decimals. "
                    f"Try {price:.{price_precision}f}"
                )
    
    logger.debug(f"✅ Price validation passed: ${price} for {symbol}")
    return True, "Valid"


# ============================================
# BALANCE VALIDATION
# ============================================

def validate_balance(symbol: str, side: str, quantity: float, price: Optional[float] = None) -> Tuple[bool, str]:
    """
    Check if account has enough balance for the order.
    
    ANALOGY: Like checking if you have enough money before buying:
    - Want to buy $100 item
    - Check wallet: Do I have $100?
    - If yes → Proceed ✅
    - If no → "Insufficient funds" ❌
    
    HOW IT WORKS:
    - BUY: Need enough USDT to purchase
    - SELL: Need enough of the asset to sell
    
    EXAMPLE:
    Want to BUY 0.01 BTC at $30,000:
    - Cost: 0.01 * $30,000 = $300 USDT needed
    - Check: Do I have $300 USDT? (+ small fee buffer)
    
    Want to SELL 0.01 BTC:
    - Check: Do I have 0.01 BTC in my account?
    
    PARAMETERS:
    - symbol: Trading pair (e.g., "BTCUSDT")
    - side: "BUY" or "SELL"
    - quantity: How much to trade
    - price: Price per unit (None for market orders = use current price)
    
    RETURNS:
    - (True, "Valid") if balance sufficient
    - (False, "Error message") if insufficient funds
    """
    
    # Get account balance
    balance = get_account_balance()
    if not balance:
        logger.warning("⚠️  Could not fetch balance. Skipping balance check.")
        return True, "Valid (balance check skipped)"
    
    available_balance = float(balance.get('availableBalance', 0))
    
    # For BUY orders: Need USDT
    if side.upper() == "BUY":
        # Calculate cost
        if price is None:
            # Market order - use current price
            price = get_current_price(symbol)
            if not price:
                logger.warning("⚠️  Could not fetch current price for balance check")
                return True, "Valid (price unavailable)"
        
        # Cost = quantity * price
        cost = quantity * price
        
        # Add 1% buffer for fees and price fluctuation
        cost_with_buffer = cost * 1.01
        
        if available_balance < cost_with_buffer:
            return False, (
                f"Insufficient USDT balance. "
                f"Need ~${cost_with_buffer:.2f}, "
                f"Available: ${available_balance:.2f}"
            )
    
    # For SELL orders: Need the asset
    # Note: This is simplified - in real implementation, we'd check position for futures
    elif side.upper() == "SELL":
        # For futures, we actually need USDT as margin
        # This is a simplified check
        if price is None:
            price = get_current_price(symbol)
        
        if price:
            margin_needed = (quantity * price) * 0.05  # Assuming 20x leverage (5% margin)
            if available_balance < margin_needed:
                return False, (
                    f"Insufficient margin. "
                    f"Need ~${margin_needed:.2f} margin, "
                    f"Available: ${available_balance:.2f}"
                )
    
    logger.debug(f"✅ Balance validation passed: {available_balance} USDT available")
    return True, "Valid"


# ============================================
# ORDER VALUE VALIDATION
# ============================================

def validate_order_value(symbol: str, quantity: float, price: Optional[float] = None) -> Tuple[bool, str]:
    """
    Check if order value (quantity × price) is within acceptable range.
    
    ANALOGY: Like store policies:
    - "Minimum purchase $5" (MIN_ORDER_USD)
    - "Maximum purchase $100,000 per transaction" (MAX_ORDER_USD)
    
    WHY THIS MATTERS:
    1. Binance has minimum notional value (usually $5-10)
    2. Prevents accidental huge orders
    3. Prevents dust orders (too small to be useful)
    
    EXAMPLE:
    Buying 0.0001 BTC at $30,000:
    - Value: 0.0001 * $30,000 = $3
    - Below $5 minimum → REJECTED ❌
    
    Buying 0.001 BTC at $30,000:
    - Value: 0.001 * $30,000 = $30
    - Above $5 minimum → ACCEPTED ✅
    
    PARAMETERS:
    - symbol: Trading pair
    - quantity: Amount to trade
    - price: Price per unit (None = use current market price)
    
    RETURNS:
    - (True, "Valid") if order value acceptable
    - (False, "Error message") if too small or too large
    """
    
    # Get price if not provided
    if price is None:
        price = get_current_price(symbol)
        if not price:
            logger.warning("⚠️  Could not fetch price for value validation")
            return True, "Valid (price unavailable)"
    
    # Calculate order value
    order_value = quantity * price
    
    # Check minimum
    if order_value < MIN_ORDER_USD:
        return False, (
            f"Order value ${order_value:.2f} below minimum ${MIN_ORDER_USD}. "
            f"Increase quantity or choose different symbol."
        )
    
    # Check maximum (safety limit)
    if order_value > MAX_ORDER_USD:
        return False, (
            f"Order value ${order_value:.2f} exceeds safety limit ${MAX_ORDER_USD:,.0f}. "
            f"Please place multiple smaller orders."
        )
    
    logger.debug(f"✅ Order value validation passed: ${order_value:.2f}")
    return True, "Valid"


# ============================================
# SIDE VALIDATION
# ============================================

def validate_side(side: str) -> Tuple[bool, str]:
    """
    Check if order side is valid.
    
    ANALOGY: Like asking "Are you buying or selling?" - must be one or the other.
    
    VALID OPTIONS:
    - "BUY" or "buy" → Normalize to "BUY"
    - "SELL" or "sell" → Normalize to "SELL"
    
    PARAMETERS:
    - side: Order direction (should be "BUY" or "SELL")
    
    RETURNS:
    - (True, "BUY" or "SELL") if valid (normalized to uppercase)
    - (False, "Error message") if invalid
    """
    
    if not side or not isinstance(side, str):
        return False, "Side must be 'BUY' or 'SELL'"
    
    side_upper = side.upper()
    
    if side_upper not in ["BUY", "SELL"]:
        return False, f"Invalid side '{side}'. Must be 'BUY' or 'SELL'"
    
    return True, side_upper


# ============================================
# COMPREHENSIVE ORDER VALIDATION
# ============================================

def validate_order(
    symbol: str,
    side: str,
    quantity: float,
    price: Optional[float] = None,
    order_type: str = "MARKET"
) -> Tuple[bool, str, dict]:
    """
    Comprehensive validation of all order parameters.
    
    ANALOGY: Like TSA security checkpoint - checks EVERYTHING:
    ✓ Valid ID (symbol exists)
    ✓ No prohibited items (valid quantity)
    ✓ Reasonable luggage (price not crazy)
    ✓ Valid ticket (enough balance)
    ✓ Proper documentation (all required fields)
    
    WHAT THIS DOES:
    Runs ALL validation checks in sequence. If any check fails,
    immediately return error. If all pass, return success with
    normalized values.
    
    PARAMETERS:
    - symbol: Trading pair (e.g., "BTCUSDT")
    - side: "BUY" or "SELL"
    - quantity: Amount to trade
    - price: Price per unit (optional for market orders)
    - order_type: Type of order (for logging)
    
    RETURNS:
    Tuple of (success, message, validated_data):
    - success: True if all validations passed
    - message: Error message if failed, "Valid" if passed
    - validated_data: Dictionary with normalized values
    
    EXAMPLE:
    ```python
    success, message, data = validate_order("BTCUSDT", "buy", 0.01, 30000)
    if success:
        # Use data['symbol'], data['side'], etc.
        place_order_with_validated_data(data)
    else:
        print(f"Validation failed: {message}")
    ```
    """
    
    logger.info(f"🔍 Validating {order_type} order: {symbol} {side} {quantity}")
    
    validated_data = {}
    
    # Validation 1: Symbol
    is_valid, message = validate_symbol(symbol)
    if not is_valid:
        logger.error(f"❌ Symbol validation failed: {message}")
        return False, message, {}
    validated_data['symbol'] = symbol.upper()
    
    # Validation 2: Side
    is_valid, normalized_side = validate_side(side)
    if not is_valid:
        logger.error(f"❌ Side validation failed: {normalized_side}")
        return False, normalized_side, {}
    validated_data['side'] = normalized_side
    
    # Validation 3: Quantity
    is_valid, message = validate_quantity(symbol, quantity)
    if not is_valid:
        logger.error(f"❌ Quantity validation failed: {message}")
        return False, message, {}
    validated_data['quantity'] = quantity
    
    # Validation 4: Price (if provided)
    if price is not None:
        is_valid, message = validate_price(symbol, price, order_type)
        if not is_valid:
            logger.error(f"❌ Price validation failed: {message}")
            return False, message, {}
        validated_data['price'] = price
    
    # Validation 5: Order value
    is_valid, message = validate_order_value(symbol, quantity, price)
    if not is_valid:
        logger.error(f"❌ Order value validation failed: {message}")
        return False, message, {}
    
    # Validation 6: Balance
    is_valid, message = validate_balance(symbol, normalized_side, quantity, price)
    if not is_valid:
        logger.error(f"❌ Balance validation failed: {message}")
        return False, message, {}
    
    # All validations passed!
    logger.info(f"✅ All validations passed for {order_type} order")
    return True, "Valid", validated_data


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    """
    Test the validator functions.
    """
    print("\n" + "="*60)
    print("🛡️  TESTING VALIDATOR")
    print("="*60 + "\n")
    
    # Test 1: Valid symbol
    print("Test 1: Validate symbol 'BTCUSDT'")
    valid, msg = validate_symbol("BTCUSDT")
    print(f"Result: {valid} - {msg}\n")
    
    # Test 2: Invalid symbol
    print("Test 2: Validate invalid symbol 'FAKECOIN'")
    valid, msg = validate_symbol("FAKECOIN")
    print(f"Result: {valid} - {msg}\n")
    
    # Test 3: Valid quantity
    print("Test 3: Validate quantity 0.01 for BTCUSDT")
    valid, msg = validate_quantity("BTCUSDT", 0.01)
    print(f"Result: {valid} - {msg}\n")
    
    # Test 4: Too small quantity
    print("Test 4: Validate too small quantity 0.0001 for BTCUSDT")
    valid, msg = validate_quantity("BTCUSDT", 0.0001)
    print(f"Result: {valid} - {msg}\n")
    
    # Test 5: Complete order validation
    print("Test 5: Complete validation for BUY order")
    valid, msg, data = validate_order("BTCUSDT", "BUY", 0.001)
    print(f"Result: {valid} - {msg}")
    if valid:
        print(f"Validated data: {data}\n")
    
    print("="*60)
    print("✅ Validator testing complete!")
    print("="*60)
