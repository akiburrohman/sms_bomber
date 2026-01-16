import sqlite3

DB = "users.db"

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        phone TEXT,
        role TEXT DEFAULT 'basic',
        premium_until TEXT,
        sms_used INTEGER DEFAULT 0,
        banned INTEGER DEFAULT 0
    )
    """)
    con.commit()
    con.close()

def add_user(uid, username):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users(user_id, username) VALUES(?,?)",
        (uid, username)
    )
    con.commit()
    con.close()

def get_user(uid):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    r = cur.fetchone()
    con.close()
    return r

def add_sms(uid):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("UPDATE users SET sms_used=sms_used+1 WHERE user_id=?", (uid,))
    con.commit()
    con.close()

def set_premium(uid, until):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute(
        "UPDATE users SET role='premium', premium_until=? WHERE user_id=?",
        (until, uid)
    )
    con.commit()
    con.close()

def set_basic(uid):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute(
        "UPDATE users SET role='basic', premium_until=NULL WHERE user_id=?",
        (uid,)
    )
    con.commit()
    con.close()

def ban_user(uid, v):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("UPDATE users SET banned=? WHERE user_id=?", (v, uid))
    con.commit()
    con.close()

def reset_user(uid):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
        UPDATE users SET sms_used=0, role='basic', premium_until=NULL
        WHERE user_id=?
    """, (uid,))
    con.commit()
    con.close()
