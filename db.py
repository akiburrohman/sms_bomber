import sqlite3
from datetime import date, datetime, timedelta

DB = "users.db"

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        role TEXT DEFAULT 'basic',
        daily_limit INTEGER DEFAULT 5,
        sent_today INTEGER DEFAULT 0,
        last_date TEXT
    )
    """)
    con.commit()
    con.close()

def get_user(user_id, username):
    """Return role, daily_limit, sent_today and reset if new BD day"""
    today = str(bd_today())
    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    if not row:
        # New user
        cur.execute(
            "INSERT INTO users (user_id, username, last_date) VALUES (?,?,?)",
            (user_id, username, today)
        )
        con.commit()
        role, limit, sent = "basic", 5, 0
    else:
        role, limit, sent, last = row[2], row[3], row[4], row[5]
        if last != today:
            # Reset daily usage if new BD day
            cur.execute(
                "UPDATE users SET sent_today=0, last_date=? WHERE user_id=?",
                (today, user_id)
            )
            con.commit()
            sent = 0

    con.close()
    return role, limit, sent

def update_sent(user_id, count):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute(
        "UPDATE users SET sent_today = sent_today + ? WHERE user_id=?",
        (count, user_id)
    )
    con.commit()
    con.close()

def set_role(user_id, role, limit):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute(
        "UPDATE users SET role=?, daily_limit=? WHERE user_id=?",
        (role, limit, user_id)
    )
    con.commit()
    con.close()

def bd_today():
    """Return current date in Bangladesh timezone (UTC+6)"""
    now_utc = datetime.utcnow()
    now_bd = now_utc + timedelta(hours=6)
    return now_bd.date()
