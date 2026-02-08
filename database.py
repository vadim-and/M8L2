import sqlite3

def init_db():
    conn = sqlite3.connect("support.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        department TEXT,
        message TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()
def add_request(user_id, username, department, message):
    conn = sqlite3.connect("support.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO requests (user_id, username, department, message, status)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, username, department, message, "new"))
    conn.commit()
    conn.close()
