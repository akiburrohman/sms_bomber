import os
import threading
import sqlite3
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
    [InlineKeyboardButton("🛠 Admin Panel", callback_data="admin_panel")]
])

CANCEL_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
])

RESTART_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔁 Restart", callback_data="restart")]
])

BACK_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("⬅️ Back", callback_data="back")]
])

# ================= START COMMAND =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()

    role, limit, sent = get_user(user.id, user.username)
    remaining = max(limit - sent, 0)
    premium_until = get_premium_until(user.id)

    # HTMLV1 escape for Telegram
    def escape_md1(text):
        return str(text).replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

    user_id_md = escape_md1(user.id)
    first_name_md = escape_md1(user.first_name)
    role_md = escape_md1(role)
    limit_md = escape_md1(limit)
    sent_md = escape_md1(sent)
    remaining_md = escape_md1(remaining)
    premium_text = escape_md1(premium_until) if role == "premium" and premium_until else ""

    msg = f"👋 Welcome to AKIB BOMBER {first_name_md}\n\n"
    msg += f"🆔 Your User ID: <code>{user_id_md}</code>\n"
    msg += f"👤 Role: {role_md}\n"
    msg += f"📊 Daily Limit: {limit_md}\n"
    msg += f"📤 Used Today: {sent_md}\n"
    msg += f"🟢 Remaining: {remaining_md}\n"
    if premium_text:
        msg += f"💎 Premium valid until: <code>{premium_text}</code>\n"
    msg += f"\n💎 Premium নিতে চাইলে আপনার User ID দিন:\n{ADMIN_USERNAME}"

    await update.message.reply_text(msg, reply_markup=START_MENU, parse_mode="HTML")

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

    elif data == "back":
        context.user_data.clear()
        await query.message.reply_text("⬅️ Back", reply_markup=START_MENU)

    elif data == "admin_panel":
        if user.id != ADMIN_ID:
            await query.message.reply_text("🚫 You are not admin!")
            return
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

        def escape_md1(text):
        return str(text).replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

        msg = "📊 Users Stats:\n\n"
        for r in rows:
            uid, uname, phone, role, sent, limit, premium_until = r
            uname_md = escape_md1(uname) if uname else "N/A"
            uid_md = escape_md1(uid)
            phone_md = escape_md1(phone) if phone else "N/A"
            role_md = escape_md1(role)
            sent_md = escape_md1(sent)
            limit_md = escape_md1(limit)
            premium_md = escape_md1(premium_until) if premium_until else "N/A"
            msg += f"ID:<code>{uid_md}</code> | Username:<code>{uname_md}</code> | Phone:<code>{phone_md}</code> | Role:<code>{role_md}<code> | Sent:<code>{sent_md}/{limit_md}</code> | Premium Until:<code>{premium_md}</code>\n"

        await query.message.reply_text(msg, parse_mode="HTML")

    elif data in ["set_premium", "set_basic", "ban_user", "unban_user", "reset_user"] and user.id == ADMIN_ID:
        context.user_data["admin_action"] = data
        prompts = {
            "set_premium": "💎 Send the USER ID to make Premium (also set duration in days):",
            "set_basic": "👤 Send the USER ID to make Basic:",
            "ban_user": "🚫 Send the USER ID to Ban:",
            "unban_user": "✅ Send the USER ID to Unban:",
            "reset_user": "🔄 Send the USER ID to reset usage:"
        }
        await query.message.reply_text(prompts[data], reply_markup=BACK_MENU)

# ================= TEXT HANDLER =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    step = context.user_data.get("step")
    admin_action = context.user_data.get("admin_action")

    # ----------------- Admin actions -----------------
    if user.id == ADMIN_ID and admin_action:
        if not text.isdigit():
            await update.message.reply_text("❌ Enter valid numeric USER ID")
            return
        uid = int(text)
        if admin_action == "set_premium":
            context.user_data["admin_uid"] = uid
            context.user_data["step"] = "premium_duration"
            await update.message.reply_text("⏱ Enter premium duration in days:", reply_markup=BACK_MENU)
        elif admin_action == "set_basic":
            set_role(uid, "basic", 100)
            await update.message.reply_text(f"✅ User {uid} set to BASIC (100 OTP/day)")
            context.user_data.pop("admin_action", None)
        elif admin_action == "ban_user":
            set_role(uid, "banned", 0)
            await update.message.reply_text(f"🚫 User {uid} BANNED")
            context.user_data.pop("admin_action", None)
        elif admin_action == "unban_user":
            set_role(uid, "basic", 100)
            await update.message.reply_text(f"✅ User {uid} UNBANNED & set to BASIC")
            context.user_data.pop("admin_action", None)
        elif admin_action == "reset_user":
            con = sqlite3.connect("users.db")
            cur = con.cursor()
            cur.execute("UPDATE users SET sent_today=0 WHERE user_id=?", (uid,))
            con.commit()
            con.close()
            await update.message.reply_text(f"🔄 User {uid} usage RESET")
            context.user_data.pop("admin_action", None)
        return

    if step == "premium_duration":
        if not text.isdigit():
            await update.message.reply_text("❌ Enter valid number of days")
            return
        days = int(text)
        uid = context.user_data.get("admin_uid")
        update_premium(uid, days)
        await update.message.reply_text(f"💎 Premium for User {uid} set for {days} days")
        context.user_data.pop("admin_uid", None)
        context.user_data.pop("admin_action", None)
        context.user_data.pop("step", None)
        return

    # ----------------- User OTP flow -----------------
    if step == "number":
        context.user_data["phone"] = text
        context.user_data["step"] = "count"
        await update.message.reply_text("🔢 How many OTP to send?", reply_markup=CANCEL_MENU)
        return

    if step == "count":
        if not text.isdigit():
            await update.message.reply_text("❌ Enter valid number")
            return
        count = int(text)
        role, limit, sent = get_user(user.id, user.username)

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
            update_sent(user.id, count)
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



