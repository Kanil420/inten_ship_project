import sqlite3
import bcrypt
from datetime import datetime
from app import db 

def connect_db():
    conn = sqlite3.connect('finance_manager.db')
    return conn

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE,
                      password TEXT
                      )''')

    # Transactions table
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      amount REAL,
                      category TEXT,
                      type TEXT,  -- income or expense
                      date TEXT,
                      FOREIGN KEY(user_id) REFERENCES users(id)
                      )''')
    conn.commit()
    conn.close()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

def register_user(username, password):
    conn = db.connect_db()
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        print("Registration successful.")
    except sqlite3.IntegrityError:
        print("Username already exists.")
    finally:
        conn.close()

def login_user(username, password):
    conn = db.connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    record = cursor.fetchone()

    if record and check_password(record[0], password):
        print("Login successful.")
        return True
    else:
        print("Invalid username or password.")
        return False

if __name__ == "__main__":
    db.create_tables()
    while True:
        print("1. Register")
        print("2. Login")
        choice = input("Choose an option: ")

        if choice == '1':
            username = input("Enter username: ")
            password = input("Enter password: ")
            register_user(username, password)
        elif choice == '2':
            username = input("Enter username: ")
            password = input("Enter password: ")
            if login_user(username, password):
                break
def add_transaction(user_id, amount, category, t_type, date):
    conn = db.connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (user_id, amount, category, type, date) VALUES (?, ?, ?, ?, ?)",
                   (user_id, amount, category, t_type, date))
    conn.commit()
    conn.close()
    print(f"{t_type.capitalize()} added successfully.")

def view_transactions(user_id):
    conn = db.connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE user_id = ?", (user_id,))
    transactions = cursor.fetchall()

    for t in transactions:
        print(f"ID: {t[0]}, Amount: {t[2]}, Category: {t[3]}, Type: {t[4]}, Date: {t[5]}")
    conn.close()

if __name__ == "__main__":
    # Assuming login flow here
    logged_in = False
    user_id = None
    while True:
        if not logged_in:
            print("1. Register")
            print("2. Login")
            choice = input("Choose an option: ")

            if choice == '1':
                username = input("Enter username: ")
                password = input("Enter password: ")
                register_user(username, password)
            elif choice == '2':
                username = input("Enter username: ")
                password = input("Enter password: ")
                if login_user(username, password):
                    logged_in = True
                    # Fetch user ID from DB for future transactions
                    conn = db.connect_db()
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    user_id = cursor.fetchone()[0]
                    conn.close()

        else:
            print("1. Add Transaction")
            print("2. View Transactions")
            print("3. Logout")
            action = input("Choose an action: ")

            if action == '1':
                amount = float(input("Enter amount: "))
                category = input("Enter category: ")
                t_type = input("Enter type (income/expense): ")
                date = input("Enter date (YYYY-MM-DD): ")
                add_transaction(user_id, amount, category, t_type, date)

            elif action == '2':
                view_transactions(user_id)

            elif action == '3':
                logged_in = False
                print("Logged out.")
from datetime import datetime

def generate_report(user_id, period='monthly'):
    conn = db.connect_db()
    cursor = conn.cursor()

    if period == 'monthly':
        current_month = datetime.now().strftime("%Y-%m")
        cursor.execute("SELECT type, SUM(amount) FROM transactions WHERE user_id = ? AND date LIKE ? GROUP BY type",
                       (user_id, f'{current_month}%'))
    elif period == 'yearly':
        current_year = datetime.now().strftime("%Y")
        cursor.execute("SELECT type, SUM(amount) FROM transactions WHERE user_id = ? AND date LIKE ? GROUP BY type",
                       (user_id, f'{current_year}%'))

    report = cursor.fetchall()
    income, expense = 0, 0
    for r in report:
        if r[0] == 'income':
            income += r[1]
        else:
            expense += r[1]
    savings = income - expense
    print(f"Income: {income}, Expense: {expense}, Savings: {savings}")
    conn.close()

if __name__ == "__main__":
    # Assuming login flow here
    # Add report option in the action list
    print("4. Generate Report (monthly/yearly)")
    period = input("Enter period (monthly/yearly): ")
    generate_report(user_id, period)



if __name__ == "__main__":
    create_tables()
