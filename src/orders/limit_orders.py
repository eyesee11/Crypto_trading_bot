"""
🎯 LIMIT ORDERS - The "Price Alert" Order

REAL-LIFE ANALOGY:
Think of limit orders like setting price alerts on Amazon or eBay:
- "Only buy if price drops to $800" (BUY limit below market)
- "Only sell if price rises to $1200" (SELL limit above market)
- Order sits and waits until your target price is hit
- Might wait seconds, hours, or never fill

EXAMPLE SCENARIOS:

1. Bargain Hunter:
   - BTC currently $30,000
   - You think it'll dip to $28,000
   - Set BUY limit @ $28,000
   - Go to sleep, order fills automatically if price drops
   - Saved $2,000 per BTC compared to market buy!

2. Profit Taker:
   - You bought BTC @ $28,000
   - Want to sell for profit when it hits $32,000
   - Set SELL limit @ $32,000
   - Relax, order fills when target reached
   - Locked in $4,000 profit per BTC!

3. Dollar-Cost Averaging:
   - Place multiple buy limits at different prices
   - $29,000, $28,000, $27,000
   - As price drops, orders fill automatically
   - Average down your entry price

WHY USE LIMIT ORDERS:
✅ Control exact price (no surprises)
✅ Better fills (might get better price than market)
✅ Lower fees (maker fees, usually 0.00% - 0.02%)
✅ Set and forget (don't need to watch charts)
✅ No slippage (get your price or nothing)

WHEN NOT TO USE:
❌ Urgent - might not fill in time
❌ Fast-moving market - price might run away
❌ Thin liquidity - order might never fill
❌ Wrong price - if set too far, won't execute

KEY CONCEPTS:

1. MAKER vs TAKER:
   - MAKER: Your order sits in order book (limit orders)
             ANALOGY: Like putting up a "For Sale" sign
   - TAKER: Your order takes from order book (market orders)
             ANALOGY: Like accepting someone's "For Sale" price
   - Maker fees are lower (exchanges reward providing liquidity)

2. TIME IN FORCE (TIF):
   - GTC (Good-Til-Canceled): Stays until filled or you cancel
     ANALOGY: Like leaving a classified ad running indefinitely
   
   - IOC (Immediate-Or-Cancel): Fill what you can now, cancel rest
     ANALOGY: Like "Flash Sale - only available right now"
   
   - FOK (Fill-Or-Kill): Fill entire order now or cancel completely
     ANALOGY: Like "All or nothing" deal

3. POST_ONLY:
   - Ensures order goes in book as maker (doesn't take)
   - If would match immediately, order is rejected
   - Guarantees maker fees
   - ANALOGY: Like "I'll only sell if I can set my own price"

HOW LIMIT ORDERS WORK:

BUY LIMIT @ $29,000 (Market is $30,000):
1. Your order enters the order book
2. Order book now shows:
   BUY  | SELL
   $29,500 | $30,100
   $29,200 | $30,200
   $29,000 ← YOU | $30,300
3. You wait...
4. Price starts dropping: $30,000... $29,800... $29,500...
5. Price hits $29,000 → YOUR ORDER FILLS! ✅
6. You bought BTC $1,000 cheaper than if you used market order!

SELL LIMIT @ $31,000 (Market is $30,000):
1. Your order enters the order book
2. Order book now shows:
   BUY  | SELL
   $29,900 | $30,100
   $29,800 | $30,500
   $29,700 | $31,000 ← YOU
3. You wait...
4. Price starts rising: $30,200... $30,600... $30,900...
5. Price hits $31,000 → YOUR ORDER FILLS! ✅
6. You sold BTC $1,000 higher than if you used market order!

TECHNICAL DETAILS:
- Order Type: LIMIT
- Time In Force: GTC (default), IOC, FOK, or POST_ONLY
- Fees: Usually 0.00% - 0.02% (maker fees)
- Execution: Not guaranteed, depends on price reaching your level
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
logger = setup_logger('LimitOrders')


def place_limit_order(
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC",
    post_only: bool = False,
    reduce_only: bool = False
) -> Optional[Dict]:
    """
    Place a limit order on Binance Futures.
    
    PARAMETERS EXPLAINED:
    
    - symbol: Trading pair (e.g., "BTCUSDT", "ETHUSDT")
      ANALOGY: Which product you're buying/selling
      
    - side: "BUY" or "SELL"
      ANALOGY: Are you buying or selling?
      
    - quantity: Amount to trade (e.g., 0.01 BTC)
      ANALOGY: How many units you want
      
    - price: Target price for execution
      ANALOGY: "Only execute at this price"
      EXAMPLE: BUY @ $28,000 means "only buy if price drops to $28,000 or less"
               SELL @ $32,000 means "only sell if price rises to $32,000 or more"
      
    - time_in_force: How long order stays active
      Options:
        • "GTC" (Good-Til-Canceled): Stays until filled or you cancel [DEFAULT]
          ANALOGY: Classified ad that runs indefinitely
          
        • "IOC" (Immediate-Or-Cancel): Fill what you can now, cancel rest
          ANALOGY: Flash sale - buy what's available now
          
        • "FOK" (Fill-Or-Kill): Fill entire order immediately or cancel
          ANALOGY: All-or-nothing deal
      
    - post_only: If True, order must be maker (won't execute immediately)
      ANALOGY: "I'll only sell if I can set my own price, not accept others' prices"
      Use case: Want to guarantee maker fees (lower/zero fees)
      
    - reduce_only: If True, only reduces existing position
      ANALOGY: "Close position only" - prevents opening new positions
    
    STEP-BY-STEP PROCESS:
    
    Step 1: VALIDATE inputs
           - All standard checks plus price validation
           - Check price isn't ridiculously far from market
    
    Step 2: CHECK CURRENT PRICE
           - Show user how far their limit is from market
           - Warn if order unlikely to fill
    
    Step 3: SEND ORDER
           - Create limit order parameters
           - Submit to Binance
    
    Step 4: HANDLE RESPONSE
           - Log order ID and details
           - Explain next steps (order is now waiting)
    
    RETURNS:
    - Dictionary with order details if successful
    - None if order failed
    
    EXAMPLE SUCCESSFUL RESPONSE:
    {
        'orderId': 12345,
        'symbol': 'BTCUSDT',
        'status': 'NEW',  # Not filled yet, waiting in order book
        'side': 'BUY',
        'type': 'LIMIT',
        'price': '28000.00',
        'origQty': '0.01',
        'timeInForce': 'GTC'
    }
    
    Note: Status is 'NEW' or 'PARTIALLY_FILLED' until price is reached
    
    REAL-WORLD EXAMPLES:
    
    Example 1: Buy the Dip
    ```python
    # BTC currently $30,000, you want to buy if it drops to $28,000
    order = place_limit_order("BTCUSDT", "BUY", 0.01, 28000)
    
    if order:
        print(f"✅ Buy order placed @ $28,000")
        print(f"🆔 Order ID: {order['orderId']}")
        print(f"⏳ Order is now waiting in the order book")
        print(f"📊 Will fill if BTC drops to $28,000 or below")
    ```
    
    Example 2: Take Profit
    ```python
    # You bought BTC @ $28,000, now want to sell @ $32,000 for profit
    order = place_limit_order("BTCUSDT", "SELL", 0.01, 32000)
    
    if order:
        print(f"✅ Sell order placed @ $32,000")
        print(f"💰 Will lock in $4,000 profit per BTC when filled")
    ```
    
    Example 3: Post-Only (Maker Fees)
    ```python
    # Want to buy but only as maker (for lower fees)
    order = place_limit_order(
        "BTCUSDT", "BUY", 0.01, 29900,
        post_only=True  # Ensures maker order
    )
    # If price is already at 29900, order will be rejected (to prevent taking)
    ```
    """
    
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"📝 PLACING LIMIT ORDER")
        logger.info(f"{'='*60}")
        
        # ============================================
        # STEP 1: VALIDATION
        # ============================================
        
        logger.info(f"🔍 Step 1: Validating order parameters...")
        
        is_valid, message, validated_data = validate_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            order_type="LIMIT"
        )
        
        if not is_valid:
            logger.error(f"❌ Validation failed: {message}")
            return None
        
        # Use validated values
        symbol = validated_data['symbol']
        side = validated_data['side']
        price = validated_data['price']
        
        logger.info(f"✅ Validation passed!")
        
        # ============================================
        # STEP 2: ANALYZE PRICE DISTANCE
        # ============================================
        # Show user how their limit compares to market
        
        logger.info(f"💵 Step 2: Analyzing price levels...")
        
        current_price = get_current_price(symbol)
        if current_price:
            price_diff = price - current_price
            price_diff_pct = (price_diff / current_price) * 100
            
            logger.info(f"   Current market price: ${current_price:,.2f}")
            logger.info(f"   Your limit price: ${price:,.2f}")
            logger.info(f"   Difference: ${price_diff:,.2f} ({price_diff_pct:+.2f}%)")
            
            # Provide helpful analysis
            if side == "BUY":
                if price >= current_price:
                    logger.warning(f"⚠️  BUY limit @ ${price:,.2f} is ABOVE market ${current_price:,.2f}")
                    logger.warning(f"⚠️  Order will likely fill immediately (similar to market order)")
                    logger.warning(f"💡 Consider lower price for true limit order")
                else:
                    logger.info(f"✅ BUY limit @ ${price:,.2f} is below market (good!)")
                    logger.info(f"📊 Order will fill if price drops {abs(price_diff_pct):.2f}%")
            
            elif side == "SELL":
                if price <= current_price:
                    logger.warning(f"⚠️  SELL limit @ ${price:,.2f} is BELOW market ${current_price:,.2f}")
                    logger.warning(f"⚠️  Order will likely fill immediately (similar to market order)")
                    logger.warning(f"💡 Consider higher price for true limit order")
                else:
                    logger.info(f"✅ SELL limit @ ${price:,.2f} is above market (good!)")
                    logger.info(f"📊 Order will fill if price rises {abs(price_diff_pct):.2f}%")
        
        # ============================================
        # STEP 3: CREATE AND SEND ORDER
        # ============================================
        
        logger.info(f"📤 Step 3: Sending limit order to Binance...")
        
        # Get Binance client
        client = get_client()
        
        # Build order parameters
        order_params = {
            'symbol': symbol,
            'side': side,
            'type': 'LIMIT',
            'quantity': quantity,
            'price': f"{price:.10f}",  # Format price with sufficient decimals
            'timeInForce': time_in_force.upper()
        }
        
        # Add optional parameters
        if post_only:
            order_params['timeInForce'] = 'GTX'  # Good-Til-Crossing (post-only)
            logger.info("   📌 Post-only mode: Order must be maker")
        
        if reduce_only:
            order_params['reduceOnly'] = True
            logger.info("   📌 Reduce-only mode: Will only close existing position")
        
        logger.info(f"   Order parameters: {order_params}")
        
        # Log the order attempt
        log_order(
            logger,
            "LIMIT",
            symbol,
            side,
            quantity,
            price=price,
            time_in_force=time_in_force,
            post_only=post_only,
            reduce_only=reduce_only
        )
        
        # SEND ORDER TO BINANCE
        response = client.futures_create_order(**order_params)
        
        # ============================================
        # STEP 4: PROCESS RESPONSE
        # ============================================
        
        logger.info(f"📨 Step 4: Processing response...")
        
        # Extract key information
        order_id = response.get('orderId')
        status = response.get('status')
        executed_qty = float(response.get('executedQty', 0))
        orig_qty = float(response.get('origQty', quantity))
        
        # Log success
        log_success(
            logger,
            f"Limit order placed",
            order_id=order_id,
            status=status,
            symbol=symbol,
            side=side,
            quantity=orig_qty,
            price=f"${price:,.2f}"
        )
        
        # Provide user-friendly summary
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ LIMIT ORDER PLACED!")
        logger.info(f"{'='*60}")
        logger.info(f"🆔 Order ID: {order_id}")
        logger.info(f"📊 Symbol: {symbol}")
        logger.info(f"↗️  Side: {side}")
        logger.info(f"📦 Quantity: {orig_qty}")
        logger.info(f"💰 Limit Price: ${price:,.2f}")
        logger.info(f"📈 Status: {status}")
        
        # Explain what happens next based on status
        if status == "NEW":
            logger.info(f"\n📋 Order Status: NEW (Waiting in order book)")
            logger.info(f"⏳ Order will fill when market price reaches ${price:,.2f}")
            logger.info(f"💡 You can cancel anytime if unfilled")
            logger.info(f"💡 Check status with: get_order_status('{symbol}', {order_id})")
        elif status == "FILLED":
            logger.info(f"\n✅ Order Status: FILLED (Executed immediately!)")
            logger.info(f"💵 Executed quantity: {executed_qty}")
            logger.info(f"💡 Price was already at your limit level")
        elif status == "PARTIALLY_FILLED":
            logger.info(f"\n⏳ Order Status: PARTIALLY FILLED")
            logger.info(f"📊 Executed: {executed_qty} / {orig_qty}")
            logger.info(f"⏳ Waiting for rest to fill at ${price:,.2f}")
        
        logger.info(f"{'='*60}\n")
        
        return response
        
    except BinanceAPIException as e:
        error_msg = f"Binance API Error: {e.message}"
        log_error(logger, error_msg, e)
        
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ ORDER FAILED")
        logger.error(f"{'='*60}")
        logger.error(f"Error Code: {e.code}")
        logger.error(f"Error Message: {e.message}")
        logger.error(f"{'='*60}\n")
        
        # Common error codes for limit orders
        if e.code == -2010:
            logger.error("💡 Hint: Insufficient balance or margin")
        elif e.code == -1111:
            logger.error("💡 Hint: Precision error - check price/quantity decimals")
        elif e.code == -4164:
            logger.error("💡 Hint: Post-only order would match immediately (use different price)")
        elif e.code == -1021:
            logger.error("💡 Hint: Timestamp error - check system clock")
        
        return None
        
    except Exception as e:
        error_msg = "Unexpected error placing limit order"
        log_error(logger, error_msg, e)
        
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ UNEXPECTED ERROR")
        logger.error(f"{'='*60}")
        logger.error(f"Error: {str(e)}")
        logger.error(f"{'='*60}\n")
        
        return None


def cancel_order(symbol: str, order_id: int) -> bool:
    """
    Cancel an open limit order.
    
    ANALOGY: Like canceling a classified ad or eBay listing:
    - "I don't want to sell anymore"
    - "Price moved, I want different level"
    - "Changed my mind"
    
    WHY CANCEL:
    - Price ran away (won't fill at current level)
    - Want to set different price
    - Changed trading strategy
    - Need capital for different trade
    
    PARAMETERS:
    - symbol: Trading pair (e.g., "BTCUSDT")
    - order_id: The order ID to cancel
    
    RETURNS:
    - True if successfully canceled
    - False if error
    
    EXAMPLE:
    ```python
    # Place order
    order = place_limit_order("BTCUSDT", "BUY", 0.01, 28000)
    
    # Later... decide to cancel
    if cancel_order("BTCUSDT", order['orderId']):
        print("✅ Order canceled")
        
        # Place new order at different price
        new_order = place_limit_order("BTCUSDT", "BUY", 0.01, 27000)
    ```
    """
    try:
        logger.info(f"🔄 Canceling order {order_id} for {symbol}...")
        
        client = get_client()
        response = client.futures_cancel_order(symbol=symbol, orderId=order_id)
        
        logger.info(f"✅ Order {order_id} canceled successfully")
        logger.info(f"   Status: {response.get('status')}")
        
        return True
        
    except BinanceAPIException as e:
        if e.code == -2011:
            logger.error(f"❌ Order {order_id} not found (already filled or canceled?)")
        else:
            log_error(logger, f"Failed to cancel order {order_id}", e)
        return False
        
    except Exception as e:
        log_error(logger, f"Unexpected error canceling order {order_id}", e)
        return False


def get_open_orders(symbol: Optional[str] = None) -> Optional[list]:
    """
    Get all open limit orders.
    
    ANALOGY: Like checking all your active classified ads:
    - See what you're selling
    - Check prices you've set
    - Decide if any need updating
    
    USEFUL FOR:
    - Reviewing current orders
    - Finding orders to cancel
    - Monitoring order book position
    
    PARAMETERS:
    - symbol: (Optional) Filter by symbol, or None for all symbols
    
    RETURNS:
    - List of open orders
    - None if error
    
    EXAMPLE:
    ```python
    # Get all open BTC orders
    orders = get_open_orders("BTCUSDT")
    
    if orders:
        print(f"You have {len(orders)} open BTC orders:")
        for order in orders:
            print(f"  {order['side']} {order['origQty']} @ ${order['price']}")
            print(f"  Order ID: {order['orderId']}")
    ```
    """
    try:
        client = get_client()
        
        if symbol:
            orders = client.futures_get_open_orders(symbol=symbol)
            logger.info(f"📋 Found {len(orders)} open orders for {symbol}")
        else:
            orders = client.futures_get_open_orders()
            logger.info(f"📋 Found {len(orders)} open orders across all symbols")
        
        return orders
        
    except Exception as e:
        log_error(logger, "Failed to get open orders", e)
        return None


# ============================================
# COMMAND-LINE INTERFACE
# ============================================

def main():
    """
    Command-line interface for limit orders.
    
    USAGE:
    python limit_orders.py SYMBOL SIDE QUANTITY PRICE [OPTIONS]
    
    EXAMPLES:
    python limit_orders.py BTCUSDT BUY 0.01 28000
    python limit_orders.py ETHUSDT SELL 0.1 2000 --time-in-force IOC
    python limit_orders.py BTCUSDT BUY 0.01 29900 --post-only
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Place limit orders on Binance Futures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Buy 0.01 BTC if price drops to $28,000:
    python limit_orders.py BTCUSDT BUY 0.01 28000
  
  Sell 0.1 ETH if price rises to $2,000:
    python limit_orders.py ETHUSDT SELL 0.1 2000
  
  Maker-only order (post-only, lower fees):
    python limit_orders.py BTCUSDT BUY 0.01 29900 --post-only
  
  Fill-or-kill order (all or nothing):
    python limit_orders.py BTCUSDT BUY 0.01 29000 --time-in-force FOK
        """
    )
    
    parser.add_argument('symbol', type=str, help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('side', type=str, choices=['BUY', 'SELL', 'buy', 'sell'],
                       help='Order side (BUY or SELL)')
    parser.add_argument('quantity', type=float, help='Quantity to trade')
    parser.add_argument('price', type=float, help='Limit price')
    parser.add_argument('--time-in-force', type=str, default='GTC',
                       choices=['GTC', 'IOC', 'FOK'],
                       help='Time in force (default: GTC)')
    parser.add_argument('--post-only', action='store_true',
                       help='Post-only (maker) order')
    parser.add_argument('--reduce-only', action='store_true',
                       help='Only reduce existing position')
    
    args = parser.parse_args()
    
    # Place the order
    print(f"\n🤖 Binance Futures Limit Order Bot")
    print(f"{'='*60}\n")
    
    result = place_limit_order(
        symbol=args.symbol.upper(),
        side=args.side.upper(),
        quantity=args.quantity,
        price=args.price,
        time_in_force=args.time_in_force,
        post_only=args.post_only,
        reduce_only=args.reduce_only
    )
    
    if result:
        print("\n✅ Order placed successfully!")
        print(f"Order ID: {result['orderId']}")
        print(f"Status: {result['status']}")
        print(f"Check bot.log for detailed information.")
    else:
        print("\n❌ Order failed!")
        print(f"Check bot.log for error details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
