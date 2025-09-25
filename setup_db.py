import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to the database
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# --- Drop existing tables ---
cur.execute("DROP TABLE IF EXISTS accounts")
cur.execute("DROP TABLE IF EXISTS users")

# --- Create users table ---
cur.execute("""
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# --- Create accounts table ---
cur.execute("""
CREATE TABLE accounts (
    account_no SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    current_balance NUMERIC(15,2) NOT NULL DEFAULT 0,
    savings_balance NUMERIC(15,2) NOT NULL DEFAULT 0
)
""")

# --- Insert initial users ---
users = [
    ('ai_root', 'FLAG{3ll!0T}'),
    ('john_doe', 'jd123'),
    ('jane_smith', 'js456'),
    ('sqli_test1', 'pass1'),
    ('sqli_test2', 'pass2')
]

for username, password in users:
    cur.execute("""
        INSERT INTO users (username, password)
        VALUES (%s, %s)
    """, (username, password))

# --- Insert accounts for each user ---
accounts = [
    ('john_doe', 251500.50, 10000.75),
    ('jane_smith', 162000.00, 15000.00),
    ('sqli_test1', 89500.00, 2500.00),
    ('sqli_test2', 74650.00, 3000.00),
    ('ai_root', 99999999.99, 999999999.99)
]

for username, current, savings in accounts:
    cur.execute("""
        INSERT INTO accounts (user_id, current_balance, savings_balance)
        SELECT id, %s, %s FROM users WHERE username=%s
    """, (current, savings, username))

# Commit and close
conn.commit()
cur.close()
conn.close()

print("Database has been reset and initialized successfully!")
