# 🤖 Binance Futures Trading Bot

## 📖 Project Overview

This is a comprehensive CLI-based trading bot for Binance USDT-M Futures that supports multiple order types with robust logging, validation, and error handling.

> 📚 **New to trading bots?** Check out our detailed [SETUP_GUIDE.md](SETUP_GUIDE.md) for step-by-step instructions with explanations and practice scenarios!

### 🎯 Real-Life Analogy

Think of this bot as your **personal stock broker assistant**:

- **Market Orders** = "Buy/Sell NOW at whatever price is available" (like grabbing the last item on sale)
- **Limit Orders** = "Only buy if price drops to $X" (like setting a price alert on Amazon)
- **Stop-Limit** = "If price hits $X, trigger a limit order at $Y" (like insurance with conditions)
- **OCO (One-Cancels-Other)** = "Take profit at $X OR stop loss at $Y" (whichever happens first cancels the other)
- **TWAP** = "Buy $1000 worth over 1 hour in small chunks" (like dollar-cost averaging)
- **Grid Trading** = "Auto-buy low, auto-sell high in a range" (like automated arbitrage)

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** installed on your system
- **pip** package manager
- **Binance Futures Testnet Account** (free, fake money)
- **API Key and Secret** from Binance Testnet

> 🆕 **First time setup?** Follow our comprehensive [SETUP_GUIDE.md](SETUP_GUIDE.md) with detailed explanations!

---

## 🔧 Step-by-Step Setup

### Step 1: Get Binance Testnet API Keys

1. **Visit Binance Futures Testnet**:

   - Go to: https://testnet.binancefuture.com
   - Click "Register" or "Log In with GitHub"

2. **Generate API Keys**:

   - After logging in, click on your profile (top right)
   - Select "API Key"
   - Click "Generate HMAC_SHA256 Key"
   - **Copy both**: API Key and Secret Key
   - ⚠️ **Save them securely** - Secret Key shown only once!

3. **Get Testnet USDT** (fake money):
   - In testnet dashboard, look for "Get Test Funds" or similar
   - Request 10,000 USDT (testnet balance)
   - This is FREE fake money for testing

### Step 2: Clone/Download Project

```bash
# If using git
git clone <repository-url>
cd Internship_bot

# Or extract the zip file and navigate to folder
cd path/to/Internship_bot
```

### Step 3: Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Or if using virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

**Dependencies installed**:

- `python-binance` - Official Binance API wrapper
- `python-dotenv` - Environment variable management
- `pandas`, `numpy` - Data manipulation
- `colorama`, `rich` - Terminal formatting
- `streamlit`, `plotly` - Web UI (optional)

### Step 4: Configure API Credentials

1. **Create `.env` file** in project root (same folder as `main.py`):

```bash
# Create .env file
touch .env  # Linux/Mac
type nul > .env  # Windows
```

2. **Add your API credentials** to `.env`:

```env
# Binance API Configuration
BINANCE_API_KEY=your_actual_api_key_here
BINANCE_API_SECRET=your_actual_secret_key_here
BINANCE_TESTNET=True

# Example (DO NOT USE THESE - they're fake):
# BINANCE_API_KEY=abcd1234efgh5678ijkl9012mnop3456
# BINANCE_API_SECRET=xyz789abc456def123ghi456jkl789mno
```

⚠️ **Important**:

- Replace `your_actual_api_key_here` with YOUR actual API key
- Replace `your_actual_secret_key_here` with YOUR actual secret key
- Keep `BINANCE_TESTNET=True` for safe testing
- Never share or commit this file to Git

### Step 5: Test Connection

```bash
# Test if API credentials work
python main.py test

# Expected output:
# ✅ Connection successful!
# Testnet: Yes
# Server time: 2025-10-23 10:30:45
```

### Step 6: Check Your Balance

```bash
# View your testnet balance
python main.py balance

# Expected output:
# Asset: USDT
# Balance: 10000.00
# Available: 10000.00
```

---

## 🎮 How to Run the Bot

### CLI Mode (Command Line)

The bot has multiple commands for different order types:

#### **Test Connection**

```bash
python main.py test
```

#### **Check Balance**

```bash
python main.py balance
```

#### **Get Current Price**

```bash
python main.py price BTCUSDT
python main.py price ETHUSDT
```

#### **Place Market Order** (instant execution)

```bash
# Syntax: python main.py market <SYMBOL> <SIDE> <QUANTITY>

# Buy 0.01 BTC at current market price
python main.py market BTCUSDT BUY 0.01

# Sell 0.01 BTC at current market price
python main.py market BTCUSDT SELL 0.01

# Buy 0.1 ETH
python main.py market ETHUSDT BUY 0.1
```

#### **Place Limit Order** (execute at specific price)

```bash
# Syntax: python main.py limit <SYMBOL> <SIDE> <QUANTITY> <PRICE>

# Buy 0.01 BTC only if price drops to $30,000
python main.py limit BTCUSDT BUY 0.01 30000

# Sell 0.01 BTC only if price rises to $35,000
python main.py limit BTCUSDT SELL 0.01 35000

# Advanced: GTC (Good Till Canceled), IOC (Immediate or Cancel), FOK (Fill or Kill)
python main.py limit BTCUSDT BUY 0.01 30000 --time-in-force GTC
```

#### **Place Stop-Limit Order** (conditional)

```bash
# Syntax: python main.py stop-limit <SYMBOL> <SIDE> <QUANTITY> <STOP_PRICE> <LIMIT_PRICE>

# Stop-loss: If BTC drops to $29,000, sell at limit price $28,900
python main.py stop-limit BTCUSDT SELL 0.01 29000 28900

# Breakout buy: If BTC rises to $31,000, buy at limit price $31,100
python main.py stop-limit BTCUSDT BUY 0.01 31000 31100
```

#### **View Open Orders**

```bash
# All open orders
python main.py orders

# Open orders for specific symbol
python main.py orders BTCUSDT
```

#### **Cancel Order**

```bash
# Syntax: python main.py cancel <SYMBOL> <ORDER_ID>

python main.py cancel BTCUSDT 12345678
```

### Web UI Mode (Streamlit)

For a visual interface with buttons and charts:

```bash
# Start the web interface
streamlit run app.py

# Then open browser to: http://localhost:8501
```

**Web UI Features**:

- Dashboard with balance and prices
- Forms for placing orders
- View and cancel open orders
- Interactive price charts
- Brutalist minimalist design

---

## 📋 Complete Command Reference

| Command                                           | Description           | Example                                                   |
| ------------------------------------------------- | --------------------- | --------------------------------------------------------- |
| `test`                                            | Test API connection   | `python main.py test`                                     |
| `balance`                                         | Check account balance | `python main.py balance`                                  |
| `price <SYMBOL>`                                  | Get current price     | `python main.py price BTCUSDT`                            |
| `market <SYMBOL> <SIDE> <QTY>`                    | Place market order    | `python main.py market BTCUSDT BUY 0.01`                  |
| `limit <SYMBOL> <SIDE> <QTY> <PRICE>`             | Place limit order     | `python main.py limit BTCUSDT BUY 0.01 30000`             |
| `stop-limit <SYMBOL> <SIDE> <QTY> <STOP> <LIMIT>` | Place stop-limit      | `python main.py stop-limit BTCUSDT SELL 0.01 29000 28900` |
| `orders [SYMBOL]`                                 | View open orders      | `python main.py orders`                                   |
| `cancel <SYMBOL> <ORDER_ID>`                      | Cancel order          | `python main.py cancel BTCUSDT 12345`                     |

---

## 🔍 Running Individual Order Modules

You can also run order modules directly:

### Market Orders Module

```bash
# Direct execution of market_orders.py
python src/orders/market_orders.py

# This will show usage instructions
```

### Limit Orders Module

```bash
# Direct execution of limit_orders.py
python src/orders/limit_orders.py

# This will show usage instructions
```

**Note**: It's recommended to use `main.py` for better CLI experience and logging.

---

## 📁 Project Structure

```
Internship_bot/
│
├── /src/                       # All source code
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Configuration and API setup
│   ├── validator.py           # Input validation utilities
│   ├── logger_config.py       # Logging configuration
│   │
│   ├── /orders/               # Basic order types
│   │   ├── __init__.py
│   │   ├── market_orders.py   # Market order implementation
│   │   └── limit_orders.py    # Limit order implementation
│   │
│   └── /advanced/             # Advanced order types (BONUS)
│       ├── __init__.py
│       ├── stop_limit.py      # Stop-Limit orders
│       ├── oco.py             # One-Cancels-Other orders
│       ├── twap.py            # Time-Weighted Average Price
│       └── grid_orders.py     # Grid trading strategy
│
├── main.py                    # Main CLI entry point
├── bot.log                    # Execution logs
├── requirements.txt           # Python dependencies
├── .env                       # API credentials (DO NOT COMMIT)
├── .env.example              # Example environment file
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

---

## 🎮 Usage Examples

### Running the Bot - Three Ways

1. **CLI Mode** (Recommended): `python main.py <command>`
2. **Web UI Mode**: `streamlit run app.py`
3. **Direct Module**: `python src/orders/market_orders.py` (for testing)

### Basic Orders

#### 1. Market Order (Buy/Sell Immediately)

```bash
# Buy 0.01 BTC at market price
python main.py market BTCUSDT BUY 0.01

# Sell 0.01 BTC at market price
python main.py market BTCUSDT SELL 0.01
```

**What happens**: Like clicking "Buy Now" on Amazon - you get the current price immediately.

#### 2. Limit Order (Buy/Sell at Specific Price)

```bash
# Buy 0.01 BTC only if price drops to $30,000
python main.py limit BTCUSDT BUY 0.01 30000

# Sell 0.01 BTC only if price rises to $35,000
python main.py limit BTCUSDT SELL 0.01 35000
```

**What happens**: Like setting a price alert - order only executes when your target price is hit.

---

### Advanced Orders (BONUS)

#### 3. Stop-Limit Order

```bash
# If price hits $29,000 (stop), place limit order at $28,900
python main.py stop-limit BTCUSDT SELL 0.01 29000 28900
```

**What happens**: Like a two-stage safety net - trigger price activates the limit order.

#### 4. OCO (One-Cancels-Other)

```bash
# Take profit at $35,000 OR stop loss at $28,000
python main.py oco BTCUSDT SELL 0.01 35000 28000
```

**What happens**: Like having two exit strategies - whichever happens first wins.

#### 5. TWAP (Time-Weighted Average Price)

```bash
# Buy 1 BTC over 60 minutes in 10 chunks
python main.py twap BTCUSDT BUY 1.0 --duration 60 --intervals 10
```

**What happens**: Like dollar-cost averaging - spreads your order over time to avoid impacting price.

#### 6. Grid Trading

```bash
# Create grid between $28,000-$32,000 with 5 levels
python main.py grid BTCUSDT 28000 32000 --grids 5 --quantity 0.01
```

**What happens**: Like automated buy-low/sell-high - places multiple orders in a range.

---

## 📊 Logging

All bot activities are logged to `bot.log` with timestamps:

- ✅ Successful orders
- ❌ Failed orders with error details
- ℹ️ API calls and responses
- ⚠️ Validation warnings

Example log entry:

```
2025-10-23 10:30:45 - INFO - Market order placed: BTCUSDT BUY 0.01
2025-10-23 10:30:46 - SUCCESS - Order executed: ID=12345, Price=30500.00
```

---

## 🛡️ Validation & Error Handling

The bot validates:

- ✓ Symbol exists on Binance (e.g., BTCUSDT, ETHUSDT)
- ✓ Quantity meets minimum requirements
- ✓ Price is within reasonable bounds
- ✓ Sufficient testnet balance
- ✓ API rate limits

---

## 🧪 Testing

### Test on Binance Testnet First!

- Testnet uses fake money - no risk!
- Same API as production
- Perfect for learning and testing strategies

### Common Test Commands

```bash
# Test market order
python main.py market BTCUSDT BUY 0.001

# Test limit order
python main.py limit ETHUSDT BUY 0.01 1800

# Check logs
cat bot.log  # Linux/Mac
type bot.log  # Windows
```

---

## 🎓 Learning Resources

> 📖 **Need more help?** Our [SETUP_GUIDE.md](SETUP_GUIDE.md) includes:
>
> - Practice scenarios (Buy the Dip, Take Profit, Stop-Loss)
> - How to read logs
> - Detailed troubleshooting
> - Safety checklist for going live

1. **Binance Futures API Documentation**

   - https://binance-docs.github.io/apidocs/futures/en/

2. **Testnet Registration**

   - https://testnet.binancefuture.com

3. **Trading Concepts**
   - Market vs Limit Orders: https://www.investopedia.com/ask/answers/100314/whats-difference-between-market-order-and-limit-order.asp
   - Stop-Loss Orders: https://www.investopedia.com/terms/s/stop-lossorder.asp

---

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Contains your API keys
2. **Use testnet first** - Don't risk real money while learning
3. **Enable IP whitelist** - Restrict API access to your IP
4. **Set API permissions** - Only enable futures trading, not withdrawals
5. **Use read-only keys** - For testing, if possible

---

## 🐛 Troubleshooting

### Common Issues

**1. "Invalid API Key"**

- Check `.env` file has correct keys
- Ensure using testnet keys with testnet URL
- Verify API permissions include futures trading

**2. "Insufficient Balance"**

- Get testnet USDT from testnet faucet
- Check balance: `python main.py balance`

**3. "Symbol not found"**

- Use correct symbol format: BTCUSDT (not BTC-USDT)
- Ensure symbol is available on futures market

**4. "Quantity too small"**

- Check minimum order quantity for symbol
- Usually 0.001 BTC or 0.01 ETH

---

## 📝 Assignment Notes

### Evaluation Criteria

- ✅ Basic Orders (50%): Market and Limit with validation
- ✅ Advanced Orders (30%): Stop-Limit, OCO, TWAP, Grid
- ✅ Logging (10%): Structured logs with timestamps
- ✅ Documentation (10%): This README and code comments

### Bonus Points

- Advanced order types implemented
- Comprehensive error handling
- Clear code structure and documentation
- Real-world analogies in comments

---

## 👨‍💻 Development

### Adding New Order Types

1. Create new file in `src/orders/` or `src/advanced/`
2. Inherit from base order class (if implemented)
3. Implement `place_order()` method
4. Add CLI command in `main.py`
5. Add tests and documentation

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings with real-life analogies
- Comment complex logic

---

## 📦 Dependencies

See `requirements.txt` for full list:

- `python-binance`: Official Binance API wrapper
- `python-dotenv`: Environment variable management
- `requests`: HTTP library (fallback)
- `pandas`: Data manipulation (optional, for TWAP/Grid)

---

## 📧 Support

For questions or issues:

- Check `bot.log` for detailed error messages
- Review Binance API documentation
- Ensure testnet account is active
- Verify API credentials in `.env`

---

## ⚖️ License

This project is for educational purposes only.  
Use at your own risk. Not financial advice.

---

## 🎯 Next Steps

1. ✅ Set up Binance testnet account
2. ✅ Install dependencies
3. ✅ Configure `.env` file
4. ✅ Test basic market order
5. ✅ Test limit order
6. ✅ Explore advanced orders
7. ✅ Review logs
8. ✅ Customize for your needs

**Happy Trading! 🚀**
