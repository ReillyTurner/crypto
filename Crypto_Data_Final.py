import hashlib
import json
import tkinter as tk
from tkinter import messagebox, ttk
import re

import pandas as pd

"""

The purpose of this program is to build the first component
in a multi-step plan, which would in theory allow me to track
profitable crypto traders with very little lag. 

In this first component (my program for this assessment), I 
want to access publicly available and current blockchain data,
and create a program where users can filter through that data 
to find what is most relevant. This step is what will help me 
determine which wallet(s) to track, as through my system we 
will be able to filter through transactions to find wallets 
with desirable characteristics/activity, indicating that they 
would be good to track.

"""

# Defines my constants, sets the columns, sources the CSV file, and sets the window size
CSV_FILE = "/Users/reillyturner/Desktop/FailingProject/extendedTradeData.csv"
REQUIRED_COLUMNS = {"trader_wallet", "token_bought", "token_sold", "trade_value_usd", "timestamp", "tx_hash"}
SORT_CHOICES = ['trade_value_usd DESC', 'trade_value_usd ASC', 'timestamp DESC', 'timestamp ASC']
MIN_RESULTS = 1
MAX_RESULTS = 99
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
COLUMNS = ("Wallet", "Token Bought", "Token Sold", "Trade Value (USD)", "Timestamp", "Tx Hash")
USER_DATA_FILE = "users.json"

# Loads CSV
def load_data():
    df = pd.read_csv(CSV_FILE)
    if not REQUIRED_COLUMNS.issubset(df.columns):
        raise ValueError("CSV file is missing required columns")
    return df

# Checks if input is valid
def validate_input(value):
    if not value.lstrip('-').isdigit():
        messagebox.showerror("Invalid Input", "Please enter a valid number.")
        return None
    num = int(value)
    if num < MIN_RESULTS or num > MAX_RESULTS:
        messagebox.showerror("Invalid Input", f"Enter a number between {MIN_RESULTS} and {MAX_RESULTS}.")
        return None
    return num

# Updates the main table with the sorted data
def update_main_table(sorted_df):
    for row in table.get_children():
        table.delete(row)
    for _, row in sorted_df.iterrows():
        table.insert("", "end", values=(
            row["trader_wallet"], row["token_bought"], row["token_sold"],
            row["trade_value_usd"], row["timestamp"], row["tx_hash"]
        ))

# Finds and displays the key transaction
def update_key_transaction(df):
    key_tx = df.loc[df['trade_value_usd'].idxmax()]
    for row in key_tx_table.get_children():
        key_tx_table.delete(row)
    key_tx_table.insert("", "end", values=(
        key_tx["trader_wallet"], key_tx["token_bought"], key_tx["token_sold"],
        key_tx["trade_value_usd"], key_tx["timestamp"], key_tx["tx_hash"]
    ))

# The instructions popup
def show_info_popup():
    messagebox.showinfo("Project Info", "This application allows you to filter through recent crypto transactions.\n\n"
                                        "You can sort the data, choose how many results to display (1-99), "
                                        "and it will highlight the key transaction with the highest trade value.\n\n"
                                        "This tool is built for monitoring high value trades on the Ethereum blockchain.")

# Function to sort the data based on the user specifications
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

# Function which adjusts each component in the UI based on whether the user has selected dark or light mode
def apply_theme(style, dark_mode):
    if dark_mode:
        bg, fg = "#2e2e2e", "#ffffff"
        button_bg, button_fg = "#555555", "#ffffff"  
        header_bg = "#444444"
        entry_bg, entry_fg = "#3e3e3e", "#ffffff"
        border_color = "#666666"  
    else:
        bg, fg = "#f8f8f8", "#000000"
        button_bg, button_fg = "#f0f0f0", "#000000"
        header_bg = "#e6e6e6"
        entry_bg, entry_fg = "#ffffff", "#000000"
        border_color = "#f0f0f0"

    window.configure(background=bg)
    
    style.configure("TFrame", background=bg)
    
    style.configure("Treeview",
                    background=bg,
                    foreground=fg,
                    fieldbackground=bg,
                    rowheight=25,
                    font=("Arial", 10))

    style.configure("Treeview.Heading",
                    background=header_bg,
                    foreground=fg,
                    font=("Arial", 10, "bold"))

    style.map("Treeview",
              background=[('selected', '#4a6984' if dark_mode else '#cdefff')],
              foreground=[('selected', '#ffffff' if dark_mode else '#000000')])
    
    if dark_mode:
        load_button.config(
            bg="#555555",    
            fg="#ffffff", 
            activebackground="#666666",
            activeforeground="#ffffff",
            highlightbackground="#666666",
            relief="solid",
            borderwidth=1
        )
    else:
        load_button.config(
            bg=button_bg,
            fg=button_fg, 
            activebackground=button_bg,
            activeforeground=button_fg,
            highlightbackground=border_color,
            relief="solid",
            borderwidth=1
        )
    

    for widget in window.winfo_children():
        widget_class = widget.winfo_class()
        
        if widget_class == "Label":
            widget.configure(background=bg, foreground=fg)
        
        elif widget_class == "Checkbutton":
            widget.configure(background=bg, foreground=fg, 
                            activebackground=bg, activeforeground=fg,
                            selectcolor=bg, highlightthickness=0)
        
        elif widget_class == "Button" and widget != load_button:  
            widget.configure(background=button_bg, foreground=button_fg,
                            activebackground=button_bg, activeforeground=button_fg,
                            highlightbackground=border_color, highlightthickness=0,
                            bd=1, relief="solid")
        
        elif widget_class == "Entry":
            widget.configure(background=entry_bg, foreground=entry_fg,
                            insertbackground=entry_fg, highlightthickness=0,
                            bd=1, relief="solid")
        
        elif widget_class == "Frame":
            widget.configure(background=bg, highlightthickness=0)
            for child in widget.winfo_children():
                child_class = child.winfo_class()
                if child_class == "Label":
                    child.configure(background=bg, foreground=fg)
    
    if dark_mode:
        style.map('TCombobox',
                fieldbackground=[('readonly', '#3e3e3e')],
                selectbackground=[('readonly', '#555555')],
                selectforeground=[('readonly', '#ffffff')])
        style.configure('TCombobox', background='#3e3e3e', foreground='#ffffff')
    else:
        style.map('TCombobox',
                fieldbackground=[('readonly', entry_bg)],
                selectbackground=[('readonly', button_bg)],
                selectforeground=[('readonly', button_fg)])
        style.configure('TCombobox', background=entry_bg, foreground=entry_fg)
    
    style.configure('TButton', 
                   background=button_bg, 
                   foreground=button_fg,
                   borderwidth=1,
                   relief="solid",
                   highlightthickness=0)
    
# Toggles between dark and light mode
def toggle_theme():
    dark_mode = dark_mode_var.get()
    apply_theme(style, dark_mode)
    
    window.after(10, lambda: 
        load_button.config(
            bg="#555555" if dark_mode else "#f0f0f0",
            fg="#ffffff" if dark_mode else "#000000",
            activebackground="#666666" if dark_mode else "#f0f0f0",
            activeforeground="#ffffff" if dark_mode else "#000000"
        )
    )

# Attempts to load user data from JSON file
def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Stores the user data
def save_user_data(user_data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(user_data, file)

# Secures the password by hasing it
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Function to validate user's login by comparing input and stored password
def login_user(username, password):
    user_data = load_user_data()
    if username in user_data:
        if user_data[username]["password"] == hash_password(password):
            return user_data[username]["name"]
    return None

# Validate password to ensure it meets requirements
def validate_password(password):
    # Check length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check for at least one number
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Check for at least one symbol (non-alphanumeric character)
    if not re.search(r'[^a-zA-Z0-9]', password):
        return False, "Password must contain at least one symbol"
    
    return True, ""

# Validate full name to ensure it contains at least one space
def validate_name(name):
    if ' ' not in name.strip():
        return False, "Full name must include both first and last name. "
    return True, ""

# Registers a new user, storing their full name, password, and username (assuming it is not taken)
def signup_user(username, password, name):
    # Validate password
    password_valid, password_error = validate_password(password)
    if not password_valid:
        return False, password_error
    
    # Validate name
    name_valid, name_error = validate_name(name)
    if not name_valid:
        return False, name_error
    
    user_data = load_user_data()
    if username in user_data:
        return False, "Username already taken"
    
    user_data[username] = {"password": hash_password(password), "name": name}
    save_user_data(user_data)
    return True, "Signup successful! You can now login."

# Creates the GUI login window with input fields, error/confirmation, and a buttons
def create_login_window():
    login_window = tk.Tk()
    login_window.geometry("400x320")
    login_window.title("Crypto Trades Data Viewer - Login")
    
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    x = (screen_width - 400) // 2
    y = (screen_height - 320) // 2
    login_window.geometry(f"400x320+{x}+{y}")
    
    form_frame = tk.Frame(login_window, padx=20, pady=20)
    form_frame.pack(expand=True, fill="both")
    
    title_label = tk.Label(form_frame, text="Login to Crypto Trades Viewer", font=("Arial", 14, "bold"))
    title_label.pack(pady=(0, 20))
    
    username_frame = tk.Frame(form_frame)
    username_frame.pack(fill="x", pady=5)
    
    username_label = tk.Label(username_frame, text="Username:", width=10, anchor="w")
    username_label.pack(side="left", padx=5)
    
    username_entry = tk.Entry(username_frame, borderwidth=1, relief="solid")
    username_entry.pack(side="right", expand=True, fill="x", padx=5)
    
    password_frame = tk.Frame(form_frame)
    password_frame.pack(fill="x", pady=5)
    
    password_label = tk.Label(password_frame, text="Password:", width=10, anchor="w")
    password_label.pack(side="left", padx=5)
    
    password_entry = tk.Entry(password_frame, show="*", borderwidth=1, relief="solid")
    password_entry.pack(side="right", expand=True, fill="x", padx=5)
    
    name_frame = tk.Frame(form_frame)
    name_frame.pack(fill="x", pady=5)
    
    name_label = tk.Label(name_frame, text="Full Name:", width=10, anchor="w")
    name_label.pack(side="left", padx=5)
    
    name_entry = tk.Entry(name_frame, borderwidth=1, relief="solid")
    name_entry.pack(side="right", expand=True, fill="x", padx=5)
    
    # Add password requirements info label
    req_label = tk.Label(form_frame, text="Password must have 8+ characterss, a number, and a symbol", 
                          font=("Arial", 10), fg="#f1f1f1")
    req_label.pack(pady=(0, 5))
    
    status_label = tk.Label(form_frame, text="", fg="red")
    status_label.pack(pady=5)
    
    button_frame = tk.Frame(form_frame)
    button_frame.pack(pady=10)
    
    # Checks name, username, and password, logs in the user, and opens the main window if successful
    def on_login():
        username = username_entry.get()
        password = password_entry.get()
        
        if not username or not password:
            status_label.config(text="Please enter both username and password")
            return
            
        name = login_user(username, password)
        if name:
            login_window.destroy()
            show_main_window(name)
        else:
            status_label.config(text="Invalid username or password")

    # Function to validate the user input, attempts to sing up the user, and displays an error or success message based on validation
    def on_signup():
        username = username_entry.get()
        password = password_entry.get()
        name = name_entry.get()
        
        if not username or not password or not name:
            status_label.config(text="Please fill all fields")
            return
            
        success, message = signup_user(username, password, name)
        if success:
            status_label.config(text=message, fg="green")
        else:
            status_label.config(text=message, fg="red")

    login_button = tk.Button(button_frame, text="Login", command=on_login, 
                           width=10, borderwidth=1, relief="solid")
    login_button.pack(side="left", padx=5)
    
    signup_button = tk.Button(button_frame, text="Sign Up", command=on_signup, 
                            width=10, borderwidth=1, relief="solid")
    signup_button.pack(side="left", padx=5)

    login_window.mainloop()

# Function to initialize the main GUI window and sets up all the different UI elements
def setup_gui(user_name):
    global dropdown, entry, table, key_tx_table, style, dark_mode_var, window, load_button

    window = tk.Tk()
    window.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
    window.title("Crypto Trades Data Viewer")

    style = ttk.Style(window)
    style.theme_use("default")

    dark_mode_var = tk.BooleanVar(value=False)

    user_frame = tk.Frame(window)
    user_frame.pack(fill="x", padx=10, pady=5)
    
    greeting_label = tk.Label(user_frame, text=f"Welcome, {user_name}!", font=("Arial", 12, "bold"))
    greeting_label.pack(side="left")
    
    theme_check = tk.Checkbutton(window, text="Dark Mode", variable=dark_mode_var, 
                                command=toggle_theme, borderwidth=0, highlightthickness=0)
    theme_check.pack(pady=(5, 0))

    info_button = tk.Button(window, text="ℹ️", font=("Arial", 12), 
                           command=show_info_popup, borderwidth=0, 
                           highlightthickness=0, relief="flat")
    info_button.place(x=WINDOW_WIDTH - 65, y=10)

    sort_label = tk.Label(window, text="Sort by:", anchor='center')
    sort_label.pack(pady=5)
    
    dropdown = ttk.Combobox(window, values=SORT_CHOICES, state="readonly")
    dropdown.set(SORT_CHOICES[0])
    dropdown.pack(pady=5)

    result_label = tk.Label(window, text=f"Number of results ({MIN_RESULTS}-{MAX_RESULTS}):")
    result_label.pack(pady=5)
    
    entry = tk.Entry(window, borderwidth=1, relief="solid", highlightthickness=0)
    entry.pack(pady=5)

    load_button = tk.Button(window, text="Load Data", command=update_table, 
                           borderwidth=1, relief="raised", highlightthickness=0,
                           padx=20, pady=5, font=("Arial", 10))
    load_button.pack(pady=10)

    table = ttk.Treeview(window, columns=COLUMNS, show="headings")
    for col in COLUMNS:
        table.heading(col, text=col)
        table.column(col, width=120)
    table.pack(expand=True, fill="both", pady=(0, 10))

    key_tx_label = tk.Label(window, text="Key Transaction (Highest Trade Value)", 
                          font=('Arial', 12, 'bold'))
    key_tx_label.pack(pady=(5, 0))
    
    key_tx_table = ttk.Treeview(window, columns=COLUMNS, show="headings", height=1)
    for col in COLUMNS:
        key_tx_table.heading(col, text=col)
        key_tx_table.column(col, width=120)
    key_tx_table.pack(pady=5, fill="x")
    
    apply_theme(style, dark_mode_var.get())
    
    return window

# Loads the data and sets up the main GUI
def show_main_window(user_name):
    global df
    df = load_data()
    app = setup_gui(user_name)
    app.mainloop()

if __name__ == "__main__":
    create_login_window()
