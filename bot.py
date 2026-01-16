import os
import threading
import sqlite3
from datetime import datetime, timedelta
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from sender import send_exact
from db import init_db, get_user, update_sent, set_role, update_premium, get_premium_until

# ================= ADMIN CONFIG =================
ADMIN_ID = 5762886443
ADMIN_USERNAME = "@md_bro2k"
BOT_TOKEN = "8516622054:AAH1Zn2glzECII3j0MddxgcMZosgyxfPUcs"

# ================= FLASK (KEEP ALIVE) =================
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is alive"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# ================= TELEGRAM BUTTONS =================
START_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("📤 Start Send SMS", callback_data="start_sms")],
    [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    [InlineKeyboardButton("🛠 Admin Panel", callback_data="admin_panel")]
])

CANCEL_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
])

RESTART_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔁 Restart", callback_data="restart")]
])

# ================= ESCAPE FUNCTION FOR MONOSPACE =================
def escape_md(text: str) -> str:
    escape_chars = "_*[]()~`>#+-=|{}.! "
    return "".join(f"\\{c}" if c in escape_chars else c for c in str(text))

# ================= START COMMAND =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()

    role, limit, sent, premium_until, phone = get_user(user.id, user.username)
    remaining = max(limit - sent, 0)
    premium_text = premium_until if premium_until else "N/A"

    msg = (
        f"👋 Welcome to AKIB BOMBER {escape_md(user.first_name)}\n\n"
        f"🆔 Your User ID: `{user.id}`\n"
        f"👤 Username: `{escape_md(user.username) if user.username else 'N/A'}`\n"
        f"📱 Phone: `{phone if phone else 'N/A'}`\n"
        f"👤 Role: `{role}`\n"
        f"📊 Daily Limit: `{limit}`\n"
        f"📤 Used Today: `{sent}`\n"
        f"🟢 Remaining: `{remaining}`\n"
        f"💎 Premium Until: `{premium_text}`\n\n"
        f"💎 Premium নিতে চাইলে আপনার User ID দিন:\n"
        f"{ADMIN_USERNAME}"
    )

    await update.message.reply_text(
        msg,
        reply_markup=START_MENU,
        parse_mode="Markdown"
    )

# ================= BUTTON HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = update.effective_user

    if data == "start_sms":
        context.user_data.clear()
        context.user_data["step"] = "number"
        await query.message.reply_text("📱 Enter Bangladeshi number (without +88):", reply_markup=CANCEL_MENU)

    elif data == "restart":
        context.user_data.clear()
        await query.message.reply_text("🔁 Restarted", reply_markup=START_MENU)

    elif data == "cancel":
        context.user_data.clear()
        await query.message.reply_text("❌ Cancelled", reply_markup=START_MENU)

    elif data == "admin_panel":
        if user.id != ADMIN_ID:
            await query.message.reply_text("🚫 You are not admin!")
            return
        # Admin panel buttons
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Users Stats", callback_data="stats")],
            [InlineKeyboardButton("💎 Set Premium", callback_data="set_premium")],
            [InlineKeyboardButton("👤 Set Basic", callback_data="set_basic")],
            [InlineKeyboardButton("🚫 Ban User", callback_data="ban_user")],
            [InlineKeyboardButton("✅ Unban User", callback_data="unban_user")],
            [InlineKeyboardButton("🔄 Reset User Usage", callback_data="reset_user")],
            [InlineKeyboardButton("❌ Close", callback_data="close_admin")]
        ])
        await query.message.reply_text("🛠 Admin Panel", reply_markup=markup)

    elif data == "close_admin":
        await query.message.reply_text("❌ Admin Panel Closed", reply_markup=START_MENU)

    elif data == "stats" and user.id == ADMIN_ID:
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        cur.execute("SELECT user_id, username, phone, role, sent_today, daily_limit, premium_until FROM users")
        rows = cur.fetchall()
        con.close()

        msg = "📊 Users Stats:\n\n"
        for r in rows:
            uid = r[0]
            uname = r[1] if r[1] else "N/A"
            phone = r[2] if r[2] else "N/A"
            role = r[3]
            sent = r[4]
            limit = r[5]
            premium_until = r[6] if r[6] else "N/A"

            msg += (
                f"ID: `{uid}` | Username: `{escape_md(uname)}` | Phone: `{phone}` | "
                f"Role: `{role}` | Sent: `{sent}/{limit}` | Premium Until: `{premium_until}`\n"
            )
        await query.message.reply_text(msg, parse_mode="Markdown")

    # Admin actions buttons
    elif data == "set_premium" and user.id == ADMIN_ID:
        context.user_data["admin_action"] = "premium"
        await query.message.reply_text("💎 Send the USER ID and number of days (like `123456 30`) to make Premium:")

    elif data == "set_basic" and user.id == ADMIN_ID:
        context.user_data["admin_action"] = "basic"
        await query.message.reply_text("👤 Send the USER ID to make Basic:")

    elif data == "ban_user" and user.id == ADMIN_ID:
        context.user_data["admin_action"] = "ban"
        await query.message.reply_text("🚫 Send the USER ID to Ban:")

    elif data == "unban_user" and user.id == ADMIN_ID:
        context.user_data["admin_action"] = "unban"
        await query.message.reply_text("✅ Send the USER ID to Unban:")

    elif data == "reset_user" and user.id == ADMIN_ID:
        context.user_data["admin_action"] = "reset"
        await query.message.reply_text("🔄 Send the USER ID to reset usage:")

# ================= TEXT HANDLER =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    step = context.user_data.get("step")
    admin_action = context.user_data.get("admin_action")

    # ----------------- Admin actions -----------------
    if user.id == ADMIN_ID and admin_action:
        if admin_action == "premium":
            parts = text.split()
            if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                await update.message.reply_text("❌ Send like `USERID DAYS` (example: 123456 30)")
                return
            uid, days = int(parts[0]), int(parts[1])
            update_premium(uid, days)
            await update.message.reply_text(f"✅ User `{uid}` PREMIUM set for `{days}` days")
        elif admin_action == "basic":
            if not text.isdigit():
                await update.message.reply_text("❌ Enter valid numeric USER ID")
                return
            uid = int(text)
            set_role(uid, "basic", 100)
            await update.message.reply_text(f"✅ User `{uid}` set to BASIC")
        elif admin_action == "ban":
            if not text.isdigit():
                await update.message.reply_text("❌ Enter valid numeric USER ID")
                return
            uid = int(text)
            set_role(uid, "banned", 0)
            await update.message.reply_text(f"🚫 User `{uid}` BANNED")
        elif admin_action == "unban":
            if not text.isdigit():
                await update.message.reply_text("❌ Enter valid numeric USER ID")
                return
            uid = int(text)
            set_role(uid, "basic", 100)
            await update.message.reply_text(f"✅ User `{uid}` UNBANNED & set to BASIC")
        elif admin_action == "reset":
            if not text.isdigit():
                await update.message.reply_text("❌ Enter valid numeric USER ID")
                return
            uid = int(text)
            con = sqlite3.connect("users.db")
            cur = con.cursor()
            cur.execute("UPDATE users SET sent_today=0 WHERE user_id=?", (uid,))
            con.commit()
            con.close()
            await update.message.reply_text(f"🔄 User `{uid}` usage RESET")
        context.user_data.pop("admin_action", None)
        return

    # ----------------- User OTP flow -----------------
    if step == "number":
        context.user_data["phone"] = text
        context.user_data["step"] = "count"
        await update.message.reply_text(f"🔢 How many OTP to send? (Basic max 30 / Premium max 50)", reply_markup=CANCEL_MENU)
        return

    if step == "count":
        if not text.isdigit():
            await update.message.reply_text("❌ Enter valid number")
            return
        count = int(text)
        role, limit, sent, premium_until, phone = get_user(user.id, user.username)

        # ----------------- SESSION MAX LIMIT -----------------
        if role == "basic" and count > 30:
            await update.message.reply_text("⚠️ Basic user can send max 30 OTP per session")
            return
        elif role == "premium" and count > 50:
            await update.message.reply_text("⚠️ Premium user can send max 50 OTP per session")
            return

        if sent + count > limit:
            await update.message.reply_text(f"⚠️ Daily limit exceeded\nUsed: {sent}/{limit}\nContact admin for premium: {ADMIN_USERNAME}")
            context.user_data.clear()
            return

        context.user_data["count"] = count
        context.user_data["step"] = "delay"
        await update.message.reply_text("⏱ Enter delay (seconds):", reply_markup=CANCEL_MENU)
        return

    if step == "delay":
        try:
            delay = float(text)
        except:
            await update.message.reply_text("❌ Enter valid seconds")
            return
        phone = context.user_data["phone"]
        count = context.user_data["count"]
        await update.message.reply_text("🚀 Sending OTPs...")
        ok, logs = send_exact(phone, count, delay)
        if ok:
            update_sent(user.id, count)  # DB update
        msg = "\n".join(logs)
        msg += "\n\n✅ DONE" if ok else "\n\n⚠️ SOME FAILED"
        await update.message.reply_text(msg, reply_markup=RESTART_MENU)
        context.user_data.clear()

# ================= RUN BOT =================
def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.run_polling()

# ================= MAIN =================
if __name__ == "__main__":
    init_db()
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
