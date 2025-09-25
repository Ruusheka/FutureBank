import psycopg2, os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

username = 'ai_root'
password = 'FLAG{SQLI_MASTER}'

# Safe version using parameterized query
cur.execute("SELECT id, username FROM users WHERE username=%s AND password=%s", (username, password))
user = cur.fetchone()
print(user)  # Should print: (id, 'ai_root')

cur.close()
conn.close()
