import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import requests
import json
import os #For storing API key in environment variable

# --- Config ---
ALPHAVANTAGE_API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY", "GNC82AQH5Y4T2CVA")
ALPHAVANTAGE_BASE_URL = "https://www.alphavantage.co/query"
PORTFOLIO_FILE = "portfolio.json"
portfolio = []

# --- API Call ---
def get_realtime_price(symbol):
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': ALPHAVANTAGE_API_KEY
    }
    try:
        response = requests.get(ALPHAVANTAGE_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            return float(data["Global Quote"]["05. price"])
        else:
            print(f"API Error: {data}")
            return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None

# --- File Handling ---
def save_portfolio():
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=4)

def load_portfolio():
    global portfolio
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    portfolio = json.loads(content)
                else:
                    portfolio = []
        except json.JSONDecodeError:
            print("Warning: portfolio.json is corrupted. Resetting to empty.")
            portfolio = []

# --- GUI Functions ---
def add_stock_gui():
    symbol = simpledialog.askstring("Add Stock", "Enter stock symbol:").upper()
    if not symbol:
        return
    try:
        shares = int(simpledialog.askstring("Add Stock", "Enter number of shares:"))
        purchase_price_str = simpledialog.askstring("Add Stock", "Enter purchase price (optional):")
        purchase_price = float(purchase_price_str) if purchase_price_str else None
        portfolio.append({'symbol': symbol, 'shares': shares, 'purchase_price': purchase_price})
        save_portfolio()
        messagebox.showinfo("Added", f"{shares} shares of {symbol} added.")
    except Exception:
        messagebox.showerror("Invalid Input", "Please enter valid numbers.")

def remove_stock_gui():
    symbol = simpledialog.askstring("Remove Stock", "Enter stock symbol to remove:").upper()
    if not symbol:
        return
    initial_len = len(portfolio)
    portfolio[:] = [stock for stock in portfolio if stock['symbol'] != symbol]
    save_portfolio()
    if len(portfolio) < initial_len:
        messagebox.showinfo("Removed", f"{symbol} removed from portfolio.")
    else:
        messagebox.showinfo("Not Found", f"{symbol} not found.")

def view_portfolio_gui():
    if not portfolio:
        messagebox.showinfo("Portfolio", "Your portfolio is empty.")
        return

    view_win = tk.Toplevel(root)
    view_win.title("Portfolio")
    tree = ttk.Treeview(view_win, columns=('Symbol', 'Shares', 'Current Price', 'Value', 'Profit/Loss'), show='headings')
    tree.heading('Symbol', text='Symbol')
    tree.heading('Shares', text='Shares')
    tree.heading('Current Price', text='Current Price ($)')
    tree.heading('Value', text='Current Value ($)')
    tree.heading('Profit/Loss', text='Profit/Loss ($)')
    tree.pack(expand=True, fill='both')

    total_value = 0
    for stock in portfolio:
        symbol = stock['symbol']
        shares = stock['shares']
        purchase_price = stock.get('purchase_price')
        current_price = get_realtime_price(symbol)

        if current_price is None:
            current_price = 100.0  # fallback value

        current_value = shares * current_price
        total_value += current_value
        profit_loss = (current_value - shares * purchase_price) if purchase_price else "-"
        profit_loss_str = f"{profit_loss:.2f}" if isinstance(profit_loss, float) else "-"

        tree.insert('', 'end', values=(symbol, shares, f"{current_price:.2f}", f"{current_value:.2f}", profit_loss_str))

    tk.Label(view_win, text=f"Total Portfolio Value: ${total_value:.2f}", font=("Arial", 12, "bold")).pack(pady=10)

def get_price_gui():
    symbol = simpledialog.askstring("Stock Price", "Enter stock symbol:").upper()
    if not symbol:
        return
    price = get_realtime_price(symbol)
    if price:
        messagebox.showinfo("Price", f"{symbol} current price: ${price:.2f}")
    else:
        messagebox.showerror("Error", f"Could not fetch price for {symbol}.")

# --- GUI Setup ---
root = tk.Tk()
root.title("📈 Stock Portfolio Tracker")
root.geometry("400x350")

tk.Label(root, text="Stock Portfolio Tracker", font=("Arial", 16, "bold")).pack(pady=10)

tk.Button(root, text="➕ Add Stock", command=add_stock_gui, width=25).pack(pady=5)
tk.Button(root, text="❌ Remove Stock", command=remove_stock_gui, width=25).pack(pady=5)
tk.Button(root, text="📊 View Portfolio", command=view_portfolio_gui, width=25).pack(pady=5)
tk.Button(root, text="💲 Get Stock Price", command=get_price_gui, width=25).pack(pady=5)
tk.Button(root, text="🚪 Exit", command=root.quit, width=25).pack(pady=20)

load_portfolio()
root.mainloop()