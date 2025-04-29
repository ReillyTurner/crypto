import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

csv_file = "/Users/reillyturner/Desktop/FailingProject/tradeData.csv"
df = pd.read_csv(csv_file)

required_columns = {"trader_wallet", "token_bought", "token_sold", "trade_value_usd", "timestamp", "tx_hash"}
if not required_columns.issubset(df.columns):
    raise ValueError("CSV file is missing required columns")

choices = ['trade_value_usd DESC', 'trade_value_usd ASC', 'timestamp DESC', 'timestamp ASC']

def update_table():
    selected_order = dropdown.get()
    sort_col, order = selected_order.split()
    ascending = (order == "ASC")
    
    num_results = entry.get()
    
    if not num_results.lstrip('-').isdigit():
        messagebox.showerror("Invalid Input", "Please enter a valid number.")
        return
    
    num_results = int(num_results)
    
    if num_results < 1:
        messagebox.showerror("Invalid Input", "Number too low. Please enter a value between 1 and 11.")
        return
    elif num_results > 11:
        messagebox.showerror("Invalid Input", "Number too large. Please enter a value between 1 and 11.")
        return
    elif num_results < 0:
        messagebox.showerror("Invalid Input", "Number cannot be negative.")
        return
    
    sorted_df = df.sort_values(by=sort_col, ascending=ascending).head(num_results)
    
    for row in table.get_children():
        table.delete(row)

    for _, row in sorted_df.iterrows():
        table.insert("", "end", values=(
            row["trader_wallet"], row["token_bought"], row["token_sold"],
            row["trade_value_usd"], row["timestamp"], row["tx_hash"]
        ))

window = tk.Tk()
window.geometry('800x500')
window.title("Crypto Trades Data Viewer")

label = tk.Label(window, text="Sort by:", anchor='center')
label.pack(pady=5)

dropdown = ttk.Combobox(window, values=choices)
dropdown.set(choices[0])
dropdown.pack(pady=5)

label_results = tk.Label(window, text="Number of results (1-11):")
label_results.pack(pady=5)

entry = tk.Entry(window)
entry.pack(pady=5)

button = tk.Button(window, text="Load Data", command=update_table)
button.pack(pady=10)

columns = ("Wallet", "Token Bought", "Token Sold", "Trade Value (USD)", "Timestamp", "Tx Hash")
table = ttk.Treeview(window, columns=columns, show="headings")

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=120)

table.pack(expand=True, fill="both")

window.mainloop()