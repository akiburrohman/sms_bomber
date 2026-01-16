import sqlite3

def init_db():
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
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

    con.close()
    return {
        "role": row[3],
        "limit": row[4],
        "sent": row[5],
        "premium_until": row[6],
        "phone": row[2],
        "username": row[1]
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

def set_role(user_id, role, limit, premium_until=None):
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute(
        "UPDATE users SET role=?, daily_limit=?, premium_until=? WHERE user_id=?",
        (role, limit, premium_until, user_id)
    )
    con.commit()
    con.close()

def set_phone(user_id, phone):
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute("UPDATE users SET phone=? WHERE user_id=?", (phone, user_id))
    con.commit()
    con.close()

def get_all_users():
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute("SELECT user_id, username, phone, role, sent_today, daily_limit, premium_until FROM users")
    rows = cur.fetchall()
    con.close()
    return rows
