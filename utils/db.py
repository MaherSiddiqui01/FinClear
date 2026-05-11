import sqlite3

conn = sqlite3.connect("finance.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS logs(
id INTEGER PRIMARY KEY AUTOINCREMENT,
client TEXT,
email TEXT,
amount REAL,
status TEXT
)
""")

conn.commit()

def save_log(client,email,amount,status):
    cur.execute(
        "INSERT INTO logs(client,email,amount,status) VALUES(?,?,?,?)",
        (client,email,amount,status)
    )
    conn.commit()