from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Needed for session management

# Helper: Connect to database
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# ========================
# Routes
# ========================

# Login page
@app.route('/', methods=['GET'])
def login_page():
    return render_template('login.html')

# Login processing
@app.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    conn = get_db_connection()
    cur = conn.cursor()

    # ⚠️ SQLi challenge: raw query
    query = f"SELECT id, username FROM users WHERE username = '{username}' AND password = '{password}'"
    print("DEBUG QUERY:", query)

    try:
        cur.execute(query)
        user = cur.fetchone()
    except Exception as e:
        print("SQL ERROR:", e)
        user = None

    cur.close()
    conn.close()

    if user:
        # Login successful
        session['user'] = {'id': user[0], 'name': user[1]}
        return redirect(url_for('dashboard'))
    else:
        # Login failed
        return render_template('login.html', error="Invalid username or password")

# Helper to fetch accounts for logged-in user
def get_user_accounts(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT account_no, current_balance, savings_balance FROM accounts WHERE user_id = %s",
            (user_id,)
        )
        accounts = [
            {
                'account_no': str(row[0])[-4:],  # Show last 4 digits
                'current_balance': row[1],
                'savings_balance': row[2]
            }
            for row in cur.fetchall()
        ]
        cur.close()
        conn.close()
        return accounts
    except Exception as e:
        print("Database error:", e)
        return []

# Dashboard page
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login_page'))

    user = session['user']
    accounts = get_user_accounts(user['id'])
    return render_template('dashboard.html', user=user, accounts=accounts)

@app.route('/dashboard/payments')
def payments():
    user = session.get('user')
    if not user:
        return redirect(url_for('login_page'))

    accounts = get_user_accounts(user['id'])

    # Only show flag to ai_root
    flag = "FLAG{3ll!0T}" if user['name'] == 'ai_root' else None

    return render_template('payments.html', user=user, accounts=accounts, flag=flag)


# Investments page
@app.route('/dashboard/investments')
def investments():
    user = session.get('user')
    if not user:
        return redirect(url_for('login_page'))

    accounts = get_user_accounts(user['id'])
    return render_template('investments.html', user=user, accounts=accounts)

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login_page'))

# Run app
if __name__ == '__main__':
    app.run(debug=True)
