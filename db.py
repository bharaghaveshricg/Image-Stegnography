import sqlite3
from datetime import datetime
import pandas as pd

DB_FILE = 'history.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  operation TEXT,
                  filename TEXT,
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()

def log_operation(operation, filename):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO history (operation, filename, timestamp) VALUES (?, ?, ?)",
              (operation, filename, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM history ORDER BY timestamp DESC", conn)
    conn.close()
    return df
