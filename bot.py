from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)
from datetime import datetime, timedelta
from db import *

# ========= CONFIG =========
BOT_TOKEN = "8516622054:AAH1Zn2glzECII3j0MddxgcMZosgyxfPUcs"
ADMIN_ID = 5762886443
# ==========================

init_db()

MAIN_MENU = ReplyKeyboardMarkup(
    [["📨 Send SMS"], ["📊 Statistics"], ["🔙 Back"]],
    resize_keyboard=True
)

ADMIN_MENU = ReplyKeyboardMarkup(
    [["👤 User Stat"]],
    [["⭐ Set Premium", "🔁 Set Basic"]],
    [["🚫 Ban", "✅ Unban"]],
    [["♻ Reset User"]],
    [["🔙 Back"]],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    add_user(u.id, u.username)

    data = get_user(u.id)

    msg = "👋 *Welcome*\n\n"
    msg += "🆔 User ID: `" + str(u.id) + "`\n"
    msg += "👤 Username: `" + str(u.username) + "`\n"
    msg += "🎭 Role: *" + data[3].upper() + "*\n"

    if data[3] == "premium" and data[4]:
        msg += "⏳ Valid Until: *" + data[4] + "*\n"

    await update.message.reply_text(
        msg,
        parse_mode="Markdown",
        reply_markup=MAIN_MENU
    )

async def send_sms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    u = get_user(uid)

    if u[6] == 1:
        await update.message.reply_text("🚫 You are banned.")
        return

    limit = 30
    if u[3] == "premium":
        limit = 50
    if uid == ADMIN_ID:
        limit = 999999

    if u[5] >= limit:
        await update.message.reply_text("⚠ SMS limit reached.")
        return

    add_sms(uid)
    await update.message.reply_text("✅ SMS sent successfully!")

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)

    msg = "📊 *Your Statistics*\n\n"
    msg += "🆔 `" + str(u[0]) + "`\n"
    msg += "👤 `" + str(u[1]) + "`\n"
    msg += "📞 `" + str(u[2]) + "`\n"
    msg += "🎭 *" + u[3] + "*\n"
    msg += "📨 SMS Used: *" + str(u[5]) + "*\n"

    if u[3] == "premium" and u[4]:
        msg += "⏳ Valid Until: *" + u[4] + "*\n"

    await update.message.reply_text(
        msg,
        parse_mode="Markdown",
        reply_markup=MAIN_MENU
    )

# ---------- ADMIN ----------
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("🛠 Admin Panel", reply_markup=ADMIN_MENU)

async def setpremium(update, context):
    if update.effective_user.id != ADMIN_ID: return
    uid = int(context.args[0])
    days = int(context.args[1])
    until = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    set_premium(uid, until)
    await update.message.reply_text("⭐ Premium set!")

async def setbasic(update, context):
    if update.effective_user.id != ADMIN_ID: return
    set_basic(int(context.args[0]))
    await update.message.reply_text("🔁 Set to basic.")

async def ban(update, context):
    if update.effective_user.id != ADMIN_ID: return
    ban_user(int(context.args[0]), 1)
    await update.message.reply_text("🚫 User banned.")

async def unban(update, context):
    if update.effective_user.id != ADMIN_ID: return
    ban_user(int(context.args[0]), 0)
    await update.message.reply_text("✅ User unbanned.")

async def reset(update, context):
    if update.effective_user.id != ADMIN_ID: return
    reset_user(int(context.args[0]))
    await update.message.reply_text("♻ User reset done.")

async def text_handler(update, context):
    t = update.message.text

    if t == "📨 Send SMS":
        await send_sms(update, context)
    elif t == "📊 Statistics":
        await statistics(update, context)
    elif t == "🔙 Back":
        await start(update, context)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("setpremium", setpremium))
    app.add_handler(CommandHandler("setbasic", setbasic))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    app.run_polling()

main()
