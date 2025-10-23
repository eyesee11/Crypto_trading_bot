# 📚 COMPLETE SETUP GUIDE - Step by Step

## 🎯 What We're Building - The Big Picture

Think of this trading bot like an **automated personal assistant** for stock trading:

- You give it instructions ("Buy Bitcoin if price drops to $28,000")
- It watches the market 24/7
- When conditions are met, it executes automatically
- Everything is logged so you can review what happened

---

## 📋 Prerequisites Checklist

Before we start, make sure you have:

- [ ] **Python 3.8 or higher installed**

  - Check: Open terminal/PowerShell and run `python --version`
  - Should show: `Python 3.8.x` or higher
  - If not: Download from [python.org](https://www.python.org/downloads/)

- [ ] **Internet connection**

  - Needed to communicate with Binance servers

- [ ] **Text editor or IDE**

  - VS Code (recommended), PyCharm, or even Notepad
  - For viewing/editing code

- [ ] **Basic Python knowledge** (optional but helpful)
  - Understand variables, functions, if/else
  - Not required - code is heavily documented

---

## 🚀 Step 1: Get Binance Testnet Account

**REAL-LIFE ANALOGY**: Like opening a demo trading account - uses fake money so you can practice without risk.

### 1.1 Register for Testnet

1. **Go to**: https://testnet.binancefuture.com
2. **Click**: "Register" or "Sign Up"
3. **Enter**: Email address (can be any email)
4. **Create**: Strong password
5. **Verify**: Email (check spam folder if needed)

**WHY TESTNET?**

- ✅ Uses fake money (no financial risk!)
- ✅ Identical to production API (same features)
- ✅ Perfect for learning and testing
- ✅ No KYC required (no ID verification)

### 1.2 Get Testnet Funds

1. **Login** to testnet account
2. **Find**: "Faucet" or "Get Test USDT" button
3. **Click** to receive test USDT (usually 10,000 USDT)
4. **Check**: Your balance shows ~10,000 USDT

**ANALOGY**: Like getting Monopoly money at the start of a game.

---

## 🔑 Step 2: Generate API Keys

**REAL-LIFE ANALOGY**: Like getting a key card to access a building - the key proves you're authorized.

### 2.1 Create API Key

1. **Login** to testnet: https://testnet.binancefuture.com
2. **Go to**: Account Settings → API Management
3. **Click**: "Create API" or "Generate New Key"
4. **Name it**: "Trading Bot" (or any name)
5. **Set permissions**:
   - ✅ Enable Reading
   - ✅ Enable Futures Trading
   - ❌ Disable Withdrawals (for safety!)
6. **Save**:
   - Copy `API Key` (long string like: `abc123xyz...`)
   - Copy `API Secret` (another long string)
   - ⚠️ **IMPORTANT**: Never share these! Like passwords!

### 2.2 (Optional but Recommended) Set IP Whitelist

1. **Find your IP**: Google "what is my IP"
2. **In API settings**: Add your IP to whitelist
3. **Why?**: Only your computer can use these keys

**SECURITY TIP**: Treat API keys like credit card numbers - never commit to GitHub, never share publicly!

---

## 💻 Step 3: Install the Bot

### 3.1 Download/Extract Project

If you received a ZIP file:

1. **Extract** to a location like:

   - Windows: `C:\Users\YourName\Desktop\Internship_bot`
   - Mac/Linux: `~/Desktop/Internship_bot`

2. **Open Terminal/PowerShell** in that folder:
   - Windows: Shift + Right-click → "Open PowerShell here"
   - Mac: Right-click → "Services" → "New Terminal at Folder"
   - Or: `cd path/to/Internship_bot`

### 3.2 Install Python Packages

**REAL-LIFE ANALOGY**: Like installing apps on your phone - we need tools to communicate with Binance.

In terminal, run:

```powershell
# Windows PowerShell
pip install -r requirements.txt
```

```bash
# Mac/Linux
pip3 install -r requirements.txt
```

**What this installs:**

- `python-binance`: Official Binance API library
- `python-dotenv`: Loads environment variables
- `pandas`, `numpy`: Data manipulation
- `colorama`, `rich`: Pretty terminal output

**Expected output:**

```
Successfully installed python-binance-1.0.19 ...
✅ All packages installed successfully
```

**If errors occur:**

- Update pip: `python -m pip install --upgrade pip`
- Try: `pip install python-binance python-dotenv requests`
- Check Python version: `python --version` (must be 3.8+)

---

## 🔧 Step 4: Configure API Credentials

### 4.1 Create .env File

**REAL-LIFE ANALOGY**: Like putting your credit card info in a digital wallet - secure storage for sensitive data.

1. **Copy** the example file:

   ```powershell
   # Windows PowerShell
   Copy-Item .env.example .env
   ```

   ```bash
   # Mac/Linux
   cp .env.example .env
   ```

2. **Open** `.env` in text editor (Notepad, VS Code, etc.)

3. **Replace** placeholders with YOUR values:

   ```env
   # Before (template):
   BINANCE_API_KEY=your_testnet_api_key_here
   BINANCE_API_SECRET=your_testnet_api_secret_here

   # After (with your actual keys):
   BINANCE_API_KEY=Nw9f6lX8sD3kJ2mP5qR7tY9zB1cV4eH6gK8lM0nQ2sU4w
   BINANCE_API_SECRET=Aa1Bb2Cc3Dd4Ee5Ff6Gg7Hh8Ii9Jj0Kk1Ll2Mm3Nn4Oo5Pp
   ```

   (These are fake examples - use YOUR keys from Step 2)

4. **Keep** other settings as-is:

   ```env
   BINANCE_TESTNET=True  # ← Keep as True for safety!
   LOG_LEVEL=INFO        # ← Controls logging detail
   ```

5. **Save** the file

### 4.2 Verify .gitignore

**IMPORTANT**: Make sure `.env` is in `.gitignore` (already done, but verify):

```gitignore
# In .gitignore file
.env  # ← Should be here
```

**WHY?**: Prevents accidentally uploading API keys to GitHub.

---

## ✅ Step 5: Test the Bot

### 5.1 Test API Connection

**REAL-LIFE ANALOGY**: Like checking if your phone has signal before making a call.

Run:

```powershell
python main.py test
```

**Expected output:**

```
==================================================================
🤖  BINANCE FUTURES TRADING BOT
==================================================================
📊 Trading on: Binance USDT-M Futures (Testnet)
💻 Mode: Command Line Interface
📝 All actions are logged to: bot.log
==================================================================

✅ Connection test successful!
📊 Account balance: 10000.00 USDT
💡 You're ready to start trading
```

**If successful**: You're all set! ✅

**If errors**:

- ❌ "Invalid API Key" → Double-check `.env` file, make sure keys are correct
- ❌ "Connection failed" → Check internet connection
- ❌ "Module not found" → Re-run `pip install -r requirements.txt`

### 5.2 Test Balance Check

```powershell
python main.py balance
```

**Expected output:**

```
💰 ACCOUNT BALANCE
==================================================
Asset: USDT
Total Balance: 10000.00000000 USDT
Available: 10000.00000000 USDT
In Orders: 0.00000000 USDT
==================================================
```

### 5.3 Test Price Fetch

```powershell
python main.py price BTCUSDT
```

**Expected output:**

```
💵 Current BTCUSDT Price: $30,500.50
```

---

## 🎮 Step 6: Place Your First Order (Safe Test)

### 6.1 Check Current BTC Price

```powershell
python main.py price BTCUSDT
```

Let's say BTC is at **$30,000**.

### 6.2 Place a LIMIT ORDER (Won't Execute Immediately)

We'll place a buy order way below market so it won't fill (safe test):

```powershell
# Try to buy at $10,000 (way below $30,000 market)
python main.py limit BTCUSDT BUY 0.001 10000
```

**What happens:**

1. Bot validates order ✓
2. Notices price is far from market
3. Places order in order book
4. Order sits waiting (won't fill because price is too low)

**Expected output:**

```
✅ LIMIT ORDER PLACED!
🆔 Order ID: 123456
📊 Symbol: BTCUSDT
💰 Limit Price: $10,000.00
📈 Status: NEW

⏳ Order will fill when market price reaches $10,000.00
```

### 6.3 Check Your Open Orders

```powershell
python main.py orders
```

**Expected output:**

```
📋 OPEN ORDERS (1 total)
================================================================================

1. Order ID: 123456
   Symbol: BTCUSDT
   Side: BUY
   Type: LIMIT
   Quantity: 0.001
   Price: $10,000.00
   Status: NEW
================================================================================
```

### 6.4 Cancel the Test Order

```powershell
python main.py cancel BTCUSDT 123456
```

(Replace `123456` with your actual order ID from step 6.3)

**Expected output:**

```
✅ Order 123456 canceled successfully
```

---

## 📖 Step 7: Understanding the Commands

Now that everything works, let's understand what you can do:

### Basic Commands

#### 1. **Market Order** (Instant execution)

```powershell
python main.py market BTCUSDT BUY 0.001
```

- **What it does**: Buys 0.001 BTC RIGHT NOW at current market price
- **Analogy**: Clicking "Buy Now" on Amazon
- **Use when**: You need to buy/sell immediately

#### 2. **Limit Order** (Wait for target price)

```powershell
python main.py limit BTCUSDT BUY 0.001 28000
```

- **What it does**: Only buys if BTC drops to $28,000
- **Analogy**: Setting a price alert "buy if price drops to $X"
- **Use when**: You want a specific price

#### 3. **Stop-Limit Order** (Conditional)

```powershell
python main.py stop-limit BTCUSDT SELL 0.001 28000 27900
```

- **What it does**: IF price drops to $28,000 (stop), THEN try to sell at $27,900 (limit)
- **Analogy**: Two-stage alarm: "If X happens, then do Y"
- **Use when**: Stop-loss, breakout trading

### Utility Commands

#### Check Balance

```powershell
python main.py balance
```

#### Get Current Price

```powershell
python main.py price BTCUSDT
```

#### List Open Orders

```powershell
python main.py orders           # All symbols
python main.py orders BTCUSDT   # Specific symbol
```

#### Cancel Order

```powershell
python main.py cancel BTCUSDT <order_id>
```

---

## 📊 Step 8: Reading the Logs

Every action is logged to `bot.log`. Let's understand it:

**Open bot.log** in text editor.

**Example log entry:**

```
2025-10-23 14:30:45 - BinanceBot - INFO - LIMIT Order: BTCUSDT BUY 0.001 | price=28000
2025-10-23 14:30:46 - BinanceBot - INFO - ✅ SUCCESS - Limit order placed | order_id=123456 | price=$28,000.00
```

**Log levels:**

- `DEBUG`: Very detailed technical info
- `INFO`: Normal operations (order placed, balance checked)
- `WARNING`: Something unusual but not critical
- `ERROR`: Something went wrong
- `SUCCESS`: Operation completed successfully

**Use logs to:**

- ✅ Verify orders were placed correctly
- ✅ Find order IDs
- ✅ Debug errors
- ✅ Audit trail (prove what you did and when)

---

## 🎓 Step 9: Practice Scenarios

### Scenario 1: Buy the Dip

**Goal**: Buy BTC if it drops 5% from current price.

1. Check current price:

   ```powershell
   python main.py price BTCUSDT
   ```

   Let's say: $30,000

2. Calculate 5% lower: $30,000 × 0.95 = $28,500

3. Place limit order:

   ```powershell
   python main.py limit BTCUSDT BUY 0.001 28500
   ```

4. Wait (check orders periodically):

   ```powershell
   python main.py orders BTCUSDT
   ```

5. If BTC drops to $28,500 → Order fills automatically! ✅

### Scenario 2: Take Profit

**Goal**: Sell at 10% profit.

1. Assume you bought at $30,000
2. Target sell price: $30,000 × 1.10 = $33,000
3. Place limit sell:
   ```powershell
   python main.py limit BTCUSDT SELL 0.001 33000
   ```
4. If BTC rises to $33,000 → Profit locked in! ✅

### Scenario 3: Stop-Loss Protection

**Goal**: Limit losses if BTC drops below $28,000.

```powershell
# If price drops to $28,000, sell at $27,900
python main.py stop-limit BTCUSDT SELL 0.001 28000 27900
```

---

## 🛡️ Safety Checklist

Before trading with real money (future):

- [ ] Tested thoroughly on testnet
- [ ] Understand all order types
- [ ] Reviewed logs after each order
- [ ] Never share API keys
- [ ] API keys have IP whitelist
- [ ] Withdrawals disabled on API keys
- [ ] Start with small amounts
- [ ] Have stop-losses in place

---

## 🐛 Troubleshooting

### Issue: "Module not found"

**Solution**:

```powershell
pip install -r requirements.txt
```

### Issue: "Invalid API Key"

**Solution**:

1. Check `.env` file has correct keys
2. No extra spaces before/after keys
3. Keys are for testnet (not production)
4. Try regenerating keys on testnet

### Issue: "Insufficient balance"

**Solution**:

1. Check balance: `python main.py balance`
2. Get more testnet USDT from faucet
3. Reduce order size (quantity)

### Issue: "Symbol not found"

**Solution**:

1. Check spelling: `BTCUSDT` not `BTC-USDT`
2. Use uppercase: `BTCUSDT` not `btcusdt`
3. Symbol must be available on Binance Futures

### Issue: "Quantity too small"

**Solution**:

1. Each symbol has minimum quantity
2. For BTC: Usually 0.001 minimum
3. Check error message for specific minimum

---

## 📚 Next Steps

1. **Practice** with different order types
2. **Review logs** after each order
3. **Experiment** with stop-limits
4. **Learn** price action and technical analysis
5. **Stay safe** - always use testnet for learning!

---

## 📞 Getting Help

If stuck:

1. Check `bot.log` for detailed errors
2. Review error messages carefully
3. Re-read relevant sections above
4. Verify .env configuration
5. Test connection: `python main.py test`

---

**🎉 Congratulations!** You've successfully set up a professional trading bot!

Remember:

- 🧪 Always test on testnet first
- 📝 Check logs regularly
- 🛡️ Never share API keys
- 💡 Start small and learn
- 📚 Understand before executing

**Happy Trading! 🚀**
