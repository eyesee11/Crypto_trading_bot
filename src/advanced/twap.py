"""
TWAP STRATEGY (Time-Weighted Average Price) - Smart Order Execution
"""

import sys
import os
import time
import argparse
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from binance.exceptions import BinanceAPIException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..config import get_client, get_current_price
from ..validator import validate_order
from ..logger_config import setup_logger, log_order, log_error, log_success
from ..orders.market_orders import place_market_order

logger = setup_logger('TWAPStrategy')


def execute_twap_strategy(
    symbol: str,
    side: str,
    total_quantity: float,
    duration_minutes: int,
    num_intervals: int,
    order_type: str = "MARKET"
) -> Optional[List[Dict]]:
    """
    Execute TWAP (Time-Weighted Average Price) strategy.
    
    Splits a large order into smaller chunks executed over time.
    
    PARAMETERS:
    - symbol: Trading pair (e.g., "BTCUSDT")
    - side: "BUY" or "SELL"
    - total_quantity: Total amount to trade
    - duration_minutes: How long to spread orders over (in minutes)
    - num_intervals: Number of orders to split into
    - order_type: "MARKET" (default) or "LIMIT"
    
    EXAMPLE - Buy $10,000 BTC over 1 hour:
    ```python
    # Split into 10 orders over 60 minutes
    orders = execute_twap_strategy(
        "BTCUSDT", "BUY",
        total_quantity=0.333,      # ~$10k worth
        duration_minutes=60,        # 1 hour
        num_intervals=10           # 10 orders
    )
    # Result: Buys 0.0333 BTC every 6 minutes
    ```
    
    EXAMPLE - Sell position gradually:
    ```python
    # Sell 1 BTC over 2 hours in 20 chunks
    orders = execute_twap_strategy(
        "BTCUSDT", "SELL",
        total_quantity=1.0,
        duration_minutes=120,       # 2 hours
        num_intervals=20           # 20 orders
    )
    # Result: Sells 0.05 BTC every 6 minutes
    ```
    
    RETURNS:
    - List of executed orders if successful
    - None if failed
    """
    
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 STARTING TWAP STRATEGY")
        logger.info(f"{'='*60}")
        
        # Calculate parameters
        quantity_per_order = total_quantity / num_intervals
        interval_seconds = (duration_minutes * 60) / num_intervals
        
        logger.info(f"Symbol: {symbol}")
        logger.info(f"Side: {side}")
        logger.info(f"Total Quantity: {total_quantity}")
        logger.info(f"Duration: {duration_minutes} minutes")
        logger.info(f"Number of Orders: {num_intervals}")
        logger.info(f"\n📐 CALCULATED:")
        logger.info(f"Quantity per order: {quantity_per_order:.8f}")
        logger.info(f"Interval: {interval_seconds:.1f} seconds ({interval_seconds/60:.2f} minutes)")
        
        # Validate one chunk
        is_valid, message, validated_data = validate_order(
            symbol, side, quantity_per_order, None, order_type
        )
        
        if not is_valid:
            logger.error(f"❌ Validation failed: {message}")
            return None
        
        symbol = validated_data['symbol']
        side = validated_data['side']
        
        # Show current price
        current_price = get_current_price(symbol)
        if current_price:
            total_value = total_quantity * current_price
            value_per_order = quantity_per_order * current_price
            logger.info(f"\n💵 Current price: ${current_price:,.2f}")
            logger.info(f"💰 Total value: ${total_value:,.2f}")
            logger.info(f"💳 Value per order: ${value_per_order:,.2f}")
        
        # Confirm execution
        logger.info(f"\n{'='*60}")
        logger.info(f"⚠️  READY TO EXECUTE TWAP STRATEGY")
        logger.info(f"{'='*60}")
        logger.info(f"This will place {num_intervals} orders over {duration_minutes} minutes")
        logger.info(f"Starting in 5 seconds... (Ctrl+C to cancel)")
        logger.info(f"{'='*60}\n")
        
        time.sleep(5)
        
        # Execute orders
        executed_orders = []
        start_time = datetime.now()
        
        for i in range(num_intervals):
            current_interval = i + 1
            logger.info(f"\n{'='*60}")
            logger.info(f"📝 INTERVAL {current_interval}/{num_intervals}")
            logger.info(f"{'='*60}")
            
            # Place order
            if order_type == "MARKET":
                result = place_market_order(symbol, side, quantity_per_order)
            else:
                logger.error(f"❌ Only MARKET orders supported currently")
                break
            
            if result:
                executed_orders.append(result)
                order_id = result.get('orderId')
                fill_price = float(result.get('avgPrice', 0))
                
                log_success(logger, f"TWAP order {current_interval}/{num_intervals} executed",
                           order_id=order_id,
                           quantity=quantity_per_order,
                           price=f"${fill_price:,.2f}" if fill_price else "N/A")
                
                # Calculate progress
                completed_qty = quantity_per_order * current_interval
                remaining_qty = total_quantity - completed_qty
                progress_pct = (current_interval / num_intervals) * 100
                
                logger.info(f"✅ Completed: {completed_qty:.8f} ({progress_pct:.1f}%)")
                logger.info(f"⏳ Remaining: {remaining_qty:.8f}")
                
            else:
                logger.error(f"❌ Failed to execute interval {current_interval}")
            
            # Wait for next interval (unless it's the last one)
            if current_interval < num_intervals:
                next_order_time = start_time + timedelta(seconds=interval_seconds * current_interval)
                wait_time = (next_order_time - datetime.now()).total_seconds()
                
                if wait_time > 0:
                    logger.info(f"⏰ Next order in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ TWAP STRATEGY COMPLETED")
        logger.info(f"{'='*60}")
        logger.info(f"Total orders executed: {len(executed_orders)}/{num_intervals}")
        
        if executed_orders:
            # Calculate average price
            total_qty = 0
            total_cost = 0
            
            for order in executed_orders:
                qty = float(order.get('executedQty', 0))
                avg_price = float(order.get('avgPrice', 0))
                total_qty += qty
                total_cost += qty * avg_price
            
            if total_qty > 0:
                average_price = total_cost / total_qty
                logger.info(f"📊 Average execution price: ${average_price:,.2f}")
                logger.info(f"📦 Total quantity: {total_qty:.8f}")
                logger.info(f"💰 Total cost/revenue: ${total_cost:,.2f}")
                
                print(f"\n✅ TWAP Strategy Completed!")
                print(f"📊 Average Price: ${average_price:,.2f}")
                print(f"📦 Total Executed: {total_qty:.8f} {symbol}")
                print(f"💰 Total Value: ${total_cost:,.2f}")
        
        logger.info(f"{'='*60}\n")
        
        return executed_orders
        
    except KeyboardInterrupt:
        logger.info(f"\n⚠️  TWAP strategy stopped by user")
        logger.info(f"✅ Orders executed so far: {len(executed_orders)}")
        return executed_orders
        
    except BinanceAPIException as e:
        log_error(logger, f"Failed to execute TWAP: BinanceAPIException: {e}", e)
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ BINANCE API ERROR")
        logger.error(f"{'='*60}")
        logger.error(f"Error: {e}")
        logger.error(f"Orders executed before error: {len(executed_orders)}")
        logger.error(f"{'='*60}\n")
        return None
        
    except Exception as e:
        log_error(logger, f"Unexpected error in TWAP: {type(e).__name__}: {e}", e)
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ UNEXPECTED ERROR")
        logger.error(f"{'='*60}")
        logger.error(f"Error: {e}")
        logger.error(f"Orders executed before error: {len(executed_orders)}")
        logger.error(f"{'='*60}\n")
        return None


def main():
    """CLI interface for TWAP strategy"""
    parser = argparse.ArgumentParser(
        description='Execute TWAP (Time-Weighted Average Price) strategy',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Buy 0.5 BTC over 1 hour in 10 orders
  python -m src.advanced.twap BTCUSDT BUY 0.5 --duration 60 --intervals 10
  
  # Sell 1.0 BTC over 2 hours in 20 orders
  python -m src.advanced.twap BTCUSDT SELL 1.0 --duration 120 --intervals 20
        """
    )
    
    parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('side', choices=['BUY', 'SELL', 'buy', 'sell'], help='Order side')
    parser.add_argument('quantity', type=float, help='Total quantity to trade')
    parser.add_argument('--duration', type=int, required=True, help='Duration in minutes')
    parser.add_argument('--intervals', type=int, required=True, help='Number of orders')
    parser.add_argument('--type', choices=['MARKET', 'LIMIT'], default='MARKET', 
                       help='Order type (default: MARKET)')
    
    args = parser.parse_args()
    
    result = execute_twap_strategy(
        args.symbol.upper(),
        args.side.upper(),
        args.quantity,
        args.duration,
        args.intervals,
        args.type
    )
    
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
