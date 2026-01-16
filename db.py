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
        role TEXT DEFAULT 'basic',
        daily_limit INTEGER DEFAULT 100,
        sent_today INTEGER DEFAULT 0,
        premium_until TEXT DEFAULT NULL
    )
    """)
    con.commit()
    con.close()

def get_user(user_id, username=None):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT role, daily_limit, sent_today, premium_until FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT INTO users(user_id, username, role, daily_limit, sent_today) VALUES(?,?,?,?,0)",
                    (user_id, username, 'basic', 100))
        con.commit()
        role, limit, sent, premium_until = 'basic', 100, 0, None
    else:
        role, limit, sent, premium_until = row
        # Check if premium expired
        if premium_until:
            try:
                if datetime.strptime(premium_until, "%Y-%m-%d") < datetime.now():
                    # downgrade to basic
                    cur.execute("UPDATE users SET role='basic', daily_limit=100, premium_until=NULL WHERE user_id=?", (user_id,))
                    con.commit()
                    role, limit, premium_until = 'basic', 100, None
            except:
                pass
    con.close()
    return role, limit, sent, premium_until

def update_sent(user_id, amount):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("UPDATE users SET sent_today = sent_today + ? WHERE user_id=?", (amount, user_id))
    con.commit()
    con.close()

def set_role(user_id, role, daily_limit, premium_until=None):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT 1 FROM users WHERE user_id=?", (user_id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users(user_id, username, role, daily_limit, sent_today, premium_until) VALUES(?,?,?,?,0,?)",
                    (user_id, None, role, daily_limit, premium_until))
    else:
        cur.execute("UPDATE users SET role=?, daily_limit=?, premium_until=? WHERE user_id=?",
                    (role, daily_limit, premium_until, user_id))
    con.commit()
    con.close()

def get_premium_until(user_id):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT premium_until FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    con.close()
    return row[0] if row else None
