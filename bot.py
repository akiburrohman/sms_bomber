import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)

from sender import send_exact
from config import BOT_TOKEN, MAX_PER_REQUEST

# ---------- HEALTH SERVER (Render sleep prevent) ----------
def start_health_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

    HTTPServer(("0.0.0.0", 10000), Handler).serve_forever()


# ---------- UI ----------
MAIN_MENU = ReplyKeyboardMarkup(
    [["📨 Send SMS", "❌ Cancel"]],
    resize_keyboard=True
)

CANCEL_MENU = ReplyKeyboardMarkup(
    [["❌ Cancel"]],
    resize_keyboard=True
)

RESTART_MENU = ReplyKeyboardMarkup(
    [["🔄 Re-Start"]],
    resize_keyboard=True
)


# ---------- COMMANDS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 Welcome to my bot",
        reply_markup=MAIN_MENU
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text

    if msg == "❌ Cancel":
        context.user_data.clear()
        await update.message.reply_text("❌ Cancelled", reply_markup=MAIN_MENU)
        return

    if msg == "📨 Send SMS":
        context.user_data["step"] = "number"
        await update.message.reply_text("📱 Enter your number:", reply_markup=CANCEL_MENU)
        return

    if msg == "🔄 Re-Start":
        await start(update, context)
        return

    step = context.user_data.get("step")

    if step == "number":
        context.user_data["phone"] = msg
        context.user_data["step"] = "count"
        await update.message.reply_text("🔢 How many OTP?", reply_markup=CANCEL_MENU)
        return

    if step == "count":
        try:
            count = int(msg)
            if count < 1 or count > MAX_PER_REQUEST:
                raise ValueError
        except:
            await update.message.reply_text("❌ Invalid number")
            return

        context.user_data["count"] = count
        context.user_data["step"] = "delay"
        await update.message.reply_text("⏱ Enter delay (seconds):", reply_markup=CANCEL_MENU)
        return

    if step == "delay":
        try:
            delay = float(msg)
            if delay < 0:
                raise ValueError
        except:
            await update.message.reply_text("❌ Invalid delay")
            return

        phone = context.user_data["phone"]
        count = context.user_data["count"]

        await update.message.reply_text("🚀 Sending OTPs...")

        ok, logs = send_exact(phone, count, delay)

        text = "\n".join(logs)
        text += "\n\n🎉 ALL OTP SENT" if ok else "\n\n⚠️ NOT ALL OTP SENT"

        await update.message.reply_text(text, reply_markup=RESTART_MENU)
        context.user_data.clear()


def main():
    threading.Thread(target=start_health_server, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
