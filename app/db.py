import sqlite3

def init_db():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            income FLOAT,
            expenses FLOAT,
            goals TEXT,
            risk_tolerance TEXT
        )
    """)
    conn.commit()
    return conn

def save_user_profile(income, expenses, goals, risk_tolerance):
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (income, expenses, goals, risk_tolerance) VALUES (?, ?, ?, ?)",
        (income, expenses, goals, risk_tolerance)
    )
    conn.commit()
    conn.close()