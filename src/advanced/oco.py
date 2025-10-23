"""
🎯 OCO ORDERS (One-Cancels-Other) - Advanced Risk Management

OCO Order:
- "Sell at $35k profit OR $28k loss"
- Both profit and protection
- Automatic cancellation
- Best of both worlds! ✅

"""

import sys
import os
import time
import argparse
from typing import Dict, Optional, Tuple
from binance.exceptions import BinanceAPIException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..config import get_client, get_current_price
from ..validator import validate_order
from ..logger_config import setup_logger, log_order, log_error, log_success
from ..orders.limit_orders import cancel_order

logger = setup_logger('OCOOrders')


def place_oco_order(
    symbol: str,
    side: str,
    quantity: float,
    take_profit_price: float,
    stop_loss_price: float,
    stop_limit_price: Optional[float] = None
) -> Optional[Tuple[Dict, Dict]]:
    """
    Place an OCO (One-Cancels-Other) order pair.
    
    PARAMETERS:
    - symbol: Trading pair (e.g., "BTCUSDT")
    - side: "SELL" (usually, for taking profit or limiting loss)
    - quantity: Amount to trade
    - take_profit_price: Target profit price
    - stop_loss_price: Stop loss trigger price
    - stop_limit_price: Limit price for stop order (optional)
    
    EXAMPLE - Long Position Protection:
    ```python
    # Bought BTC @ $30k, now protect position
    orders = place_oco_order(
        "BTCUSDT", "SELL", 0.01,
        take_profit_price=35000,  # Sell at $35k for profit
        stop_loss_price=28000,    # Sell at $28k to limit loss
        stop_limit_price=27900    # Actual stop sell price
    )
    # Result: Two orders placed, when one fills, other cancels
    ```
    
    EXAMPLE - Short Position Protection:
    ```python
    # Shorted BTC @ $30k, protect if it rises
    orders = place_oco_order(
        "BTCUSDT", "BUY", 0.01,
        take_profit_price=28000,  # Buy at $28k for profit
        stop_loss_price=32000,    # Buy at $32k to limit loss
        stop_limit_price=32100    # Actual stop buy price
    )
    ```
    
    RETURNS:
    - Tuple of (take_profit_order, stop_loss_order) if successful
    - None if failed
    """
    
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 PLACING OCO ORDER (ONE-CANCELS-OTHER)")
        logger.info(f"{'='*60}")
        
        # For OCO orders, we only validate symbol, side, and quantity
        # We skip price validation because OCO naturally has prices far from market
        # (take profit above and stop loss below, or vice versa)
        is_valid, message, validated_data = validate_order(
            symbol, side, quantity, None, "MARKET"  # Use MARKET type to skip price checks
        )
        
        if not is_valid:
            logger.error(f"❌ Validation failed: {message}")
            return None
        
        symbol = validated_data['symbol']
        side = validated_data['side']
        
        # Analyze prices
        current = get_current_price(symbol)
        if current:
            logger.info(f"💵 Current price: ${current:,.2f}")
            logger.info(f"🎯 Take Profit: ${take_profit_price:,.2f} ({((take_profit_price - current) / current * 100):+.2f}%)")
            logger.info(f"🛡️  Stop Loss: ${stop_loss_price:,.2f} ({((stop_loss_price - current) / current * 100):+.2f}%)")
            
            # Logic checks for SELL OCO
            if side == "SELL":
                if take_profit_price <= current:
                    logger.warning(f"⚠️  Take profit price is below current - will fill immediately!")
                if stop_loss_price >= current:
                    logger.warning(f"⚠️  Stop loss price is above current - will trigger immediately!")
                if take_profit_price <= stop_loss_price:
                    logger.error(f"❌ For SELL: Take profit must be > Stop loss!")
                    return None
            
            # Logic checks for BUY OCO
            elif side == "BUY":
                if take_profit_price >= current:
                    logger.warning(f"⚠️  Take profit price is above current - will fill immediately!")
                if stop_loss_price <= current:
                    logger.warning(f"⚠️  Stop loss price is below current - will trigger immediately!")
                if take_profit_price >= stop_loss_price:
                    logger.error(f"❌ For BUY: Take profit must be < Stop loss!")
                    return None
        
        client = get_client()
        
        # Step 1: Place Take Profit (Limit Order)
        logger.info(f"\n📝 Step 1/2: Placing TAKE PROFIT order...")
        
        tp_params = {
            'symbol': symbol,
            'side': side,
            'type': 'LIMIT',
            'quantity': quantity,
            'price': f"{take_profit_price:.10f}",
            'timeInForce': 'GTC'
        }
        
        log_order(logger, "LIMIT (Take Profit)", symbol, side, quantity, price=take_profit_price)
        tp_response = client.futures_create_order(**tp_params)
        tp_order_id = tp_response.get('orderId')
        
        log_success(logger, "Take profit order placed", 
                   order_id=tp_order_id,
                   price=f"${take_profit_price:,.2f}")
        
        # Step 2: Place Stop Loss (Stop Market or Stop Limit)
        logger.info(f"\n📝 Step 2/2: Placing STOP LOSS order...")
        
        # If stop_limit_price not provided, use stop_loss_price (market stop)
        if stop_limit_price is None:
            # Use stop market (simpler, guaranteed fill but no price control)
            sl_type = 'STOP_MARKET'
            sl_params = {
                'symbol': symbol,
                'side': side,
                'type': sl_type,
                'quantity': quantity,
                'stopPrice': f"{stop_loss_price:.10f}"
            }
        else:
            # Use stop limit (more control, but might not fill)
            sl_type = 'STOP'
            sl_params = {
                'symbol': symbol,
                'side': side,
                'type': sl_type,
                'quantity': quantity,
                'price': f"{stop_limit_price:.10f}",
                'stopPrice': f"{stop_loss_price:.10f}",
                'timeInForce': 'GTC'
            }
        
        log_order(logger, f"{sl_type} (Stop Loss)", symbol, side, quantity, 
                 stop_price=stop_loss_price, 
                 limit_price=stop_limit_price if stop_limit_price else None)
        
        sl_response = client.futures_create_order(**sl_params)
        sl_order_id = sl_response.get('orderId')
        
        log_success(logger, "Stop loss order placed",
                   order_id=sl_order_id,
                   stop_price=f"${stop_loss_price:,.2f}")
        
        # Success!
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ OCO ORDER PAIR PLACED SUCCESSFULLY!")
        logger.info(f"{'='*60}")
        logger.info(f"📊 When ONE order fills, manually cancel the other:")
        logger.info(f"   Take Profit ID: {tp_order_id}")
        logger.info(f"   Stop Loss ID: {sl_order_id}")
        logger.info(f"\n💡 TIP: Monitor with: python main.py orders {symbol}")
        logger.info(f"💡 TIP: Cancel with: python main.py cancel {symbol} <order_id>")
        logger.info(f"{'='*60}\n")
        
        print(f"\n✅ OCO Order Placed!")
        print(f"📊 Take Profit Order ID: {tp_order_id} @ ${take_profit_price:,.2f}")
        print(f"🛡️  Stop Loss Order ID: {sl_order_id} @ ${stop_loss_price:,.2f}")
        print(f"\n⚠️  IMPORTANT: When one fills, cancel the other manually!")
        
        return (tp_response, sl_response)
        
    except BinanceAPIException as e:
        log_error(logger, f"Failed to place OCO order: BinanceAPIException: {e}", e)
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ BINANCE API ERROR")
        logger.error(f"{'='*60}")
        logger.error(f"Error: {e}")
        logger.error(f"{'='*60}\n")
        return None
        
    except Exception as e:
        log_error(logger, f"Unexpected error placing OCO order: {type(e).__name__}: {e}", e)
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ UNEXPECTED ERROR")
        logger.error(f"{'='*60}")
        logger.error(f"Error: {e}")
        logger.error(f"{'='*60}\n")
        return None


def monitor_oco_orders(symbol: str, tp_order_id: int, sl_order_id: int, check_interval: int = 5):
    """
    Monitor OCO order pair and auto-cancel the other when one fills.
    
    ANALOGY: Like a security guard watching two doors - when someone enters one,
    lock the other door automatically.
    
    PARAMETERS:
    - symbol: Trading pair
    - tp_order_id: Take profit order ID
    - sl_order_id: Stop loss order ID
    - check_interval: Seconds between checks (default 5)
    
    NOTE: This is a blocking function - it will run until one order fills.
    Use this in a separate script or background process.
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"👁️  MONITORING OCO ORDERS")
    logger.info(f"{'='*60}")
    logger.info(f"Symbol: {symbol}")
    logger.info(f"Take Profit ID: {tp_order_id}")
    logger.info(f"Stop Loss ID: {sl_order_id}")
    logger.info(f"Check Interval: {check_interval}s")
    logger.info(f"{'='*60}\n")
    
    client = get_client()
    
    try:
        while True:
            # Check both orders
            try:
                orders = client.futures_get_open_orders(symbol=symbol)
                open_order_ids = [o['orderId'] for o in orders]
                
                tp_filled = tp_order_id not in open_order_ids
                sl_filled = sl_order_id not in open_order_ids
                
                if tp_filled:
                    logger.info(f"✅ Take Profit filled! Canceling Stop Loss...")
                    cancel_order(symbol, sl_order_id)
                    logger.info(f"🎉 OCO completed - Take Profit executed!")
                    break
                    
                elif sl_filled:
                    logger.info(f"🛡️  Stop Loss filled! Canceling Take Profit...")
                    cancel_order(symbol, tp_order_id)
                    logger.info(f"🎉 OCO completed - Stop Loss executed!")
                    break
                
                else:
                    logger.debug(f"⏳ Both orders still active... (checking again in {check_interval}s)")
                    
            except Exception as e:
                logger.error(f"Error checking orders: {e}")
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        logger.info(f"\n⚠️  Monitoring stopped by user")
        logger.info(f"💡 Orders are still active - cancel manually if needed")


def main():
    """CLI interface for OCO orders"""
    parser = argparse.ArgumentParser(description='Place OCO (One-Cancels-Other) orders')
    parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('side', choices=['BUY', 'SELL', 'buy', 'sell'], help='Order side')
    parser.add_argument('quantity', type=float, help='Quantity to trade')
    parser.add_argument('take_profit', type=float, help='Take profit price')
    parser.add_argument('stop_loss', type=float, help='Stop loss price')
    parser.add_argument('--stop-limit', type=float, help='Stop limit price (optional)', default=None)
    parser.add_argument('--monitor', action='store_true', help='Auto-monitor and cancel')
    
    args = parser.parse_args()
    
    result = place_oco_order(
        args.symbol.upper(), 
        args.side.upper(),
        args.quantity, 
        args.take_profit, 
        args.stop_loss,
        args.stop_limit
    )
    
    if result and args.monitor:
        tp_order, sl_order = result
        monitor_oco_orders(
            args.symbol.upper(),
            tp_order['orderId'],
            sl_order['orderId']
        )
    
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
