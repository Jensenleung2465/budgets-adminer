from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

# Generate a new Fernet key if not exists
def get_fernet_key():
    key_file = 'fernet_key.key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as file:
            return file.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as file:
            file.write(key)
        return key

# Load the Fernet key
fernet_key = get_fernet_key()

# Function to encrypt and decrypt data
def encrypt_data(data):
    f = Fernet(fernet_key)
    return f.encrypt(data.encode())

def decrypt_data(data):
    f = Fernet(fernet_key)
    return f.decrypt(data).decode()

# Create the database and necessary tables
def setup_database():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    password TEXT)''')
    
    # Create expenses table
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    amount BLOB,
                    category TEXT,
                    date TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    # Create income table
    c.execute('''CREATE TABLE IF NOT EXISTS income (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    amount BLOB,
                    source TEXT,
                    date TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    # Create debts table
    c.execute('''CREATE TABLE IF NOT EXISTS debts (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    amount BLOB,
                    creditor TEXT,
                    due_date TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()

setup_database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    user_id = 1  # Example user_id for testing
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    
    # Fetch total expenses
    c.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (user_id,))
    total_expenses = c.fetchone()[0] or 0

    # Fetch total income
    c.execute("SELECT SUM(amount) FROM income WHERE user_id=?", (user_id,))
    total_income = c.fetchone()[0] or 0

    # Fetch total debts
    c.execute("SELECT SUM(amount) FROM debts WHERE user_id=?", (user_id,))
    total_debts = c.fetchone()[0] or 0

    conn.close()
    
    return render_template('dashboard.html', total_expenses=total_expenses, total_income=total_income, total_debts=total_debts)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']
        
        encrypted_amount = encrypt_data(amount)
        encrypted_category = encrypt_data(category)

        user_id = 1  # Example user_id for testing
        
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
                  (user_id, encrypted_amount, encrypted_category, date))
        conn.commit()
        conn.close()
        
        return redirect(url_for('dashboard'))
    
    return render_template('add_expense.html')

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        amount = request.form['amount']
        source = request.form['source']
        date = request.form['date']
        
        encrypted_amount = encrypt_data(amount)
        encrypted_source = encrypt_data(source)

        user_id = 1  # Example user_id for testing
        
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("INSERT INTO income (user_id, amount, source, date) VALUES (?, ?, ?, ?)",
                  (user_id, encrypted_amount, encrypted_source, date))
        conn.commit()
        conn.close()
        
        return redirect(url_for('dashboard'))
    
    return render_template('add_income.html')

@app.route('/add_debt', methods=['GET', 'POST'])
def add_debt():
    if request.method == 'POST':
        amount = request.form['amount']
        creditor = request.form['creditor']
        due_date = request.form['due_date']
        
        encrypted_amount = encrypt_data(amount)
        encrypted_creditor = encrypt_data(creditor)

        user_id = 1  # Example user_id for testing
        
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("INSERT INTO debts (user_id, amount, creditor, due_date) VALUES (?, ?, ?, ?)",
                  (user_id, encrypted_amount, encrypted_creditor, due_date))
        conn.commit()
        conn.close()
        
        return redirect(url_for('dashboard'))
    
    return render_template('add_debt.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1487)