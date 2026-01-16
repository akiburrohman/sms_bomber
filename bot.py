from db import init_db, get_user, update_sent, set_role
ADMIN_ID = 5762886443  # তোমার telegram numeric ID
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

BOT_TOKEN = "8516622054:AAH1Zn2glzECII3j0MddxgcMZosgyxfPUcs"

# ================= FLASK =================
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is alive"


def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)


# ================= TELEGRAM BOT =================
START_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("📤 Start Bombing SMS", callback_data="start_sms")],
    [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
])

CANCEL_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
])

RESTART_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔁 Restart Bombing", callback_data="restart")]
])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 Welcome to my akib sms bombing bot",
        reply_markup=START_MENU
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_sms":
        context.user_data.clear()
        context.user_data["step"] = "number"
        await query.message.reply_text(
            "📱 Enter your number only Bangladeshi number:",
            reply_markup=CANCEL_MENU
        )

    elif query.data == "restart":
        context.user_data.clear()
        await query.message.reply_text(
            "👋 Welcome to my akib sms bomber bot",
            reply_markup=START_MENU
        )

    elif query.data == "cancel":
        context.user_data.clear()
        await query.message.reply_text(
            "❌ Cancelled",
            reply_markup=START_MENU
        )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    step = context.user_data.get("step")

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

        context.user_data["count"] = int(text)
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

        msg = "\n".join(logs)
        msg += "\n\n✅ DONE" if ok else "\n\n⚠️ SOME FAILED"

        await update.message.reply_text(
            msg,
            reply_markup=RESTART_MENU
        )
        context.user_data.clear()


def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.run_polling()


# ================= MAIN =================
if __name__ == "__main__":
    # Flask in background thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Telegram bot MUST be main thread
    run_bot()



