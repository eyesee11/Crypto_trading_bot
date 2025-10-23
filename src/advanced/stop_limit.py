"""
STOP-LIMIT ORDERS/ Conditional Price Alert Orders
"""

import sys
import os
from typing import Dict, Optional
from binance.exceptions import BinanceAPIException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..config import get_client, get_current_price
from ..validator import validate_order
from ..logger_config import setup_logger, log_order, log_error, log_success

logger = setup_logger('StopLimitOrders')


def place_stop_limit_order(
    symbol: str,
    side: str,
    quantity: float,
    stop_price: float,
    limit_price: float,
    reduce_only: bool = False
) -> Optional[Dict]:
    """
    Place a stop-limit order.
    
    PARAMETERS:
    - symbol: Trading pair (e.g., "BTCUSDT")
    - side: "BUY" or "SELL"
    - quantity: Amount to trade
    - stop_price: Trigger price (when to activate)
    - limit_price: Execution price (after trigger)
    - reduce_only: Only close positions
    
    EXAMPLE - Stop Loss:
    ```python
    # Bought BTC @ $30k, set stop-loss @ $28k
    order = place_stop_limit_order(
        "BTCUSDT", "SELL", 0.01,
        stop_price=28000,    # Trigger at $28k
        limit_price=27900    # Sell at $27.9k
    )
    ```
    
    EXAMPLE - Breakout Entry:
    ```python
    # BTC at $30k, buy if breaks $31k
    order = place_stop_limit_order(
        "BTCUSDT", "BUY", 0.01,
        stop_price=31000,    # Trigger at $31k
        limit_price=31100    # Buy at $31.1k
    )
    ```
    """
    
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"📝 PLACING STOP-LIMIT ORDER")
        logger.info(f"{'='*60}")
        
        # Validate
        is_valid, message, validated_data = validate_order(
            symbol, side, quantity, limit_price, "STOP_LIMIT"
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
            logger.info(f"🎯 Stop price: ${stop_price:,.2f}")
            logger.info(f"💰 Limit price: ${limit_price:,.2f}")
            
            stop_diff = ((stop_price - current) / current) * 100
            logger.info(f"📊 Stop is {stop_diff:+.2f}% from current price")
            
            # Check limit price vs stop price (Binance requirement)
            limit_stop_diff = abs((limit_price - stop_price) / stop_price) * 100
            logger.info(f"📏 Limit price is {limit_stop_diff:.2f}% away from stop price")
            
            # Binance typically requires limit price within ~5% of stop price
            if limit_stop_diff > 5:
                logger.warning(f"⚠️  Limit price is {limit_stop_diff:.1f}% from stop price.")
                logger.warning(f"⚠️  Binance may reject if difference is too large (typically >5%).")
                logger.warning(f"💡 Suggestion: Try limit price closer to stop price (e.g., ${stop_price * 0.95:,.2f} to ${stop_price * 1.05:,.2f})")
            
            # Logic check
            if side == "SELL" and stop_price > current:
                logger.warning(f"⚠️  SELL stop above market - will trigger immediately!")
            elif side == "BUY" and stop_price < current:
                logger.warning(f"⚠️  BUY stop below market - will trigger immediately!")
        
        # Create order
        client = get_client()
        
        order_params = {
            'symbol': symbol,
            'side': side,
            'type': 'STOP',
            'quantity': quantity,
            'price': f"{limit_price:.10f}",
            'stopPrice': f"{stop_price:.10f}",
            'timeInForce': 'GTC'
        }
        
        if reduce_only:
            order_params['reduceOnly'] = True
        
        log_order(logger, "STOP_LIMIT", symbol, side, quantity,
                 stop_price=stop_price, limit_price=limit_price)
        
        response = client.futures_create_order(**order_params)
        
        order_id = response.get('orderId')
        status = response.get('status')
        
        log_success(logger, "Stop-limit order placed",
                   order_id=order_id, status=status,
                   stop_price=f"${stop_price:,.2f}",
                   limit_price=f"${limit_price:,.2f}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ STOP-LIMIT ORDER PLACED!")
        logger.info(f"{'='*60}")
        logger.info(f"🆔 Order ID: {order_id}")
        logger.info(f"📊 Symbol: {symbol}")
        logger.info(f"🎯 Stop Price: ${stop_price:,.2f} (trigger)")
        logger.info(f"💰 Limit Price: ${limit_price:,.2f} (execution)")
        logger.info(f"📈 Status: {status}")
        logger.info(f"\n⏳ Waiting for price to reach ${stop_price:,.2f}...")
        logger.info(f"💡 Once triggered, limit order @ ${limit_price:,.2f} will be placed")
        logger.info(f"{'='*60}\n")
        
        return response
        
    except Exception as e:
        log_error(logger, "Failed to place stop-limit order", e)
        return None


def main():
    """CLI for stop-limit orders"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Place stop-limit orders')
    parser.add_argument('symbol', help='Trading symbol')
    parser.add_argument('side', choices=['BUY', 'SELL', 'buy', 'sell'])
    parser.add_argument('quantity', type=float, help='Quantity')
    parser.add_argument('stop_price', type=float, help='Stop/trigger price')
    parser.add_argument('limit_price', type=float, help='Limit/execution price')
    parser.add_argument('--reduce-only', action='store_true')
    
    args = parser.parse_args()
    
    result = place_stop_limit_order(
        args.symbol.upper(), args.side.upper(),
        args.quantity, args.stop_price, args.limit_price,
        args.reduce_only
    )
    
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
