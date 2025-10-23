"""
 STREAMLIT UI for the Bot
Then open browser to: http://localhost:8501 or simply run streamlit run app.py
"""

import streamlit as st
import sys
import os
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import bot modules
from src.config import (
    test_connection, 
    get_account_balance, 
    get_current_price,
    get_symbol_info,
    get_client
)
from src.orders.market_orders import place_market_order
from src.orders.limit_orders import place_limit_order, get_open_orders, cancel_order
from src.advanced.stop_limit import place_stop_limit_order
from src.advanced.oco import place_oco_order
from src.advanced.twap import execute_twap_strategy
from src.logger_config import setup_logger

# Page configurations
st.set_page_config(
    page_title="Binance Futures Bot",
    page_icon="▪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS
st.markdown("""
<style>
    /* Global brutalist styling */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
    }
    
    /* Remove all rounded corners */
    .stButton button, .stSelectbox, .stNumberInput, .stRadio, div[data-baseweb="select"], 
    div[data-baseweb="input"], .stAlert, .stMetric {
        border-radius: 0 !important;
    }
    
    /* Harsh borders everywhere */
    .stButton button {
        border: 2px solid #000 !important;
        background: #fff !important;
        color: #000 !important;
        font-weight: 600 !important;
        font-size: 11px !important;
        padding: 8px 16px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton button:hover {
        background: #000 !important;
        color: #fff !important;
    }
    
    /* Minimal headers */
    h1, h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -1px;
        line-height: 1.2;
    }
    
    h1 { font-size: 24px !important; }
    h2 { font-size: 18px !important; }
    h3 { font-size: 14px !important; }
    
    /* Metric boxes - brutalist style */
    [data-testid="stMetricValue"] {
        font-size: 20px !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 10px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Remove colored delta arrows/stripes */
    [data-testid="stMetricDelta"] {
        display: none !important;
    }
    
    [data-testid="stMetricDeltaIcon-Up"],
    [data-testid="stMetricDeltaIcon-Down"] {
        display: none !important;
    }
    
    /* Input fields */
    input, select, textarea {
        border: 2px solid #000 !important;
        border-radius: 0 !important;
        font-size: 12px !important;
    }
    
    /* Alert boxes - minimal */
    .stAlert {
        padding: 12px !important;
        border-left: 4px solid #000 !important;
        background: #f5f5f5 !important;
        font-size: 11px !important;
    }
    
    /* Success */
    .stSuccess {
        border-left-color: #000 !important;
        background: #e8e8e8 !important;
    }
    
    /* Error */
    .stError {
        border-left-color: #000 !important;
        background: #e8e8e8 !important;
    }
    
    /* Info */
    .stInfo {
        border-left-color: #666 !important;
        background: #f5f5f5 !important;
    }
    
    /* Remove icons from alerts */
    .stAlert > div > div:first-child {
        display: none;
    }
    
    /* Sidebar brutalist */
    [data-testid="stSidebar"] {
        background: #000 !important;
        color: #fff !important;
        border-right: 4px solid #000 !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #fff !important;
    }
    
    [data-testid="stSidebar"] .stButton button {
        background: #fff !important;
        color: #000 !important;
        border: 2px solid #fff !important;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: #000 !important;
        color: #fff !important;
        border: 2px solid #fff !important;
    }
    
    /* Radio buttons */
    [data-testid="stRadio"] label {
        font-size: 11px !important;
        text-transform: uppercase;
    }
    
    /* Tables */
    .dataframe {
        font-size: 11px !important;
        border: 2px solid #000 !important;
    }
    
    .dataframe th {
        background: #000 !important;
        color: #fff !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 10px !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-size: 11px !important;
        text-transform: uppercase;
        font-weight: 600 !important;
    }
    
    /* Remove padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize logger
logger = setup_logger('StreamlitUI')

# Initialize session state
if 'connection_status' not in st.session_state:
    st.session_state.connection_status = None
if 'last_order' not in st.session_state:
    st.session_state.last_order = None
if 'price_history' not in st.session_state:
    st.session_state.price_history = []


def show_header():
    """Display main header"""
    st.markdown("# BINANCE FUTURES BOT")
    
    # Test connection on load
    if st.session_state.connection_status is None:
        with st.spinner("CONNECTING..."):
            st.session_state.connection_status = test_connection()
    
    # Connection status indicator - minimal
    if st.session_state.connection_status:
        st.success("CONNECTED | TESTNET")
    else:
        st.error("CONNECTION FAILED | CHECK .ENV")
        st.stop()


def show_account_overview():
    """Display account balance and info"""
    st.markdown("## ACCOUNT")
    
    balance = get_account_balance()
    
    if balance:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("BALANCE", f"${float(balance.get('walletBalance', 0)):,.2f}")
        
        with col2:
            st.metric("AVAILABLE", f"${float(balance.get('availableBalance', 0)):,.2f}")
        
        with col3:
            in_orders = float(balance.get('walletBalance', 0)) - float(balance.get('availableBalance', 0))
            st.metric("LOCKED", f"${in_orders:,.2f}")


def show_price_dashboard():
    """Display real-time prices for popular pairs"""
    st.markdown("## MARKET")
    
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"]
    cols = st.columns(len(symbols))
    
    for idx, symbol in enumerate(symbols):
        with cols[idx]:
            price = get_current_price(symbol)
            if price:
                st.metric(symbol.replace("USDT", ""), f"${price:,.2f}")


def show_market_order_form():
    """Form for placing market orders"""
    st.markdown("## MARKET ORDER")
    
    st.info("INSTANT EXECUTION AT CURRENT PRICE")
    
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.selectbox("PAIR", ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"], key="market_symbol")
        quantity = st.number_input("QTY", min_value=0.001, value=0.001, step=0.001, format="%.4f", key="market_quantity")
    
    with col2:
        side = st.radio("SIDE", ["BUY", "SELL"], key="market_side", horizontal=True)
        reduce_only = st.checkbox("REDUCE ONLY", key="market_reduce")
        
        # Show estimated cost
        current_price = get_current_price(symbol)
        if current_price:
            estimated_cost = quantity * current_price
            st.metric("EST COST", f"${estimated_cost:,.2f}")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("EXECUTE", type="primary", use_container_width=True):
            with st.spinner("EXECUTING..."):
                result = place_market_order(symbol, side, quantity, reduce_only)
                
                if result:
                    st.session_state.last_order = result
                    st.success(f"ORDER EXECUTED | ID: {result.get('orderId')}")
                else:
                    st.error("ORDER FAILED | CHECK LOGS")
    
    with col2:
        if st.session_state.last_order:
            if st.button("VIEW LAST", use_container_width=True):
                st.json(st.session_state.last_order)


def show_limit_order_form():
    """Form for placing limit orders"""
    st.markdown("## LIMIT ORDER")
    
    st.info("EXECUTES AT SPECIFIED PRICE ONLY")
    
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.selectbox("PAIR", ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"], key="limit_symbol")
        quantity = st.number_input("QTY", min_value=0.001, value=0.001, step=0.001, format="%.4f", key="limit_quantity")
        
        # Show current price for reference
        current_price = get_current_price(symbol)
        if current_price:
            st.info(f"MARKET: ${current_price:,.2f}")
    
    with col2:
        side = st.radio("SIDE", ["BUY", "SELL"], key="limit_side", horizontal=True)
        price = st.number_input("LIMIT PRICE", min_value=0.01, value=float(current_price) if current_price else 30000.0, 
                               step=0.01, format="%.2f", key="limit_price")
        
        # Show price difference
        if current_price:
            diff_pct = ((price - current_price) / current_price) * 100
            if side == "BUY":
                if diff_pct < 0:
                    st.success(f"{abs(diff_pct):.2f}% BELOW MARKET")
                else:
                    st.error(f"{diff_pct:.2f}% ABOVE MARKET")
            else:
                if diff_pct > 0:
                    st.success(f"{diff_pct:.2f}% ABOVE MARKET")
                else:
                    st.error(f"{abs(diff_pct):.2f}% BELOW MARKET")
    
    # Advanced options
    with st.expander("ADVANCED"):
        col1, col2 = st.columns(2)
        
        with col1:
            time_in_force = st.selectbox("TIME IN FORCE", ["GTC", "IOC", "FOK"])
        
        with col2:
            post_only = st.checkbox("POST ONLY")
            reduce_only = st.checkbox("REDUCE ONLY")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("PLACE ORDER", type="primary", use_container_width=True):
            with st.spinner("PLACING..."):
                result = place_limit_order(symbol, side, quantity, price, time_in_force, post_only, reduce_only)
                
                if result:
                    st.session_state.last_order = result
                    st.success(f"ORDER PLACED | ID: {result.get('orderId')}")
                    st.info(f"TARGET: ${price:,.2f}")
                else:
                    st.error("ORDER FAILED | CHECK LOGS")


def show_stop_limit_form():
    """Form for placing stop-limit orders"""
    st.markdown("## STOP-LIMIT ORDER")
    
    st.info("TWO-STAGE: TRIGGER + EXECUTION")
    
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.selectbox("PAIR", ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"], key="stop_symbol")
        quantity = st.number_input("QTY", min_value=0.001, value=0.001, step=0.001, format="%.4f", key="stop_quantity")
        
        current_price = get_current_price(symbol)
        if current_price:
            st.info(f"MARKET: ${current_price:,.2f}")
    
    with col2:
        side = st.radio("SIDE", ["BUY", "SELL"], key="stop_side", horizontal=True)
        stop_price = st.number_input("STOP PRICE", min_value=0.01, 
                                     value=float(current_price * 0.95) if current_price else 28000.0,
                                     step=0.01, format="%.2f", key="stop_trigger")
        limit_price = st.number_input("LIMIT PRICE", min_value=0.01,
                                      value=float(current_price * 0.94) if current_price else 27900.0,
                                      step=0.01, format="%.2f", key="stop_limit")
    
    # Visual explanation
    if current_price:
        st.markdown("### FLOW")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("CURRENT", f"${current_price:,.2f}")
        with col2:
            diff = ((stop_price - current_price) / current_price * 100)
            st.metric("TRIGGER", f"${stop_price:,.2f}")
            st.caption(f"{diff:+.2f}%")
        with col3:
            diff = ((limit_price - current_price) / current_price * 100)
            st.metric("EXECUTE", f"${limit_price:,.2f}")
            st.caption(f"{diff:+.2f}%")
    
    if st.button("PLACE ORDER", type="primary", use_container_width=True):
        with st.spinner("PLACING..."):
            result = place_stop_limit_order(symbol, side, quantity, stop_price, limit_price)
            
            if result:
                st.session_state.last_order = result
                st.success(f"ORDER PLACED | ID: {result.get('orderId')}")
                st.info(f"TRIGGER: ${stop_price:,.2f} | EXECUTE: ${limit_price:,.2f}")
            else:
                st.error("ORDER FAILED | CHECK LOGS")


def show_oco_form():
    """Form for placing OCO (One-Cancels-Other) orders"""
    st.markdown("## ⚡ OCO ORDER (ONE-CANCELS-OTHER)")
    st.markdown("*Advanced: Set both take-profit and stop-loss. When one fills, the other cancels automatically.*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.selectbox("PAIR", ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"], key="oco_symbol")
        side = st.radio("SIDE", ["SELL", "BUY"], horizontal=True, key="oco_side",
                       help="Usually SELL for long positions, BUY for short positions")
    
    with col2:
        quantity = st.number_input("QUANTITY", min_value=0.001, value=0.01,
                                  step=0.001, format="%.3f", key="oco_quantity")
        
        current_price = get_current_price(symbol)
        if current_price:
            st.metric("CURRENT PRICE", f"${current_price:,.2f}")
    
    st.markdown("---")
    st.markdown("### PRICE TARGETS")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 TAKE PROFIT**")
        take_profit = st.number_input("Price", min_value=0.01, value=35000.0,
                                     step=100.0, format="%.2f", key="oco_tp",
                                     help="Sell/Buy at this price for profit")
        
        if current_price and side == "SELL":
            st.caption(f"({((take_profit - current_price) / current_price * 100):+.2f}% from market)")
    
    with col2:
        st.markdown("**🛡️ STOP LOSS**")
        stop_loss = st.number_input("Price", min_value=0.01, value=28000.0,
                                   step=100.0, format="%.2f", key="oco_sl",
                                   help="Sell/Buy at this price to limit losses")
        
        if current_price and side == "SELL":
            st.caption(f"({((stop_loss - current_price) / current_price * 100):+.2f}% from market)")
    
    with st.expander("ADVANCED"):
        stop_limit_price = st.number_input("Stop Limit Price (Optional)", 
                                          min_value=0.01, value=0.0,
                                          step=100.0, format="%.2f", key="oco_stop_limit",
                                          help="Limit price for stop order. Leave at 0 for market stop.")
    
    st.markdown("---")
    
    # Preview
    st.markdown("### PREVIEW")
    st.info(f"""
    **{side}** {quantity} {symbol}
    
    ✅ **If price reaches ${take_profit:,.2f}** → Take profit fills, stop loss cancels
    
    ❌ **If price reaches ${stop_loss:,.2f}** → Stop loss fills, take profit cancels
    
    ⚠️ Remember: When one order fills, you must manually cancel the other!
    """)
    
    if st.button("PLACE OCO ORDER", type="primary", use_container_width=True):
        with st.spinner("PLACING..."):
            result = place_oco_order(
                symbol, side, quantity, take_profit, stop_loss,
                stop_limit_price if stop_limit_price > 0 else None
            )
            
            if result:
                tp_order, sl_order = result
                st.success(f"OCO ORDERS PLACED!")
                st.info(f"Take Profit ID: {tp_order.get('orderId')}")
                st.info(f"Stop Loss ID: {sl_order.get('orderId')}")
                st.warning("⚠️ When one fills, cancel the other manually!")
            else:
                st.error("ORDER FAILED | CHECK LOGS")


def show_twap_form():
    """Form for executing TWAP strategy"""
    st.markdown("## ⚡ TWAP STRATEGY")
    st.markdown("*Advanced: Split large order into smaller chunks executed over time for better average price.*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.selectbox("PAIR", ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"], key="twap_symbol")
        side = st.radio("SIDE", ["BUY", "SELL"], horizontal=True, key="twap_side")
    
    with col2:
        total_quantity = st.number_input("TOTAL QUANTITY", min_value=0.001, value=0.1,
                                        step=0.01, format="%.3f", key="twap_quantity")
        
        current_price = get_current_price(symbol)
        if current_price:
            total_value = total_quantity * current_price
            st.metric("TOTAL VALUE", f"${total_value:,.2f}")
    
    st.markdown("---")
    st.markdown("### TIME PARAMETERS")
    
    col1, col2 = st.columns(2)
    
    with col1:
        duration = st.number_input("DURATION (minutes)", min_value=1, value=60,
                                  step=5, key="twap_duration",
                                  help="How long to spread orders over")
    
    with col2:
        intervals = st.number_input("NUMBER OF ORDERS", min_value=2, value=10,
                                   step=1, key="twap_intervals",
                                   help="How many chunks to split into")
    
    # Calculate preview
    qty_per_order = total_quantity / intervals
    interval_time = duration / intervals
    
    st.markdown("---")
    st.markdown("### CALCULATION PREVIEW")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("QUANTITY PER ORDER", f"{qty_per_order:.8f}")
    
    with col2:
        st.metric("INTERVAL TIME", f"{interval_time:.2f} min")
    
    with col3:
        if current_price:
            value_per_order = qty_per_order * current_price
            st.metric("VALUE PER ORDER", f"${value_per_order:,.2f}")
    
    st.info(f"""
    **Strategy Execution:**
    
    - Execute {intervals} orders
    - Every {interval_time:.2f} minutes
    - Each order: {qty_per_order:.8f} {symbol}
    - Total duration: {duration} minutes
    - Total quantity: {total_quantity} {symbol}
    
    ⏳ This will take approximately {duration} minutes to complete.
    """)
    
    st.warning("⚠️ TWAP is blocking - bot will be busy during execution. Monitor progress in terminal.")
    
    if st.button("START TWAP STRATEGY", type="primary", use_container_width=True):
        with st.spinner(f"EXECUTING TWAP STRATEGY... ({duration} minutes)"):
            result = execute_twap_strategy(
                symbol, side, total_quantity, duration, intervals
            )
            
            if result and len(result) > 0:
                st.success(f"TWAP COMPLETED | {len(result)} ORDERS EXECUTED")
                
                # Calculate average price
                total_qty = sum(float(o.get('executedQty', 0)) for o in result)
                total_cost = sum(float(o.get('executedQty', 0)) * float(o.get('avgPrice', 0)) for o in result)
                avg_price = total_cost / total_qty if total_qty > 0 else 0
                
                st.metric("AVERAGE EXECUTION PRICE", f"${avg_price:,.2f}")
                st.info(f"Total Executed: {total_qty:.8f} {symbol}")
            else:
                st.error("TWAP FAILED | CHECK LOGS")


def show_open_orders():
    """Display and manage open orders"""
    st.markdown("## OPEN ORDERS")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        symbol_filter = st.selectbox("FILTER", ["All Symbols", "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"], key="order_filter")
    
    with col2:
        if st.button("REFRESH", use_container_width=True):
            st.rerun()
    
    # Get orders
    symbol = None if symbol_filter == "All Symbols" else symbol_filter
    orders = get_open_orders(symbol)
    
    if orders and len(orders) > 0:
        # Convert to DataFrame for better display
        orders_data = []
        for order in orders:
            orders_data.append({
                "Order ID": order.get('orderId'),
                "Symbol": order.get('symbol'),
                "Type": order.get('type'),
                "Side": order.get('side'),
                "Quantity": float(order.get('origQty', 0)),
                "Price": f"${float(order.get('price', 0)):,.2f}" if order.get('price') != '0' else 'Market',
                "Status": order.get('status'),
                "Time": datetime.fromtimestamp(order.get('time', 0) / 1000).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        df = pd.DataFrame(orders_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Cancel order section
        st.markdown("---")
        st.markdown("### CANCEL ORDER")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            cancel_symbol = st.selectbox("SYMBOL", list(set([o['symbol'] for o in orders])), key="cancel_symbol")
        
        with col2:
            # Filter order IDs for selected symbol
            symbol_orders = [o for o in orders if o['symbol'] == cancel_symbol]
            order_id = st.selectbox("ORDER ID", [o['orderId'] for o in symbol_orders], key="cancel_order_id")
        
        with col3:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if st.button("CANCEL", type="secondary", use_container_width=True):
                if cancel_order(cancel_symbol, order_id):
                    st.success(f"ORDER {order_id} CANCELED")
                    st.rerun()
                else:
                    st.error("CANCEL FAILED")
    else:
        st.info("NO OPEN ORDERS")


def show_price_chart(symbol="BTCUSDT"):
    """Display price chart (simplified version)"""
    st.markdown(f"## {symbol}")
    
    try:
        client = get_client()
        
        # Get recent klines (candlestick data)
        klines = client.futures_klines(symbol=symbol, interval="15m", limit=50)
        
        # Convert to DataFrame
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Convert to proper types
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        # Create candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol
        )])
        
        fig.update_layout(
            title=None,
            yaxis_title="PRICE",
            xaxis_title="TIME",
            height=400,
            template="plotly_white",
            font=dict(family="IBM Plex Mono", size=10),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=40, r=40, t=20, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Failed to load chart: {str(e)}")


def main():
    """Main application"""
    
    # Header
    show_header()
    
    # Sidebar navigation
    st.sidebar.markdown("## NAVIGATION")
    
    page = st.sidebar.radio(
        "",
        [
            "DASHBOARD",
            "MARKET ORDER",
            "LIMIT ORDER",
            "━━━ ⚡ ADVANCED ━━━",
            "STOP-LIMIT",
            "OCO ORDER",
            "TWAP STRATEGY",
            "━━━━━━━━━━━━━",
            "OPEN ORDERS",
            "CHARTS",
            "HELP"
        ],
        label_visibility="collapsed"
    )
    
    # Account overview (always visible)
    with st.sidebar:
        st.markdown("---")
        balance = get_account_balance()
        if balance:
            st.metric("BALANCE", f"${float(balance.get('walletBalance', 0)):,.2f}")
        
        st.markdown("---")
        st.markdown("### PRICES")
        symbols = ["BTCUSDT", "ETHUSDT"]
        for symbol in symbols:
            price = get_current_price(symbol)
            if price:
                st.metric(symbol.replace("USDT", ""), f"${price:,.2f}")
    
    # Main content based on selection
    if page == "DASHBOARD":
        st.markdown("# DASHBOARD")
        show_price_dashboard()
        
        st.markdown("---")
        
        st.markdown("---")
        show_open_orders()
    
    elif page == "MARKET ORDER":
        show_market_order_form()
    
    elif page == "LIMIT ORDER":
        show_limit_order_form()
    
    elif page == "━━━ ⚡ ADVANCED ━━━" or page == "━━━━━━━━━━━━━":
        # Separator pages - redirect to dashboard
        st.markdown("# SELECT AN ORDER TYPE")
        st.info("Choose from the menu on the left")
    
    elif page == "STOP-LIMIT":
        show_stop_limit_form()
    
    elif page == "OCO ORDER":
        show_oco_form()
    
    elif page == "TWAP STRATEGY":
        show_twap_form()
    
    elif page == "OPEN ORDERS":
        show_open_orders()
    
    elif page == "CHARTS":
        st.markdown("# CHARTS")
        
        symbol = st.selectbox("PAIR", ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"], key="chart_symbol")
        
        show_price_chart(symbol)
    
    elif page == "HELP":
        st.markdown("# HELP")
        
        st.markdown("""
        ## QUICK START
        
        ### MARKET ORDERS
        Execute immediately at current price
        
        ### LIMIT ORDERS
        Execute only at your target price
        
        ### STOP-LIMIT ORDERS
        Two prices - trigger and execution
        
        ---
        
        ## NOTES
        
        - TESTNET MODE (fake money)
        - All actions logged to bot.log
        - Start with small quantities
        - Use stop-losses in real trading
        - Check open orders regularly
        
        ---
        
        ## DOCS
        
        - SETUP_GUIDE.md - Setup instructions
        - TRADING_CONCEPTS.md - Trading basics
        - QUICK_START.md - Command reference
        
        ---
        
        ## TROUBLESHOOT
        
        **Connection Failed?**
        Check .env file for API keys
        
        **Order Failed?**
        Check bot.log for errors
        Verify balance and quantity
        """)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**BINANCE FUTURES BOT**")
    st.sidebar.markdown("v1.0 | TESTNET")


if __name__ == "__main__":
    main()
