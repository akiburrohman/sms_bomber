from db import init_db, get_user, update_sent, set_role
import os
import threading
from flask import Flask
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from sender import send_exact

# ================= ADMIN =================
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

# ================= TELEGRAM UI =================
START_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("📤 Start Send SMS", callback_data="start_sms")],
    [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
])

CANCEL_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
])

RESTART_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔁 Restart", callback_data="restart")]
])

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()

    role, limit, sent = get_user(user.id, user.username)

    await update.message.reply_text(
        f"👋 Welcome {user.first_name}\n\n"
        f"🆔 Your User ID: `{user.id}`\n"
        f"👤 Role: {role}\n"
        f"📊 Daily Limit: {limit}\n\n"
        f"💎 Premium নিতে চাইলে আপনার User ID দিন:\n"
        f"{ADMIN_USERNAME}",
        reply_markup=START_MENU,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_sms":
        context.user_data.clear()
        context.user_data["step"] = "number"
        await query.message.reply_text(
            "📱 Enter Bangladeshi number (without +88):",
            reply_markup=CANCEL_MENU
        )

    elif query.data == "restart":
        context.user_data.clear()
        await query.message.reply_text(
            "🔁 Restarted",
            reply_markup=START_MENU
        )

    elif query.data == "cancel":
        context.user_data.clear()
        await query.message.reply_text(
            "❌ Cancelled",
            reply_markup=START_MENU
        )

# ================= TEXT FLOW =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    step = context.user_data.get("step")

    role, limit, sent_today = get_user(user.id, user.username)

    if role == "banned":
        await update.message.reply_text("🚫 You are banned.")
        return

    if step == "number":
        context.user_data["phone"] = text
        context.user_data["step"] = "count"
        await update.message.reply_text(
            "🔢 How many OTP to send?",
            reply_markup=CANCEL_MENU
        )
        return

    if step == "count":
        if not text.isdigit():
            await update.message.reply_text("❌ Enter valid number")
            return

        count = int(text)

        if sent_today + count > limit:
            await update.message.reply_text(
                f"⚠️ Limit exceeded\n\n"
                f"Used: {sent_today}/{limit}\n"
                f"Contact admin for premium:\n{ADMIN_USERNAME}"
            )
            context.user_data.clear()
            return

        context.user_data["count"] = count
        context.user_data["step"] = "delay"
        await update.message.reply_text(
            "⏱ Enter delay (seconds):",
            reply_markup=CANCEL_MENU
        )
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

        await update.message.reply_text(
            msg,
            reply_markup=RESTART_MENU
        )
        context.user_data.clear()

# ================= ADMIN COMMANDS =================
async def setpremium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    uid = int(context.args[0])
    set_role(uid, "premium", 100)
    await update.message.reply_text("✅ User set to PREMIUM")

async def setbasic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    uid = int(context.args[0])
    set_role(uid, "basic", 5)
    await update.message.reply_text("✅ User set to BASIC")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    uid = int(context.args[0])
    set_role(uid, "banned", 0)
    await update.message.reply_text("🚫 User BANNED")

# ================= RUN =================
def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setpremium", setpremium))
    app.add_handler(CommandHandler("setbasic", setbasic))
    app.add_handler(CommandHandler("ban", ban))

    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    app.run_polling()

# ================= MAIN =================
if __name__ == "__main__":
    init_db()

    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
