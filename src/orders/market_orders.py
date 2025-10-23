"""
🛒 MARKET ORDERS - The "Buy Now" Button

REAL-LIFE ANALOGY:
Think of market orders like Amazon's "Buy Now" button:
- You want something RIGHT NOW
- You accept whatever the current price is
- Immediate execution (usually fills in < 1 second)
- Price might be slightly different than what you saw (like surge pricing)

EXAMPLE SCENARIOS:

1. Emergency Exit:
   - Bitcoin crashing, you need to sell NOW
   - Don't care about exact price, just GET OUT
   - Use market SELL order

2. FOMO (Fear Of Missing Out):
   - Bitcoin breaking out, price rising fast
   - Afraid you'll miss the move
   - Use market BUY order to get in immediately

3. Quick Trade:
   - Saw news that will move price
   - Need to act in seconds
   - Market order executes fastest

WHY USE MARKET ORDERS:
✅ Instant execution (fills immediately)
✅ Simple (just symbol, side, quantity)
✅ Guaranteed to fill (unless extreme conditions)
✅ No waiting for specific price

WHEN NOT TO USE:
❌ Thin markets (low liquidity) - might get bad price
❌ Large orders - can move the market against you
❌ Want specific price - use limit order instead
❌ Not urgent - limit order might get better price

HOW MARKET ORDERS WORK:
1. You say "Buy 0.01 BTC at market price"
2. Exchange looks at order book:
   - Seller A: Selling 0.005 BTC @ $30,100
   - Seller B: Selling 0.005 BTC @ $30,105
   - Seller C: Selling 0.01 BTC @ $30,110
3. Your order "eats" through sellers:
   - Takes 0.005 from Seller A
   - Takes 0.005 from Seller B
4. Average fill price: ~$30,102.50
5. Order complete in milliseconds!

TECHNICAL DETAILS:
- Order Type: MARKET
- Time In Force: Not needed (fills immediately)
- Slippage: Possible in volatile markets
- Fees: Usually 0.02% - 0.04% (taker fees)
"""

import sys
import os
from typing import Dict, Optional
from binance.exceptions import BinanceAPIException

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_client, get_current_price
from validator import validate_order
from logger_config import setup_logger, log_order, log_error, log_success

# Initialize logger
logger = setup_logger('MarketOrders')


def place_market_order(
    symbol: str,
    side: str,
    quantity: float,
    reduce_only: bool = False
) -> Optional[Dict]:
    """
    Place a market order on Binance Futures.
    
    PARAMETERS EXPLAINED:
    
    - symbol: Trading pair (e.g., "BTCUSDT", "ETHUSDT")
      ANALOGY: Which product you're buying/selling
      
    - side: "BUY" or "SELL"
      ANALOGY: Are you buying or selling?
      
    - quantity: Amount to trade (e.g., 0.01 BTC)
      ANALOGY: How many units you want
      
    - reduce_only: (Optional) If True, only reduces existing position
      ANALOGY: Like "close position only" - prevents opening new positions
      Use case: You have a long position, want to close it, but don't want to
                accidentally open a short if order is too large
    
    STEP-BY-STEP PROCESS:
    
    Step 1: VALIDATE inputs
           - Check symbol exists
           - Check quantity is valid
           - Check balance is sufficient
           - If any check fails → STOP, return error
    
    Step 2: GET CURRENT PRICE (for logging/reference)
           - Fetch current market price
           - Log it so user knows approximate execution price
    
    Step 3: SEND ORDER to Binance
           - Create order parameters
           - Send to Binance API
           - Wait for response
    
    Step 4: HANDLE RESPONSE
           - If success → Log details, return order info
           - If error → Log error, return None
    
    RETURNS:
    - Dictionary with order details if successful
    - None if order failed
    
    EXAMPLE SUCCESSFUL RESPONSE:
    {
        'orderId': 12345,
        'symbol': 'BTCUSDT',
        'status': 'FILLED',
        'side': 'BUY',
        'type': 'MARKET',
        'executedQty': '0.01',
        'avgPrice': '30102.50',
        'updateTime': 1635789012345
    }
    
    REAL-WORLD EXAMPLE:
    ```python
    # Buy 0.01 BTC immediately at market price
    order = place_market_order("BTCUSDT", "BUY", 0.01)
    
    if order:
        print(f"✅ Bought {order['executedQty']} BTC")
        print(f"💰 Average price: ${order['avgPrice']}")
        print(f"🆔 Order ID: {order['orderId']}")
    else:
        print("❌ Order failed - check logs")
    ```
    """
    
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"📝 PLACING MARKET ORDER")
        logger.info(f"{'='*60}")
        
        # ============================================
        # STEP 1: VALIDATION
        # ============================================
        # ANALOGY: Like security checkpoint at airport
        
        logger.info(f"🔍 Step 1: Validating order parameters...")
        
        is_valid, message, validated_data = validate_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=None,  # No price for market orders
            order_type="MARKET"
        )
        
        if not is_valid:
            logger.error(f"❌ Validation failed: {message}")
            return None
        
        # Use validated (normalized) values
        symbol = validated_data['symbol']
        side = validated_data['side']
        
        logger.info(f"✅ Validation passed!")
        
        # ============================================
        # STEP 2: GET CURRENT PRICE (for reference)
        # ============================================
        # ANALOGY: Like checking price tag before clicking "Buy Now"
        
        logger.info(f"💵 Step 2: Fetching current market price...")
        
        current_price = get_current_price(symbol)
        if current_price:
            estimated_cost = quantity * current_price
            logger.info(f"   Current {symbol} price: ${current_price:,.2f}")
            logger.info(f"   Estimated order value: ${estimated_cost:,.2f}")
        else:
            logger.warning("⚠️  Could not fetch current price (order will still proceed)")
        
        # ============================================
        # STEP 3: CREATE AND SEND ORDER
        # ============================================
        # ANALOGY: Like clicking "Confirm Purchase" button
        
        logger.info(f"📤 Step 3: Sending order to Binance...")
        
        # Get Binance client
        client = get_client()
        
        # Build order parameters
        order_params = {
            'symbol': symbol,
            'side': side,
            'type': 'MARKET',
            'quantity': quantity,
        }
        
        # Add reduce_only if specified
        # ANALOGY: Like "close position only" checkbox
        if reduce_only:
            order_params['reduceOnly'] = True
            logger.info("   📌 Reduce-only mode enabled (will only close existing position)")
        
        logger.info(f"   Order parameters: {order_params}")
        
        # Log the order attempt
        log_order(
            logger,
            "MARKET",
            symbol,
            side,
            quantity,
            reduce_only=reduce_only
        )
        
        # SEND ORDER TO BINANCE
        # This is the critical moment!
        response = client.futures_create_order(**order_params)
        
        # ============================================
        # STEP 4: PROCESS RESPONSE
        # ============================================
        # ANALOGY: Like getting order confirmation email
        
        logger.info(f"📨 Step 4: Processing response...")
        
        # Extract key information
        order_id = response.get('orderId')
        status = response.get('status')
        executed_qty = float(response.get('executedQty', 0))
        
        # Calculate average fill price if available
        if 'avgPrice' in response and response['avgPrice']:
            avg_price = float(response['avgPrice'])
        elif 'price' in response and response['price']:
            avg_price = float(response['price'])
        else:
            # Fallback to current price if not in response
            avg_price = current_price if current_price else 0
        
        # Calculate total value
        total_value = executed_qty * avg_price if avg_price else 0
        
        # Log success with details
        log_success(
            logger,
            f"Market order executed",
            order_id=order_id,
            status=status,
            symbol=symbol,
            side=side,
            quantity=executed_qty,
            avg_price=f"${avg_price:,.2f}",
            total_value=f"${total_value:,.2f}"
        )
        
        # Print user-friendly summary
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ ORDER SUCCESSFULLY EXECUTED!")
        logger.info(f"{'='*60}")
        logger.info(f"🆔 Order ID: {order_id}")
        logger.info(f"📊 Symbol: {symbol}")
        logger.info(f"↗️  Side: {side}")
        logger.info(f"📦 Quantity: {executed_qty}")
        logger.info(f"💰 Average Price: ${avg_price:,.2f}")
        logger.info(f"💵 Total Value: ${total_value:,.2f}")
        logger.info(f"📈 Status: {status}")
        logger.info(f"{'='*60}\n")
        
        return response
        
    except BinanceAPIException as e:
        # Binance-specific errors
        # ANALOGY: Like getting "Payment declined" from credit card
        
        error_msg = f"Binance API Error: {e.message}"
        log_error(logger, error_msg, e)
        
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ ORDER FAILED")
        logger.error(f"{'='*60}")
        logger.error(f"Error Code: {e.code}")
        logger.error(f"Error Message: {e.message}")
        logger.error(f"{'='*60}\n")
        
        # Common error codes and helpful messages
        if e.code == -2010:
            logger.error("💡 Hint: Insufficient balance or margin")
        elif e.code == -1111:
            logger.error("💡 Hint: Precision error - check quantity decimal places")
        elif e.code == -1021:
            logger.error("💡 Hint: Timestamp error - check system time")
        
        return None
        
    except Exception as e:
        # Unexpected errors
        # ANALOGY: Like store's system crashing during checkout
        
        error_msg = "Unexpected error placing market order"
        log_error(logger, error_msg, e)
        
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ UNEXPECTED ERROR")
        logger.error(f"{'='*60}")
        logger.error(f"Error: {str(e)}")
        logger.error(f"{'='*60}\n")
        
        return None


def get_order_status(symbol: str, order_id: int) -> Optional[Dict]:
    """
    Check the status of an order.
    
    ANALOGY: Like tracking a package after ordering online:
    - "Where is my order?"
    - "Has it shipped yet?"
    - "Is it delivered?"
    
    USEFUL FOR:
    - Confirming order was filled
    - Checking fill price
    - Verifying execution
    
    PARAMETERS:
    - symbol: Trading pair (e.g., "BTCUSDT")
    - order_id: The order ID from place_market_order response
    
    RETURNS:
    - Dictionary with order status
    - None if error
    
    EXAMPLE:
    ```python
    # Place order
    order = place_market_order("BTCUSDT", "BUY", 0.01)
    
    # Check status
    if order:
        status = get_order_status("BTCUSDT", order['orderId'])
        print(f"Order status: {status['status']}")
        print(f"Filled quantity: {status['executedQty']}")
    ```
    """
    try:
        client = get_client()
        order_info = client.futures_get_order(symbol=symbol, orderId=order_id)
        
        logger.info(f"📋 Order {order_id} status: {order_info.get('status')}")
        return order_info
        
    except Exception as e:
        log_error(logger, f"Failed to get order status for {order_id}", e)
        return None


# ============================================
# COMMAND-LINE INTERFACE
# ============================================

def main():
    """
    Command-line interface for market orders.
    
    USAGE:
    python market_orders.py SYMBOL SIDE QUANTITY [--reduce-only]
    
    EXAMPLES:
    python market_orders.py BTCUSDT BUY 0.01
    python market_orders.py ETHUSDT SELL 0.1
    python market_orders.py BTCUSDT SELL 0.01 --reduce-only
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Place market orders on Binance Futures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Buy 0.01 BTC at market price:
    python market_orders.py BTCUSDT BUY 0.01
  
  Sell 0.1 ETH at market price:
    python market_orders.py ETHUSDT SELL 0.1
  
  Close position (reduce-only):
    python market_orders.py BTCUSDT SELL 0.01 --reduce-only
        """
    )
    
    parser.add_argument('symbol', type=str, help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('side', type=str, choices=['BUY', 'SELL', 'buy', 'sell'],
                       help='Order side (BUY or SELL)')
    parser.add_argument('quantity', type=float, help='Quantity to trade')
    parser.add_argument('--reduce-only', action='store_true',
                       help='Only reduce existing position')
    
    args = parser.parse_args()
    
    # Place the order
    print(f"\n🤖 Binance Futures Market Order Bot")
    print(f"{'='*60}\n")
    
    result = place_market_order(
        symbol=args.symbol.upper(),
        side=args.side.upper(),
        quantity=args.quantity,
        reduce_only=args.reduce_only
    )
    
    if result:
        print("\n✅ Order placed successfully!")
        print(f"Check bot.log for detailed information.")
    else:
        print("\n❌ Order failed!")
        print(f"Check bot.log for error details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
