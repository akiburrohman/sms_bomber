import sqlite3
from datetime import datetime

def init_db():
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        phone TEXT,
        role TEXT DEFAULT 'basic',
        daily_limit INTEGER DEFAULT 30,
        sent_today INTEGER DEFAULT 0,
        premium_until TEXT,
        banned INTEGER DEFAULT 0
    )
    """)
    con.commit()
    con.close()

def get_user(user_id, username=None):
    con = sqlite3.connect("users.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    if not row:
        cur.execute(
            "INSERT INTO users (user_id, username) VALUES (?,?)",
            (user_id, username)
        )
        con.commit()
        cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()

    # ---- AUTO PREMIUM EXPIRE ----
    role, limit, premium_until = row[3], row[4], row[6]
    if role == "premium" and premium_until:
        if datetime.now().date() > datetime.strptime(premium_until, "%Y-%m-%d").date():
            cur.execute("""
                UPDATE users
                SET role='basic', daily_limit=30, premium_until=NULL
                WHERE user_id=?
            """, (user_id,))
            con.commit()
            role = "basic"
            limit = 30
            premium_until = None

    con.close()
    return {
        "role": role,
        "limit": limit,
        "sent": row[5],
        "premium_until": premium_until,
        "phone": row[2],
        "username": row[1],
        "banned": bool(row[7])
    }

def update_sent(user_id, count):
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute(
        "UPDATE users SET sent_today = sent_today + ? WHERE user_id=?",
        (count, user_id)
    )
    con.commit()
    con.close()

def reset_daily():
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute("UPDATE users SET sent_today = 0")
    con.commit()
    con.close()

def set_premium(user_id, days):
    until = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute("""
        UPDATE users
        SET role='premium', daily_limit=50, premium_until=?
        WHERE user_id=?
    """, (until, user_id))
    con.commit()
    con.close()

def set_phone(user_id, phone):
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute("UPDATE users SET phone=? WHERE user_id=?", (phone, user_id))
    con.commit()
    con.close()

def ban_user(user_id):
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute("UPDATE users SET banned=1 WHERE user_id=?", (user_id,))
    con.commit()
    con.close()

def unban_user(user_id):
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute("UPDATE users SET banned=0 WHERE user_id=?", (user_id,))
    con.commit()
    con.close()

def get_all_users():
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute("""
        SELECT user_id, username, phone, role,
        sent_today, daily_limit, premium_until, banned
        FROM users
    """)
    rows = cur.fetchall()
    con.close()
    return rows
