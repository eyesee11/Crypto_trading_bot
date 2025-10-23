# ⚡ QUICK START - Commands to Run Right Now

This is your **copy-paste cheat sheet**. Just follow these commands in order!

---

## 🔧 Initial Setup (One-Time)

### Step 1: Install Dependencies

```powershell
# Navigate to project folder (update path for your system)
cd "c:\Users\91819\Desktop\Internship_bot"

# Install required packages
pip install -r requirements.txt
```

**Expected Output:**

```
Successfully installed python-binance-1.0.19 ...
✅ All packages installed
```

---

### Step 2: Create .env File

```powershell
# Copy the example file
Copy-Item .env.example .env

# Open .env in notepad to edit
notepad .env
```

**In .env file, replace with YOUR keys:**

```env
BINANCE_API_KEY=your_actual_api_key_from_testnet
BINANCE_API_SECRET=your_actual_api_secret_from_testnet
BINANCE_TESTNET=True
LOG_LEVEL=INFO
```

**Save and close Notepad.**

---

## ✅ Test Commands (Run These First!)

### Test 1: Check Connection

```powershell
python main.py test
```

**If you see:**

```
✅ Connection successful!
📊 Account balance: 10000.00 USDT
```

**You're good to go!** ✅

**If you see errors:**

- Double-check .env file
- Make sure API keys are correct
- Verify internet connection

---

### Test 2: Check Balance

```powershell
python main.py balance
```

**Expected:**

```
💰 ACCOUNT BALANCE
Total Balance: 10000.00000000 USDT
Available: 10000.00000000 USDT
```

---

### Test 3: Get Current BTC Price

```powershell
python main.py price BTCUSDT
```

**Expected:**

```
💵 Current BTCUSDT Price: $30,500.50
```

---

## 🎮 Your First Orders (Safe Tests)

### Test 4: Place Limit Order (Won't Fill)

```powershell
# This order is FAR below market, so it won't execute
# It's a safe test!
python main.py limit BTCUSDT BUY 0.001 10000
```

**What Happens:**

- Order placed successfully ✅
- Order sits in order book (waiting)
- Won't fill because price is too low
- Completely safe test!

**Expected Output:**

```
✅ LIMIT ORDER PLACED!
🆔 Order ID: 123456
💰 Limit Price: $10,000.00
📈 Status: NEW
```

---

### Test 5: Check Your Open Orders

```powershell
python main.py orders
```

**Expected:**

```
📋 OPEN ORDERS (1 total)
1. Order ID: 123456
   Symbol: BTCUSDT
   Side: BUY
   Price: $10,000.00
   Status: NEW
```

**You should see your test order from Test 4!**

---

### Test 6: Cancel Your Test Order

```powershell
# Replace 123456 with YOUR order ID from Test 5
python main.py cancel BTCUSDT 123456
```

**Expected:**

```
✅ Order 123456 canceled successfully
```

---

### Test 7: Verify Order is Canceled

```powershell
python main.py orders
```

**Expected:**

```
📋 No open orders
```

**Perfect!** Your test order is gone.

---

## 📚 Full Command Reference

### Utility Commands

```powershell
# Test API connection
python main.py test

# Check account balance
python main.py balance

# Get current price for any symbol
python main.py price BTCUSDT
python main.py price ETHUSDT
python main.py price ADAUSDT

# List all open orders
python main.py orders

# List open orders for specific symbol
python main.py orders BTCUSDT

# Cancel a specific order
python main.py cancel BTCUSDT <order_id>
```

---

### Basic Order Commands

#### Market Orders (Instant Execution)

```powershell
# BUY 0.001 BTC at current market price
python main.py market BTCUSDT BUY 0.001

# SELL 0.001 BTC at current market price
python main.py market BTCUSDT SELL 0.001

# Close position only (reduce-only mode)
python main.py market BTCUSDT SELL 0.001 --reduce-only
```

#### Limit Orders (Wait for Target Price)

```powershell
# BUY 0.001 BTC only if price drops to $28,000
python main.py limit BTCUSDT BUY 0.001 28000

# SELL 0.001 BTC only if price rises to $35,000
python main.py limit BTCUSDT SELL 0.001 35000

# Post-only order (maker fees, won't execute immediately)
python main.py limit BTCUSDT BUY 0.001 29900 --post-only

# Immediate-or-cancel (fill what you can now)
python main.py limit BTCUSDT BUY 0.001 30000 --time-in-force IOC

# Fill-or-kill (all or nothing)
python main.py limit BTCUSDT BUY 0.001 30000 --time-in-force FOK
```

---

### Advanced Order Commands

#### Stop-Limit Orders

```powershell
# Stop-loss: If price drops to $28,000, sell at $27,900
python main.py stop-limit BTCUSDT SELL 0.001 28000 27900

# Breakout: If price breaks $31,000, buy at $31,100
python main.py stop-limit BTCUSDT BUY 0.001 31000 31100
```

---

## 🎯 Real Trading Scenarios

### Scenario 1: Buy the Dip

```powershell
# Step 1: Check current price
python main.py price BTCUSDT
# Let's say it shows: $30,000

# Step 2: Place buy order 5% below market
python main.py limit BTCUSDT BUY 0.001 28500

# Step 3: Monitor (check periodically)
python main.py orders BTCUSDT

# If you want to cancel before it fills
python main.py cancel BTCUSDT <order_id>
```

---

### Scenario 2: Take Profit

```powershell
# Assume you bought at $30,000
# Want to sell at $33,000 for profit

# Place sell order at target
python main.py limit BTCUSDT SELL 0.001 33000

# Check status
python main.py orders BTCUSDT
```

---

### Scenario 3: Stop-Loss Protection

```powershell
# You bought BTC, want protection if it drops

# Stop-loss: Trigger at $28,000, sell at $27,900
python main.py stop-limit BTCUSDT SELL 0.001 28000 27900

# Verify order is placed
python main.py orders BTCUSDT
```

---

### Scenario 4: Full Trade Setup

```powershell
# Complete trade with entry, stop-loss, and take-profit

# Step 1: Entry - Buy at support
python main.py limit BTCUSDT BUY 0.001 29000

# Wait for entry to fill, then:

# Step 2: Set stop-loss
python main.py stop-limit BTCUSDT SELL 0.001 28000 27900

# Step 3: Set take-profit
python main.py limit BTCUSDT SELL 0.001 33000

# Step 4: Monitor all orders
python main.py orders BTCUSDT
```

---

## 📊 Checking Your Work

### View Logs

```powershell
# Windows - View last 50 lines
Get-Content bot.log -Tail 50

# Windows - View entire log
notepad bot.log

# Windows - Follow log in real-time
Get-Content bot.log -Wait -Tail 20
```

---

## 🚨 Emergency Commands

### Cancel All BTC Orders

```powershell
# First, list all BTC orders
python main.py orders BTCUSDT

# Then cancel each one individually
python main.py cancel BTCUSDT <order_id_1>
python main.py cancel BTCUSDT <order_id_2>
```

### Check Current Positions

```powershell
python main.py balance
```

---

## 💡 Pro Tips

### Tip 1: Always Check Price First

```powershell
# Before placing ANY order, check current price
python main.py price BTCUSDT
```

### Tip 2: Start Small

```powershell
# Use minimum quantities for testing
# BTC: 0.001 (about $30 at $30,000/BTC)
python main.py market BTCUSDT BUY 0.001
```

### Tip 3: Keep Logs Open

```powershell
# In one terminal: Follow logs
Get-Content bot.log -Wait -Tail 20

# In another terminal: Place orders
python main.py limit BTCUSDT BUY 0.001 28000
```

### Tip 4: Verify Before and After

```powershell
# BEFORE placing order
python main.py balance
python main.py orders BTCUSDT

# Place order here

# AFTER placing order
python main.py balance
python main.py orders BTCUSDT
```

---

## 📝 Common Command Patterns

### Pattern 1: Quick Market Buy

```powershell
python main.py price BTCUSDT  # Check price
python main.py market BTCUSDT BUY 0.001  # Buy
python main.py balance  # Verify
```

### Pattern 2: Set Limit and Wait

```powershell
python main.py limit BTCUSDT BUY 0.001 28000  # Place order
python main.py orders BTCUSDT  # Verify it's there
# ... wait ...
python main.py orders BTCUSDT  # Check if filled
```

### Pattern 3: Full Trade Management

```powershell
# Entry
python main.py limit BTCUSDT BUY 0.001 29000

# Check if filled (run periodically)
python main.py orders BTCUSDT

# Once filled, set exit orders
python main.py stop-limit BTCUSDT SELL 0.001 28000 27900  # Stop
python main.py limit BTCUSDT SELL 0.001 33000  # Target
```

---

## 🎓 Learning Path

**Day 1: Setup & Testing**

```powershell
python main.py test
python main.py balance
python main.py price BTCUSDT
```

**Day 2: Safe Order Practice**

```powershell
# Place far-away limit (won't fill)
python main.py limit BTCUSDT BUY 0.001 10000
python main.py orders
python main.py cancel BTCUSDT <order_id>
```

**Day 3: Real Limit Orders**

```powershell
# Place realistic limit orders
python main.py limit BTCUSDT BUY 0.001 29000
# Monitor and learn
```

**Day 4: Stop-Limits**

```powershell
# Practice stop-limit orders
python main.py stop-limit BTCUSDT SELL 0.001 28000 27900
```

**Day 5: Full Strategy**

```powershell
# Combine entry + stop + target
# Real trade management!
```

---

## 🔍 Troubleshooting Commands

### Check Python Version

```powershell
python --version
# Should show: Python 3.8.x or higher
```

### Reinstall Packages

```powershell
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Test Individual Modules

```powershell
# Test configuration
python src/config.py

# Test validator
python src/validator.py

# Test logger
python src/logger_config.py
```

### Verify .env File

```powershell
Get-Content .env
# Check that keys are present (don't share output!)
```

---

## 📞 Quick Help

**Issue: Command not found**

```powershell
# Make sure you're in project directory
cd "c:\Users\91819\Desktop\Internship_bot"
```

**Issue: Module not found**

```powershell
pip install -r requirements.txt
```

**Issue: Invalid API key**

```powershell
# Check .env file
notepad .env
# Verify keys are correct
```

**Issue: Order failed**

```powershell
# Check logs for details
notepad bot.log
```

---

## ✅ Success Checklist

After running these commands successfully, you should have:

- [x] Tested API connection
- [x] Checked balance
- [x] Fetched current prices
- [x] Placed a test order
- [x] Viewed open orders
- [x] Canceled the test order
- [x] Reviewed logs

**🎉 Congratulations! You're ready to trade!**

---

**Remember:**

- Always check price first
- Start with small quantities
- Review logs after each action
- Use testnet until comfortable
- Never share your API keys

**Happy Trading! 🚀**
