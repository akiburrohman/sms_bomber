import sqlite3
import datetime

DB_FILE = "users.db"

def init_db():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        phone TEXT,
        role TEXT DEFAULT 'basic',
        daily_limit INTEGER DEFAULT 100,
        sent_today INTEGER DEFAULT 0,
        premium_until TEXT
    )
    """)
    con.commit()
    con.close()

def get_user(user_id, username=None):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT role, daily_limit, sent_today FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if not row:
        # add new user
        role = "basic"
        limit = 100
        cur.execute("INSERT INTO users(user_id, username, role, daily_limit, sent_today) VALUES(?,?,?,?,?)",
                    (user_id, username, role, limit, 0))
        con.commit()
        con.close()
        return role, limit, 0
    con.close()
    return row

def update_sent(user_id, count):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("UPDATE users SET sent_today = sent_today + ? WHERE user_id=?", (count, user_id))
    con.commit()
    con.close()

def set_role(user_id, role, limit=100):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("UPDATE users SET role=?, daily_limit=? WHERE user_id=?", (role, limit, user_id))
    con.commit()
    con.close()

def update_premium(user_id, days):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    premium_until = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    cur.execute("UPDATE users SET role='premium', daily_limit=50, premium_until=? WHERE user_id=?",
                (premium_until, user_id))
    con.commit()
    con.close()

def get_premium_until(user_id):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT premium_until FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    con.close()
    if row and row[0]:
        return row[0]
    return None
