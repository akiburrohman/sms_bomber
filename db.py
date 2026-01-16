import sqlite3
from datetime import datetime, timedelta

DB_FILE = "users.db"

def init_db():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        phone TEXT,
        role TEXT DEFAULT 'basic',
        sent_today INTEGER DEFAULT 0,
        daily_limit INTEGER DEFAULT 100,
        premium_until TEXT
    )
    """)
    con.commit()
    con.close()

def get_user(user_id, username=None):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT user_id, username, phone, role, sent_today, daily_limit, premium_until FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if row:
        con.close()
        premium_until = row[6]
        return row[3], row[5], row[4], premium_until, row[2]
    else:
        # new user insert
        cur.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        con.commit()
        con.close()
        return "basic", 100, 0, None, None

def update_sent(user_id, count):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("UPDATE users SET sent_today = sent_today + ? WHERE user_id=?", (count, user_id))
    con.commit()
    con.close()

def set_role(user_id, role, limit):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("UPDATE users SET role=?, daily_limit=? WHERE user_id=?", (role, limit, user_id))
    con.commit()
    con.close()

# ========== PREMIUM FUNCTIONS ==========
def update_premium(user_id, days):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT premium_until FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    now = datetime.now()
    if row and row[0]:
        old = datetime.fromisoformat(row[0])
        if old > now:
            new_until = old + timedelta(days=days)
        else:
            new_until = now + timedelta(days=days)
    else:
        new_until = now + timedelta(days=days)
    cur.execute("UPDATE users SET role='premium', daily_limit=1000, premium_until=? WHERE user_id=?", (new_until.isoformat(), user_id))
    con.commit()
    con.close()

def get_premium_until(user_id):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT premium_until FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    con.close()
    return row[0] if row else None
