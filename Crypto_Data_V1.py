import tkinter as tk
from tkinter import ttk
from dune_client.client import DuneClient

# Initialize Dune API client
dune = DuneClient("gS0FOltRf8jkh2SzXgwgCcnygt8fObm0")

# Different sorting options for the dropdown
choices = ['trade_value_usd DESC', 'trade_value_usd ASC', 'timestamp DESC', 'timestamp ASC']

# Function to fetch and update table data
def fetch_data():
    selected_order = dropdown.get()  # Get the selected order from dropdown
    
    # Modify the query based on dropdown selection
    query = f"""
SELECT
  tx_from AS trader_wallet,
  token_bought_symbol AS token_bought,
  token_sold_symbol AS token_sold,
  amount_usd AS trade_value_usd,
  block_time AS timestamp,  -- Fixed this line
  tx_hash
FROM dex.trades
WHERE
  blockchain = 'ethereum'
  AND amount_usd > 500000
  AND block_time >= CURRENT_DATE - INTERVAL '30' DAY
ORDER BY {selected_order}
    """

    # Fetch results from Dune
    dune.run_query(4859878)  
    query_result = dune.get_latest_result(4859878)
    results = query_result.get("result", [])  # Extract the result data
    
    # Clear old data in the table
    for row in table.get_children():
        table.delete(row)

    # Insert new data
    for row in results:
        table.insert("", "end", values=(
            row["trader_wallet"], row["token_bought"], row["token_sold"],
            row["trade_value_usd"], row["timestamp"], row["tx_hash"]
        ))

# Create the main window
window = tk.Tk()
window.geometry('800x500')
window.title("Dune Analytics Viewer")

# Label
label = tk.Label(window, text="Sort by:", anchor='center')
label.pack(pady=5)

# Dropdown
dropdown = ttk.Combobox(window, values=choices)
dropdown.set(choices[0])  # Default selection
dropdown.pack(pady=5)

# Button to fetch data
button = tk.Button(window, text="Fetch Data", command=fetch_data)
button.pack(pady=10)

# Table for displaying data
columns = ("Wallet", "Token Bought", "Token Sold", "Trade Value (USD)", "Timestamp", "Tx Hash")
table = ttk.Treeview(window, columns=columns, show="headings")

# Define column headings
for col in columns:
    table.heading(col, text=col)
    table.column(col, width=120)

table.pack(expand=True, fill="both")

# Run the main event loop
window.mainloop()
