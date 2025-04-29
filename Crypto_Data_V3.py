import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

# Constants
CSV_FILE = "/Users/reillyturner/Desktop/FailingProject/tradeData.csv"
REQUIRED_COLUMNS = {"trader_wallet", "token_bought", "token_sold", "trade_value_usd", "timestamp", "tx_hash"}
SORT_CHOICES = ['trade_value_usd DESC', 'trade_value_usd ASC', 'timestamp DESC', 'timestamp ASC']
MIN_RESULTS = 1
MAX_RESULTS = 11
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
COLUMNS = ("Wallet", "Token Bought", "Token Sold", "Trade Value (USD)", "Timestamp", "Tx Hash")

# Load and validate CSV
def load_data():
    df = pd.read_csv(CSV_FILE)
    if not REQUIRED_COLUMNS.issubset(df.columns):
        raise ValueError("CSV file is missing required columns")
    return df

# Validate user input
def validate_input(value):
    if not value.lstrip('-').isdigit():
        messagebox.showerror("Invalid Input", "Please enter a valid number.")
        return None
    num = int(value)
    if num < MIN_RESULTS:
        messagebox.showerror("Invalid Input", f"Number too low. Please enter a value between {MIN_RESULTS} and {MAX_RESULTS}.")
        return None
    if num > MAX_RESULTS:
        messagebox.showerror("Invalid Input", f"Number too large. Please enter a value between {MIN_RESULTS} and {MAX_RESULTS}.")
        return None
    return num

# Update the main data table
def update_main_table(sorted_df):
    for row in table.get_children():
        table.delete(row)
    for _, row in sorted_df.iterrows():
        table.insert("", "end", values=(
            row["trader_wallet"], row["token_bought"], row["token_sold"],
            row["trade_value_usd"], row["timestamp"], row["tx_hash"]
        ))

# Update the key transaction table
def update_key_transaction(df):
    key_tx = df.loc[df['trade_value_usd'].idxmax()]
    for row in key_tx_table.get_children():
        key_tx_table.delete(row)
    key_tx_table.insert("", "end", values=(
        key_tx["trader_wallet"], key_tx["token_bought"], key_tx["token_sold"],
        key_tx["trade_value_usd"], key_tx["timestamp"], key_tx["tx_hash"]
    ))

# Main callback
def update_table():
    selected_order = dropdown.get()
    sort_col, order = selected_order.split()
    ascending = (order == "ASC")
    
    num_results = validate_input(entry.get())
    if num_results is None:
        return
    
    sorted_df = df.sort_values(by=sort_col, ascending=ascending).head(num_results)
    update_main_table(sorted_df)
    update_key_transaction(df)

# Setup GUI
def setup_gui():
    global dropdown, entry, table, key_tx_table

    window = tk.Tk()
    window.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
    window.title("Crypto Trades Data Viewer")

    # Sort dropdown
    tk.Label(window, text="Sort by:", anchor='center').pack(pady=5)
    dropdown = ttk.Combobox(window, values=SORT_CHOICES)
    dropdown.set(SORT_CHOICES[0])
    dropdown.pack(pady=5)

    # Entry field
    tk.Label(window, text=f"Number of results ({MIN_RESULTS}-{MAX_RESULTS}):").pack(pady=5)
    entry = tk.Entry(window)
    entry.pack(pady=5)

    # Button
    tk.Button(window, text="Load Data", command=update_table).pack(pady=10)

    # Main table
    table = ttk.Treeview(window, columns=COLUMNS, show="headings")
    for col in COLUMNS:
        table.heading(col, text=col)
        table.column(col, width=120)
    table.pack(expand=True, fill="both", pady=(0, 10))

    # Key transaction row
    tk.Label(window, text="Key Transaction (Highest Trade Value)", font=('Arial', 12, 'bold')).pack(pady=(5, 0))
    key_tx_table = ttk.Treeview(window, columns=COLUMNS, show="headings", height=1)
    for col in COLUMNS:
        key_tx_table.heading(col, text=col)
        key_tx_table.column(col, width=120)
    key_tx_table.pack(pady=5, fill="x")

    return window

# Run the app
df = load_data()
app = setup_gui()
app.mainloop()
