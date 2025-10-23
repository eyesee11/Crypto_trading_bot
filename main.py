"""
🤖 BINANCE FUTURES TRADING BOT - Main CLI Entry Point

This is the central command interface for all bot operations.
Think of it as the "remote control" for your trading bot.

USAGE:
    python main.py <command> [arguments]

AVAILABLE COMMANDS:
    market      - Place market order (instant execution)
    limit       - Place limit order (wait for target price)
    stop-limit  - Place stop-limit order (conditional)
    oco         - Place OCO order (one-cancels-other)
    twap        - Execute TWAP strategy (time-weighted)
    grid        - Execute grid trading strategy
    balance     - Check account balance
    orders      - View open orders
    test        - Test API connection

REAL-LIFE ANALOGY:
Think of this main.py as the dashboard of your car:
- Different buttons for different functions
- One interface controls everything
- Clear display of what's happening
- Safety checks before executing

"""

import sys
import os
import argparse
from typing import Optional

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import test_connection, get_account_balance, get_current_price
from src.orders.market_orders import place_market_order
from src.orders.limit_orders import place_limit_order, get_open_orders, cancel_order
from src.advanced.stop_limit import place_stop_limit_order
from src.advanced.oco import place_oco_order
from src.advanced.twap import execute_twap_strategy
from src.logger_config import setup_logger

# Initialize main logger
logger = setup_logger('MainCLI')


def display_banner():
    """Display welcome banner"""
    print("\n" + "="*70)
    print("🤖  BINANCE FUTURES TRADING BOT")
    print("="*70)
    print("📊 Trading on: Binance USDT-M Futures (Testnet)")
    print("💻 Mode: Command Line Interface")
    print("📝 All actions are logged to: bot.log")
    print("="*70 + "\n")


def command_test(args):
    """Test API connection"""
    logger.info("Testing API connection...")
    
    if test_connection():
        print("✅ Connection successful!")
        print("💡 You're ready to start trading")
        return 0
    else:
        print("❌ Connection failed")
        print("💡 Check your .env file and API credentials")
        return 1


def command_balance(args):
    """Check account balance"""
    logger.info("Fetching account balance...")
    
    balance = get_account_balance()
    
    if balance:
        print("\n💰 ACCOUNT BALANCE")
        print("="*50)
        print(f"Asset: {balance.get('asset', 'USDT')}")
        print(f"Total Balance: {balance.get('walletBalance', 'N/A')} USDT")
        print(f"Available: {balance.get('availableBalance', 'N/A')} USDT")
        print(f"In Orders: {float(balance.get('walletBalance', 0)) - float(balance.get('availableBalance', 0)):.8f} USDT")
        print("="*50 + "\n")
        return 0
    else:
        print("❌ Could not fetch balance")
        return 1


def command_price(args):
    """Get current price for symbol"""
    symbol = args.symbol.upper()
    logger.info(f"Fetching current price for {symbol}...")
    
    price = get_current_price(symbol)
    
    if price:
        print(f"\n💵 Current {symbol} Price: ${price:,.2f}\n")
        return 0
    else:
        print(f"❌ Could not fetch price for {symbol}")
        return 1


def command_market(args):
    """Place market order"""
    logger.info(f"Executing market order: {args.side} {args.quantity} {args.symbol}")
    
    result = place_market_order(
        symbol=args.symbol.upper(),
        side=args.side.upper(),
        quantity=args.quantity,
        reduce_only=args.reduce_only
    )
    
    return 0 if result else 1


def command_limit(args):
    """Place limit order"""
    logger.info(f"Executing limit order: {args.side} {args.quantity} {args.symbol} @ ${args.price}")
    
    result = place_limit_order(
        symbol=args.symbol.upper(),
        side=args.side.upper(),
        quantity=args.quantity,
        price=args.price,
        time_in_force=args.time_in_force,
        post_only=args.post_only,
        reduce_only=args.reduce_only
    )
    
    return 0 if result else 1


def command_stop_limit(args):
    """Place stop-limit order"""
    logger.info(f"Executing stop-limit order: {args.side} {args.quantity} {args.symbol}")
    
    result = place_stop_limit_order(
        symbol=args.symbol.upper(),
        side=args.side.upper(),
        quantity=args.quantity,
        stop_price=args.stop_price,
        limit_price=args.limit_price,
        reduce_only=args.reduce_only
    )
    
    return 0 if result else 1


def command_oco(args):
    """Place OCO (One-Cancels-Other) order"""
    logger.info(f"Executing OCO order: {args.side} {args.quantity} {args.symbol}")
    
    result = place_oco_order(
        symbol=args.symbol.upper(),
        side=args.side.upper(),
        quantity=args.quantity,
        take_profit_price=args.take_profit,
        stop_loss_price=args.stop_loss,
        stop_limit_price=args.stop_limit
    )
    
    return 0 if result else 1


def command_twap(args):
    """Execute TWAP strategy"""
    logger.info(f"Executing TWAP strategy: {args.side} {args.quantity} {args.symbol}")
    
    result = execute_twap_strategy(
        symbol=args.symbol.upper(),
        side=args.side.upper(),
        total_quantity=args.quantity,
        duration_minutes=args.duration,
        num_intervals=args.intervals
    )
    
    return 0 if result else 1


def command_orders(args):
    """List open orders"""
    symbol = args.symbol.upper() if args.symbol else None
    
    logger.info(f"Fetching open orders{' for ' + symbol if symbol else ''}...")
    
    orders = get_open_orders(symbol)
    
    if orders is not None:
        if len(orders) == 0:
            print("\n📋 No open orders\n")
        else:
            print(f"\n📋 OPEN ORDERS ({len(orders)} total)")
            print("="*80)
            for i, order in enumerate(orders, 1):
                print(f"\n{i}. Order ID: {order['orderId']}")
                print(f"   Symbol: {order['symbol']}")
                print(f"   Side: {order['side']}")
                print(f"   Type: {order['type']}")
                print(f"   Quantity: {order['origQty']}")
                if 'price' in order and order['price'] != '0':
                    print(f"   Price: ${float(order['price']):,.2f}")
                if 'stopPrice' in order and order['stopPrice'] != '0':
                    print(f"   Stop Price: ${float(order['stopPrice']):,.2f}")
                print(f"   Status: {order['status']}")
            print("="*80 + "\n")
        return 0
    else:
        print("❌ Could not fetch orders")
        return 1


def command_cancel(args):
    """Cancel an order"""
    logger.info(f"Canceling order {args.order_id} for {args.symbol}...")
    
    if cancel_order(args.symbol.upper(), args.order_id):
        print(f"✅ Order {args.order_id} canceled successfully")
        return 0
    else:
        print(f"❌ Failed to cancel order {args.order_id}")
        return 1


def main():
    """Main entry point"""
    
    # Create main parser
    parser = argparse.ArgumentParser(
        description='Binance Futures Trading Bot - CLI Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
BASIC COMMANDS:
  Test connection:
    python main.py test
  
  Check balance:
    python main.py balance
  
  Get BTC price:
    python main.py price BTCUSDT
  
  Place market order:
    python main.py market BTCUSDT BUY 0.01
  
  Place limit order:
    python main.py limit BTCUSDT BUY 0.01 28000
  
  List open orders:
    python main.py orders
    python main.py orders BTCUSDT
  
  Cancel order:
    python main.py cancel BTCUSDT 12345

⚡ ADVANCED COMMANDS:
  Stop-limit order (conditional):
    python main.py stop-limit BTCUSDT SELL 0.01 28000 27900
  
  OCO order (one-cancels-other):
    python main.py oco BTCUSDT SELL 0.01 35000 28000
    # Take profit @ 35k OR stop loss @ 28k
  
  TWAP strategy (split large order over time):
    python main.py twap BTCUSDT BUY 0.5 --duration 60 --intervals 10
    # Buy 0.5 BTC over 60 minutes in 10 chunks

For detailed help on specific commands:
  python main.py <command> --help

Logs are saved to: bot.log
        """
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Test command
    parser_test = subparsers.add_parser('test', help='Test API connection')
    parser_test.set_defaults(func=command_test)
    
    # Balance command
    parser_balance = subparsers.add_parser('balance', help='Check account balance')
    parser_balance.set_defaults(func=command_balance)
    
    # Price command
    parser_price = subparsers.add_parser('price', help='Get current price')
    parser_price.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    parser_price.set_defaults(func=command_price)
    
    # Market order command
    parser_market = subparsers.add_parser('market', help='Place market order')
    parser_market.add_argument('symbol', help='Trading symbol')
    parser_market.add_argument('side', choices=['BUY', 'SELL', 'buy', 'sell'])
    parser_market.add_argument('quantity', type=float, help='Quantity to trade')
    parser_market.add_argument('--reduce-only', action='store_true',
                              help='Only reduce existing position')
    parser_market.set_defaults(func=command_market)
    
    # Limit order command
    parser_limit = subparsers.add_parser('limit', help='Place limit order')
    parser_limit.add_argument('symbol', help='Trading symbol')
    parser_limit.add_argument('side', choices=['BUY', 'SELL', 'buy', 'sell'])
    parser_limit.add_argument('quantity', type=float, help='Quantity to trade')
    parser_limit.add_argument('price', type=float, help='Limit price')
    parser_limit.add_argument('--time-in-force', default='GTC',
                            choices=['GTC', 'IOC', 'FOK'],
                            help='Time in force (default: GTC)')
    parser_limit.add_argument('--post-only', action='store_true',
                            help='Post-only (maker) order')
    parser_limit.add_argument('--reduce-only', action='store_true',
                            help='Only reduce existing position')
    parser_limit.set_defaults(func=command_limit)
    
    # Stop-limit order command
    parser_stop = subparsers.add_parser('stop-limit', help='⚡ [ADVANCED] Place stop-limit order')
    parser_stop.add_argument('symbol', help='Trading symbol')
    parser_stop.add_argument('side', choices=['BUY', 'SELL', 'buy', 'sell'])
    parser_stop.add_argument('quantity', type=float, help='Quantity to trade')
    parser_stop.add_argument('stop_price', type=float, help='Stop/trigger price')
    parser_stop.add_argument('limit_price', type=float, help='Limit/execution price')
    parser_stop.add_argument('--reduce-only', action='store_true',
                            help='Only reduce existing position')
    parser_stop.set_defaults(func=command_stop_limit)
    
    # OCO order command (ADVANCED)
    parser_oco = subparsers.add_parser('oco', help='⚡ [ADVANCED] Place OCO (One-Cancels-Other) order')
    parser_oco.add_argument('symbol', help='Trading symbol')
    parser_oco.add_argument('side', choices=['BUY', 'SELL', 'buy', 'sell'])
    parser_oco.add_argument('quantity', type=float, help='Quantity to trade')
    parser_oco.add_argument('take_profit', type=float, help='Take profit price')
    parser_oco.add_argument('stop_loss', type=float, help='Stop loss price')
    parser_oco.add_argument('--stop-limit', type=float, default=None,
                           help='Stop limit price (optional)')
    parser_oco.set_defaults(func=command_oco)
    
    # TWAP strategy command (ADVANCED)
    parser_twap = subparsers.add_parser('twap', help='⚡ [ADVANCED] Execute TWAP strategy')
    parser_twap.add_argument('symbol', help='Trading symbol')
    parser_twap.add_argument('side', choices=['BUY', 'SELL', 'buy', 'sell'])
    parser_twap.add_argument('quantity', type=float, help='Total quantity to trade')
    parser_twap.add_argument('--duration', type=int, required=True,
                            help='Duration in minutes')
    parser_twap.add_argument('--intervals', type=int, required=True,
                            help='Number of order intervals')
    parser_twap.set_defaults(func=command_twap)
    
    # Orders command
    parser_orders = subparsers.add_parser('orders', help='List open orders')
    parser_orders.add_argument('symbol', nargs='?', help='Filter by symbol (optional)')
    parser_orders.set_defaults(func=command_orders)
    
    # Cancel command
    parser_cancel = subparsers.add_parser('cancel', help='Cancel an order')
    parser_cancel.add_argument('symbol', help='Trading symbol')
    parser_cancel.add_argument('order_id', type=int, help='Order ID to cancel')
    parser_cancel.set_defaults(func=command_cancel)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show banner
    display_banner()
    
    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation canceled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        logger.error(f"Unexpected error in main: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
