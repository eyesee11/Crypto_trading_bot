"""
📐 GRID TRADING STRATEGY - Automated Buy Low, Sell High

GRID TRADING MATH:

Example Setup:
- Range: $100k - $120k ($20k range)
- Grids: 5 levels (4 gaps between)
- Quantity: 0.01 BTC per level
- Current price: $110k (middle)

Calculations:
- Grid spacing = ($120k - $100k) / 4 = $5,000
- Levels: $100k, $105k, $110k, $115k, $120k
- BUY orders: 2 (at $100k and $105k) = 0.02 BTC total
- SELL orders: 2 (at $115k and $120k) = 0.02 BTC total
- Capital needed: 0.02 BTC + (0.02 × $110k in USDT) = ~$2,200

Profit per cycle:
- Buy at $105k, Sell at $115k = $10k difference
- Profit: 0.01 BTC × $10k = $100
- If price oscillates 10 times = $1,000 profit!

"""

import sys
import os
import argparse
from typing import List, Dict, Optional, Tuple
from binance.exceptions import BinanceAPIException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..config import get_client, get_current_price
from ..validator import validate_symbol, validate_quantity
from ..logger_config import setup_logger, log_order, log_error, log_success
from ..orders.limit_orders import place_limit_order, get_open_orders, cancel_order

logger = setup_logger('GridTrading')


def calculate_grid_levels(
    lower_price: float,
    upper_price: float,
    num_grids: int
) -> List[float]:
    """
    Calculate price levels for grid trading.
    
    ANALOGY: Like dividing a ladder into equal steps.
    
    PARAMETERS:
    - lower_price: Bottom of the range
    - upper_price: Top of the range
    - num_grids: Number of grid levels
    
    RETURNS:
    - List of price levels
    
    EXAMPLE:
    ```python
    levels = calculate_grid_levels(100000, 120000, 5)
    # Returns: [100000, 105000, 110000, 115000, 120000]
    ```
    """
    if num_grids < 2:
        raise ValueError("Need at least 2 grid levels")
    
    if lower_price >= upper_price:
        raise ValueError("Lower price must be less than upper price")
    
    # Calculate spacing between levels
    grid_spacing = (upper_price - lower_price) / (num_grids - 1)
    
    # Generate levels
    levels = []
    for i in range(num_grids):
        level = lower_price + (grid_spacing * i)
        levels.append(level)
    
    return levels


def setup_grid_trading(
    symbol: str,
    lower_price: float,
    upper_price: float,
    num_grids: int,
    quantity_per_grid: float,
    current_price: Optional[float] = None
) -> Optional[Dict]:
    """
    Set up a grid trading strategy.
    
    Places BUY orders below current price and SELL orders above current price
    at evenly spaced grid levels.
    
    PARAMETERS:
    - symbol: Trading pair (e.g., "BTCUSDT")
    - lower_price: Lower bound of grid range
    - upper_price: Upper bound of grid range
    - num_grids: Number of grid levels
    - quantity_per_grid: Quantity for each grid order
    - current_price: Current market price (auto-fetched if None)
    
    EXAMPLE - Range-Bound Trading:
    ```python
    # BTC bouncing between $100k - $120k
    result = setup_grid_trading(
        "BTCUSDT",
        lower_price=100000,
        upper_price=120000,
        num_grids=5,
        quantity_per_grid=0.01
    )
    # Places buy orders at $100k, $105k
    # Places sell orders at $115k, $120k
    # (Assuming current price is $110k)
    ```
    
    RETURNS:
    - Dictionary with buy_orders and sell_orders lists
    - None if failed
    """
    
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"📐 SETTING UP GRID TRADING STRATEGY")
        logger.info(f"{'='*60}")
        
        # Validate symbol
        is_valid, message = validate_symbol(symbol)
        if not is_valid:
            logger.error(f"❌ Invalid symbol: {message}")
            return None
        
        symbol = symbol.upper()
        
        # Get current price if not provided
        if current_price is None:
            current_price = get_current_price(symbol)
            if not current_price:
                logger.error(f"❌ Could not fetch current price for {symbol}")
                return None
        
        # Validate price range
        if current_price < lower_price or current_price > upper_price:
            logger.warning(f"⚠️  Current price ${current_price:,.2f} is outside grid range!")
            logger.warning(f"   Grid: ${lower_price:,.2f} - ${upper_price:,.2f}")
            logger.warning(f"   Consider adjusting range to include current price")
        
        # Calculate grid levels
        logger.info(f"\n📊 GRID PARAMETERS:")
        logger.info(f"Symbol: {symbol}")
        logger.info(f"Range: ${lower_price:,.2f} - ${upper_price:,.2f}")
        logger.info(f"Number of grids: {num_grids}")
        logger.info(f"Quantity per grid: {quantity_per_grid}")
        logger.info(f"Current price: ${current_price:,.2f}")
        
        levels = calculate_grid_levels(lower_price, upper_price, num_grids)
        
        logger.info(f"\n📐 CALCULATED GRID LEVELS:")
        for i, level in enumerate(levels, 1):
            position = "BELOW" if level < current_price else "ABOVE" if level > current_price else "CURRENT"
            logger.info(f"  Level {i}: ${level:,.2f} ({position})")
        
        # Separate buy and sell levels
        buy_levels = [level for level in levels if level < current_price]
        sell_levels = [level for level in levels if level > current_price]
        
        logger.info(f"\n📝 ORDER PLAN:")
        logger.info(f"BUY orders: {len(buy_levels)} levels")
        logger.info(f"SELL orders: {len(sell_levels)} levels")
        
        # Calculate capital required
        buy_capital = sum(quantity_per_grid * level for level in buy_levels)
        sell_capital = quantity_per_grid * len(sell_levels)  # BTC needed
        
        logger.info(f"\n💰 CAPITAL REQUIRED:")
        logger.info(f"For BUY orders: ${buy_capital:,.2f} USDT")
        logger.info(f"For SELL orders: {sell_capital:.8f} BTC")
        
        # Confirm
        logger.info(f"\n{'='*60}")
        logger.info(f"⚠️  READY TO PLACE GRID ORDERS")
        logger.info(f"{'='*60}")
        logger.info(f"This will place {len(buy_levels) + len(sell_levels)} orders")
        logger.info(f"Continue? (Will start in 3 seconds...)")
        logger.info(f"{'='*60}\n")
        
        import time
        time.sleep(3)
        
        # Place orders
        buy_orders = []
        sell_orders = []
        
        # Place BUY orders
        if buy_levels:
            logger.info(f"\n{'='*60}")
            logger.info(f"📝 PLACING BUY ORDERS")
            logger.info(f"{'='*60}")
            
            for i, price in enumerate(buy_levels, 1):
                logger.info(f"\nBUY Order {i}/{len(buy_levels)} @ ${price:,.2f}")
                
                result = place_limit_order(
                    symbol=symbol,
                    side="BUY",
                    quantity=quantity_per_grid,
                    price=price,
                    time_in_force="GTC",
                    post_only=True  # Maker orders to save on fees
                )
                
                if result:
                    buy_orders.append(result)
                    logger.info(f"✅ BUY order placed: ID {result.get('orderId')}")
                else:
                    logger.error(f"❌ Failed to place BUY order @ ${price:,.2f}")
        
        # Place SELL orders
        if sell_levels:
            logger.info(f"\n{'='*60}")
            logger.info(f"📝 PLACING SELL ORDERS")
            logger.info(f"{'='*60}")
            
            for i, price in enumerate(sell_levels, 1):
                logger.info(f"\nSELL Order {i}/{len(sell_levels)} @ ${price:,.2f}")
                
                result = place_limit_order(
                    symbol=symbol,
                    side="SELL",
                    quantity=quantity_per_grid,
                    price=price,
                    time_in_force="GTC",
                    post_only=True  # Maker orders to save on fees
                )
                
                if result:
                    sell_orders.append(result)
                    logger.info(f"✅ SELL order placed: ID {result.get('orderId')}")
                else:
                    logger.error(f"❌ Failed to place SELL order @ ${price:,.2f}")
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ GRID TRADING SETUP COMPLETE!")
        logger.info(f"{'='*60}")
        logger.info(f"BUY orders placed: {len(buy_orders)}")
        logger.info(f"SELL orders placed: {len(sell_orders)}")
        logger.info(f"Total orders: {len(buy_orders) + len(sell_orders)}")
        logger.info(f"\n💡 MONITORING:")
        logger.info(f"   Check orders: python main.py orders {symbol}")
        logger.info(f"   Cancel all: Use cancel command for each order ID")
        logger.info(f"{'='*60}\n")
        
        print(f"\n✅ Grid Trading Activated!")
        print(f"📊 {len(buy_orders)} BUY orders + {len(sell_orders)} SELL orders placed")
        print(f"💡 Monitor: python main.py orders {symbol}")
        
        return {
            'symbol': symbol,
            'buy_orders': buy_orders,
            'sell_orders': sell_orders,
            'grid_levels': levels,
            'current_price': current_price
        }
        
    except BinanceAPIException as e:
        log_error(logger, f"Failed to setup grid: BinanceAPIException: {e}", e)
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ BINANCE API ERROR")
        logger.error(f"{'='*60}")
        logger.error(f"Error: {e}")
        logger.error(f"{'='*60}\n")
        return None
        
    except Exception as e:
        log_error(logger, f"Unexpected error setting up grid: {type(e).__name__}: {e}", e)
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ UNEXPECTED ERROR")
        logger.error(f"{'='*60}")
        logger.error(f"Error: {e}")
        logger.error(f"{'='*60}\n")
        return None


def cancel_all_grid_orders(symbol: str) -> bool:
    """
    Cancel all open orders for a symbol (useful for stopping grid trading).
    
    ANALOGY: Like pulling up the fishing net - removes all pending orders.
    
    PARAMETERS:
    - symbol: Trading pair
    
    RETURNS:
    - True if all orders canceled successfully
    - False if any failures
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"🛑 CANCELING ALL GRID ORDERS FOR {symbol}")
    logger.info(f"{'='*60}")
    
    orders = get_open_orders(symbol)
    
    if not orders or len(orders) == 0:
        logger.info(f"No open orders to cancel")
        return True
    
    logger.info(f"Found {len(orders)} open orders")
    
    success_count = 0
    fail_count = 0
    
    for order in orders:
        order_id = order['orderId']
        side = order['side']
        price = float(order['price']) if order.get('price') != '0' else 0
        
        logger.info(f"\nCanceling {side} order @ ${price:,.2f} (ID: {order_id})")
        
        if cancel_order(symbol, order_id):
            success_count += 1
            logger.info(f"✅ Canceled")
        else:
            fail_count += 1
            logger.error(f"❌ Failed to cancel")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"CANCELLATION SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"✅ Successful: {success_count}")
    logger.info(f"❌ Failed: {fail_count}")
    logger.info(f"{'='*60}\n")
    
    return fail_count == 0


def main():
    """CLI interface for grid trading"""
    parser = argparse.ArgumentParser(
        description='Grid Trading Strategy',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Set up grid trading for BTC between $100k-$120k
  python -m src.advanced.grid_trading BTCUSDT 100000 120000 --grids 5 --quantity 0.01
  
  # Cancel all grid orders
  python -m src.advanced.grid_trading BTCUSDT --cancel
        """
    )
    
    parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('lower_price', nargs='?', type=float, help='Lower bound of grid range')
    parser.add_argument('upper_price', nargs='?', type=float, help='Upper bound of grid range')
    parser.add_argument('--grids', type=int, help='Number of grid levels')
    parser.add_argument('--quantity', type=float, help='Quantity per grid level')
    parser.add_argument('--cancel', action='store_true', help='Cancel all orders for symbol')
    
    args = parser.parse_args()
    
    if args.cancel:
        result = cancel_all_grid_orders(args.symbol.upper())
        sys.exit(0 if result else 1)
    
    if not all([args.lower_price, args.upper_price, args.grids, args.quantity]):
        parser.error("--grids and --quantity are required unless using --cancel")
    
    result = setup_grid_trading(
        args.symbol.upper(),
        args.lower_price,
        args.upper_price,
        args.grids,
        args.quantity
    )
    
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
