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

# ---------- MENUS ----------
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


# ---------- COMMANDS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 Welcome to my bot",
        reply_markup=START_MENU
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_sms":
        context.user_data.clear()
        context.user_data["step"] = "number"
        await query.message.reply_text(
            "📱 Enter your number:",
            reply_markup=CANCEL_MENU
        )

    elif query.data == "restart":
        context.user_data.clear()
        await query.message.reply_text(
            "👋 Welcome to my bot",
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

    # ---- STEP 1: NUMBER ----
    if step == "number":
        context.user_data["phone"] = text
        context.user_data["step"] = "count"

        await update.message.reply_text(
            "🔢 How many OTP to send?",
            reply_markup=CANCEL_MENU
        )
        return

    # ---- STEP 2: COUNT ----
    if step == "count":
        if not text.isdigit():
            await update.message.reply_text("❌ Enter a valid number")
            return

        context.user_data["count"] = int(text)
        context.user_data["step"] = "delay"

        await update.message.reply_text(
            "⏱ Enter delay (seconds):",
            reply_markup=CANCEL_MENU
        )
        return

    # ---- STEP 3: DELAY ----
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

        result_text = "\n".join(logs)

        if ok:
            result_text += "\n\n🎉 RESULT: ALL OTP SENT SUCCESSFULLY"
        else:
            result_text += "\n\n⚠️ RESULT: SOME OTP FAILED"

        await update.message.reply_text(
            result_text,
            reply_markup=RESTART_MENU
        )

        context.user_data.clear()


# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
