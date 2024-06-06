import sqlite3
from tkinter import *
from tkinter import messagebox, ttk

# Set up the SQLite database
conn = sqlite3.connect('expense_tracker.db')
cursor = conn.cursor()

# Create tables if they do not exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY,
    amount REAL,
    description TEXT,
    category TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY,
    category TEXT UNIQUE,
    amount REAL
)
''')
conn.commit()

# Function to add an expense
def add_expense():
    try:
        amount = float(amount_entry.get())
        description = description_entry.get()
        category = category_combobox.get()
        cursor.execute('INSERT INTO expenses (amount, description, category) VALUES (?, ?, ?)', (amount, description, category))
        conn.commit()
        messagebox.showinfo("Success", "Expense added successfully!")
        load_expenses()  # Reload the expense view
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to set a budget
def set_budget():
    try:
        category = budget_category_combobox.get()
        amount = float(budget_amount_entry.get())

        # Check if the category already exists
        cursor.execute('SELECT id FROM budgets WHERE category = ?', (category,))
        result = cursor.fetchone()

        if result:
            # If the category exists, update the amount
            cursor.execute('UPDATE budgets SET amount = ? WHERE category = ?', (amount, category))
        else:
            # If the category does not exist, insert a new record
            cursor.execute('INSERT INTO budgets (category, amount) VALUES (?, ?)', (category, amount))

        conn.commit()
        messagebox.showinfo("Success", "Budget set successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to check budgets against expenses
def check_budget():
    try:
        cursor.execute('SELECT category, SUM(amount) FROM expenses GROUP BY category')
        expenses = cursor.fetchall()
        cursor.execute('SELECT category, amount FROM budgets')
        budgets = cursor.fetchall()
        for expense in expenses:
            for budget in budgets:
                if expense[0] == budget[0] and expense[1] >= budget[1]:
                    messagebox.showwarning("Budget Alert", f"Budget exceeded for {expense[0]}!")
        root.after(60000, check_budget)  # Check every 60 seconds
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to test database connections and queries
def test_db():
    try:
        cursor.execute('SELECT * FROM expenses')
        cursor.fetchall()
        cursor.execute('SELECT * FROM budgets')
        cursor.fetchall()
        messagebox.showinfo("Success", "Database connection and queries are working!")
    except Exception as e:
        messagebox.showerror("Error", f"Database error: {e}")

# Function to load expenses into the Treeview
def load_expenses():
    for row in expense_tree.get_children():
        expense_tree.delete(row)
    cursor.execute('SELECT * FROM expenses ORDER BY date DESC')
    for row in cursor.fetchall():
        expense_tree.insert('', 'end', values=row)

# Tkinter window setup
root = Tk()
root.title("Personal Expense Tracker")

# Organize UI elements into frames
main_frame = Frame(root)
main_frame.grid(row=0, column=0, padx=10, pady=10)

expense_frame = LabelFrame(main_frame, text="Log Expense")
expense_frame.grid(row=0, column=0, padx=10, pady=10)

budget_frame = LabelFrame(main_frame, text="Set Budget")
budget_frame.grid(row=0, column=1, padx=10, pady=10)

view_frame = LabelFrame(main_frame, text="View Expenses")
view_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Expense logging form
amount_label = Label(expense_frame, text="Amount:")
amount_label.grid(row=0, column=0)
amount_entry = Entry(expense_frame)
amount_entry.grid(row=0, column=1)

description_label = Label(expense_frame, text="Description:")
description_label.grid(row=1, column=0)
description_entry = Entry(expense_frame)
description_entry.grid(row=1, column=1)

category_label = Label(expense_frame, text="Category:")
category_label.grid(row=2, column=0)
category_combobox = ttk.Combobox(expense_frame, values=["Groceries", "Utilities", "Transportation", "Entertainment"])
category_combobox.grid(row=2, column=1)

add_button = Button(expense_frame, text="Add Expense", command=add_expense)
add_button.grid(row=3, columnspan=2)

# Budget setting form
budget_label = Label(budget_frame, text="Set Budget:")
budget_label.grid(row=0, columnspan=2)

budget_category_label = Label(budget_frame, text="Category:")
budget_category_label.grid(row=1, column=0)
budget_category_combobox = ttk.Combobox(budget_frame, values=["Groceries", "Utilities", "Transportation", "Entertainment"])
budget_category_combobox.grid(row=1, column=1)

budget_amount_label = Label(budget_frame, text="Amount:")
budget_amount_label.grid(row=2, column=0)
budget_amount_entry = Entry(budget_frame)
budget_amount_entry.grid(row=2, column=1)

set_budget_button = Button(budget_frame, text="Set Budget", command=set_budget)
set_budget_button.grid(row=3, columnspan=2)

# View expenses table
columns = ('id', 'amount', 'description', 'category', 'date')
expense_tree = ttk.Treeview(view_frame, columns=columns, show='headings')
for col in columns:
    expense_tree.heading(col, text=col.capitalize())
expense_tree.grid(row=0, column=0, sticky='nsew')

# Scrollbar for the Treeview
scrollbar = ttk.Scrollbar(view_frame, orient=VERTICAL, command=expense_tree.yview)
expense_tree.configure(yscroll=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky='ns')

# Test database button
test_button = Button(root, text="Run DB Test", command=test_db)
test_button.grid(row=8, columnspan=2)

# Start periodic budget check
root.after(60000, check_budget)  # Check every 60 seconds

# Load expenses initially
load_expenses()

# Start the Tkinter main loop
root.mainloop()
