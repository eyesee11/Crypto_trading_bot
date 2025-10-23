# 🌐 WEB UI GUIDE - Streamlit Interface Tour

## 🎯 What is the Web UI?

The **Streamlit Web Interface** is a visual, browser-based alternative to the command-line interface.
**Same bot, same features, different interface!**

---

## 📋 Prerequisites

Before starting, make sure you've completed the basic setup:

- [x] Python 3.8+ installed
- [x] Dependencies installed (`pip install -r requirements.txt`)
- [x] `.env` file configured with API keys
- [x] Binance Testnet account active

> 💡 **Haven't done basic setup?** Follow [SETUP_GUIDE.md](SETUP_GUIDE.md) first!

---

## 🚀 Step 1: Launch the Web UI

### 1.1 Activate Virtual Environment (if using one)

**Windows:**

```powershell
.venv\Scripts\activate
```

**Mac/Linux:**

```bash
source .venv/bin/activate
```

### 1.2 Start Streamlit Server

```bash
streamlit run app.py
```

**Expected Output:**

```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.1.x:8501
```

### 1.3 Open Browser

- **Automatically**: Browser should open automatically
- **Manually**: Navigate to `http://localhost:8501`

> 📧 **First Time?** Streamlit may ask for your email - you can **press Enter to skip**.

---

## 🎨 Interface Overview

When the app loads, you'll see:

### **Header**

```
BINANCE FUTURES BOT
CONNECTED | TESTNET
```

### **Sidebar (Left)**

- Navigation menu
- Account balance
- Quick prices (BTC, ETH)

### **Main Area (Center)**

- Current page content
- Forms and buttons
- Charts and data

---

## 🗺️ Feature Tour - Follow This Order

### **TOUR STEP 1: Dashboard** 🏠

**What you'll see:**

- Account overview (BALANCE, AVAILABLE, LOCKED)
- Market prices for popular pairs (BTC, ETH, BNB, ADA)
- Open orders table

**What to do:**

1. ✅ Check your testnet balance (should show ~10,000 USDT)
2. ✅ Note the current BTC price
3. ✅ Confirm "CONNECTED | TESTNET" shows at top

**Why this matters:**

- Confirms API connection works
- Shows your starting balance
- Gives you current market prices for reference

---

### **TOUR STEP 2: Market Order** 🛒

**Navigation:** Click "MARKET ORDER" in sidebar

**What you'll see:**

- Form with: PAIR, QTY, SIDE, REDUCE ONLY
- Estimated cost calculator
- EXECUTE button

**Practice Exercise:**

1. **Select pair**: BTCUSDT (from dropdown)
2. **Enter quantity**: 0.001 (very small amount)
3. **Select side**: BUY
4. **Check estimated cost**: Should show ~$30 (0.001 BTC × $30,000)
5. **Click EXECUTE**

**What happens:**

```
EXECUTING...
✓ ORDER EXECUTED | ID: 123456789
```

**What you learned:**

- ✅ Market orders execute instantly
- ✅ You bought 0.001 BTC at current market price
- ✅ Order ID is displayed for tracking

**Analogy:** Like clicking "Buy Now" on Amazon - instant purchase at current price.

---

### **TOUR STEP 3: View Your Order** 📋

**Navigation:** Click "OPEN ORDERS" in sidebar

**What you'll see:**

- Table with columns: Order ID, Symbol, Type, Side, Quantity, Price, Status, Time
- Filter dropdown (All Symbols / BTCUSDT / etc.)
- REFRESH button

**What to do:**

1. ✅ Look for your market order (may show as FILLED already)
2. ✅ Note the Order ID matches what was shown
3. ✅ Check Status (likely "FILLED" for market orders)

**If order filled instantly:**

- It won't appear here (filled orders are closed)
- Check Dashboard → you'll see reduced available balance
- This is normal for market orders!

**What you learned:**

- ✅ Open orders are "waiting" orders
- ✅ Market orders usually fill instantly (so they disappear)
- ✅ Limit orders stay visible until filled or canceled

---

### **TOUR STEP 4: Limit Order** 🎯

**Navigation:** Click "LIMIT ORDER" in sidebar

**What you'll see:**

- PAIR, QTY, SIDE, LIMIT PRICE fields
- Current market price display
- % difference calculator
- ADVANCED options expander

**Practice Exercise - Safe Test:**

**Current BTC price:** ~$30,000 (check from dashboard)

**We'll place a buy order BELOW market** (won't fill immediately):

1. **Select pair**: BTCUSDT
2. **Enter quantity**: 0.001
3. **Select side**: BUY
4. **Enter limit price**: 25000 (well below market)
5. **Check the alert**: Should show "X% BELOW MARKET" in green ✓
6. **Click PLACE ORDER**

**What happens:**

```
PLACING...
✓ ORDER PLACED | ID: 987654321
TARGET: $25,000.00
```

**What you learned:**

- ✅ Limit orders wait for target price
- ✅ Order stays open until price reaches $25,000
- ✅ You can set precise entry prices

**Analogy:** Like setting a price alert - "only buy if BTC drops to $25k"

---

### **TOUR STEP 5: Manage Open Order** ❌

**Navigation:** Stay on "OPEN ORDERS" or click it again

**What you'll see:**

- Your limit order from Step 4 in the table
- Status: "NEW" (waiting for price)

**Practice Exercise - Cancel Order:**

1. **Scroll down** to "CANCEL ORDER" section
2. **Select symbol**: BTCUSDT
3. **Select order ID**: 987654321 (your order from Step 4)
4. **Click CANCEL**

**What happens:**

```
✓ ORDER 987654321 CANCELED
```

Table refreshes → order disappears

**What you learned:**

- ✅ How to cancel pending orders
- ✅ Only "NEW" orders can be canceled
- ✅ FILLED orders are permanent (already executed)

---

### **TOUR STEP 6: Stop-Limit Order** 🛡️

**Navigation:** Click "STOP-LIMIT" in sidebar

**What you'll see:**

- PAIR, QTY, SIDE fields
- STOP PRICE (trigger)
- LIMIT PRICE (execution)
- FLOW diagram showing: CURRENT → TRIGGER → EXECUTE

**Understanding Stop-Limit:**
Two-stage order:

1. **When price hits STOP PRICE** → Order activates
2. **Then tries to fill at LIMIT PRICE**

**Practice Exercise - Stop-Loss:**

**Scenario:** You own BTC at $30,000 and want to limit losses

**Current BTC price:** $30,000

1. **Select pair**: BTCUSDT
2. **Enter quantity**: 0.001
3. **Select side**: SELL (to exit position)
4. **Stop price**: 29000 (trigger if drops to $29k)
5. **Limit price**: 28900 (sell at $28.9k after trigger)
6. **Check FLOW diagram**:
   - CURRENT: $30,000
   - TRIGGER: $29,000 (-3.33%)
   - EXECUTE: $28,900 (-3.67%)

**For now:** DON'T click PLACE ORDER (this is just practice)

**What you learned:**

- ✅ Stop-limit protects against losses
- ✅ Two prices: when to activate (stop) + where to execute (limit)
- ✅ Common for risk management

**Analogy:** Like car insurance - "if accident happens (stop), pay me this much (limit)"

---

### **TOUR STEP 7: Price Charts** 📈

**Navigation:** Click "CHARTS" in sidebar

**What you'll see:**

- Pair selector dropdown
- Interactive candlestick chart (15-minute intervals)
- Price, time, open, high, low, close data

**What to do:**

1. **Select BTCUSDT** (or any pair)
2. **Hover over candles** to see exact prices
3. **Zoom in/out** using chart controls
4. **Switch pairs** to compare (ETH, BNB, ADA)

**What you learned:**

- ✅ Visual price history
- ✅ Identify trends (up/down/sideways)
- ✅ Better timing for limit orders

**Analogy:** Like checking weather patterns before planning a trip

---

### **TOUR STEP 8: Help Section** 📚

**Navigation:** Click "HELP" in sidebar

**What you'll see:**

- Quick start guide
- Order type definitions
- Important notes
- Documentation links
- Troubleshooting tips

**What to do:**

1. ✅ Bookmark this page for reference
2. ✅ Read through order types if unclear
3. ✅ Check "NOTES" section for safety reminders

---

## 🎮 Advanced Features

### **Advanced Options in Limit Orders**

Click "ADVANCED" expander to reveal:

#### **1. TIME IN FORCE**

- **GTC (Good Till Canceled)**: Order stays until filled or manually canceled
- **IOC (Immediate or Cancel)**: Fill now or cancel (partial fills allowed)
- **FOK (Fill or Kill)**: Fill entire order now or cancel (no partial fills)

**When to use:**

- GTC: Normal limit orders (most common)
- IOC: Want to fill quickly, ok with partial
- FOK: All-or-nothing orders

#### **2. POST ONLY**

- ☑️ Checked: Guarantees "maker" order (lower fees)
- ☐ Unchecked: Can be "taker" (higher fees)

**When to use:**

- Check for lower fees
- Uncheck if you need immediate fill

#### **3. REDUCE ONLY**

- ☑️ Checked: Can only close existing positions (not open new)
- ☐ Unchecked: Can open new positions

**When to use:**

- Check when taking profit or cutting losses
- Prevents accidentally increasing position

---

## 📊 Sidebar Quick Actions

The sidebar always shows:

### **Account Balance**

```
BALANCE: $9,970.00
```

Updates after each order

### **Quick Prices**

```
BTC: $30,500.00
ETH: $1,850.00
```

Refreshes when you change pages

**Pro Tip:** Use sidebar to monitor while placing orders in main area

---

## 🔄 Workflow Recommendations

### **For Day Trading:**

1. Open CHARTS → Identify trend
2. Open DASHBOARD → Check balance
3. Place LIMIT ORDER → Wait for entry
4. Monitor OPEN ORDERS → Confirm fill
5. Place STOP-LIMIT → Protect profit/loss

### **For Quick Trades:**

1. Check DASHBOARD → Current price
2. Place MARKET ORDER → Instant execution
3. Check DASHBOARD → Confirm new balance

### **For Position Management:**

1. Open ORDERS → See all active orders
2. Use CHARTS → Check price action
3. CANCEL or modify as needed

---

## ⚡ Keyboard Shortcuts & Tips

### **Browser Navigation:**

- **F5** or **Ctrl+R**: Refresh page (reconnects to API)
- **Ctrl+Shift+R**: Hard refresh (clears cache)
- **Ctrl+Click**: Open link in new tab

### **Streamlit Tips:**

- **Auto-refresh**: Page updates automatically on interactions
- **Back button**: Use sidebar navigation (not browser back)
- **Multiple tabs**: You can open multiple tabs to same UI
- **Mobile friendly**: Works on phones/tablets

---

## 🛡️ Safety Best Practices

### **Always Check:**

1. ✅ "TESTNET" shows in header (green)
2. ✅ Quantity is correct (0.001 not 1.0!)
3. ✅ Price makes sense (not 10x too high/low)
4. ✅ Side is correct (BUY vs SELL)

### **Before Placing Orders:**

1. Check current price on DASHBOARD
2. Verify you have enough balance
3. For limit orders: confirm % difference
4. For stop-limits: verify FLOW makes sense

### **After Placing Orders:**

1. Note the Order ID (in case you need to cancel)
2. Check OPEN ORDERS to confirm
3. Monitor CHARTS for price movement
4. Set stop-losses for protection

---

## 🐛 Troubleshooting

### **Issue: "CONNECTION FAILED"**

**Solutions:**

1. Check `.env` file has correct API keys
2. Verify internet connection
3. Restart Streamlit: `Ctrl+C` then `streamlit run app.py`
4. Check Binance Testnet is online: https://testnet.binancefuture.com

### **Issue: "ORDER FAILED"**

**Solutions:**

1. Check error message in red box
2. Verify sufficient balance (DASHBOARD → AVAILABLE)
3. Check minimum quantity (usually 0.001 BTC)
4. Review `bot.log` for detailed error

### **Issue: Orders Not Showing**

**Solutions:**

1. Click REFRESH button
2. Check filter dropdown (should be "All Symbols" or specific symbol)
3. Market orders may have filled instantly (check balance changed)
4. Hard refresh browser: `Ctrl+Shift+R`

### **Issue: Page Won't Load**

**Solutions:**

1. Check terminal for errors
2. Ensure Streamlit is running (`streamlit run app.py`)
3. Try different browser (Chrome, Firefox, Edge)
4. Check port 8501 isn't blocked by firewall

### **Issue: Can't Cancel Order**

**Solutions:**

1. Order may have already filled (check status)
2. Only "NEW" status orders can be canceled
3. Verify correct Order ID selected
4. Refresh and try again

---

## 📝 Practice Checklist

Complete this to master the Web UI:

- [ ] Launched Web UI successfully
- [ ] Viewed Dashboard and confirmed balance
- [ ] Placed a market order (tiny amount!)
- [ ] Placed a limit order below market (won't fill)
- [ ] Viewed the order in OPEN ORDERS
- [ ] Canceled the limit order
- [ ] Checked price charts for BTC and ETH
- [ ] Explored STOP-LIMIT form (didn't place)
- [ ] Tested ADVANCED options in limit orders
- [ ] Read HELP section
- [ ] Checked logs (`bot.log`) for order history

---

## 🎓 Next Steps

After completing this tour:

1. **Practice More:**

   - Place small limit orders at different prices
   - Try all TIME IN FORCE options
   - Experiment with POST ONLY

2. **Learn Strategy:**

   - Read [TRADING_CONCEPTS.md](TRADING_CONCEPTS.md)
   - Study candlestick patterns
   - Practice risk management

3. **Explore CLI:**

   - Try [SETUP_GUIDE.md](SETUP_GUIDE.md) for CLI version
   - Compare speed: CLI vs Web UI
   - Learn scripting with CLI

4. **Go Deeper:**
   - Study Binance API docs
   - Learn technical analysis
   - Understand order book mechanics

---

## 🔄 Switching Between CLI and Web UI

**Both can run simultaneously!**

**Terminal 1:**

```bash
streamlit run app.py
# Web UI at http://localhost:8501
```

**Terminal 2:**

```bash
python main.py balance
python main.py orders
# CLI commands work independently
```

**They share:**

- ✅ Same `.env` configuration
- ✅ Same `bot.log` file
- ✅ Same Binance account
- ✅ Same orders (placed from either interface)

---

## 📞 Getting Help

If you get stuck:

1. **Check Logs:**

   ```bash
   # View recent logs
   tail -n 50 bot.log  # Mac/Linux
   Get-Content bot.log -Tail 50  # Windows PowerShell
   ```

2. **Test Connection:**

   ```bash
   python main.py test
   ```

3. **Restart Everything:**

   - Stop Streamlit (`Ctrl+C`)
   - Close browser
   - Run `streamlit run app.py` again

4. **Review Documentation:**
   - [SETUP_GUIDE.md](SETUP_GUIDE.md) - Initial setup
   - [QUICK_START.md](QUICK_START.md) - Command reference
   - [TRADING_CONCEPTS.md](TRADING_CONCEPTS.md) - Trading basics

---

## 🎉 Congratulations!

You've completed the Web UI tour! You now know how to:

- ✅ Navigate the interface
- ✅ Place all order types
- ✅ Manage open orders
- ✅ Read price charts
- ✅ Use advanced options
- ✅ Troubleshoot issues

**Remember:**

- 🧪 This is TESTNET (fake money)
- 📝 All actions are logged
- 🛡️ Always use stop-losses
- 📚 Keep learning!

**Happy Trading! 🚀**

---

_Last Updated: October 2025_
_For CLI version, see [SETUP_GUIDE.md](SETUP_GUIDE.md)_
