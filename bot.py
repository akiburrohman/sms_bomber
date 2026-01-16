from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from db import *
from datetime import datetime

# ========== CONFIG ==========
BOT_TOKEN = "8516622054:AAH1Zn2glzECII3j0MddxgcMZosgyxfPUcs"
ADMIN_ID = 5762886443
ADMIN_USERNAME = "@md_bro2k"

# ========== INIT ==========
init_db()

# ========== MENUS ==========
MAIN_MENU = ReplyKeyboardMarkup(
    [["📨 Send OTP"], ["📊 Statistics"], ["🔙 Back"]],
    resize_keyboard=True
)

ADMIN_MENU = ReplyKeyboardMarkup(
    [["📊 Users Stats"]],
    [["💎 Set Premium", "👤 Set Basic"]],
    [["🚫 Ban", "✅ Unban"]],
    [["♻ Reset User"]],
    [["🔙 Back"]],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    add_user(u.id, u.username)
    data = get_user(u.id)

    msg = f"👋 Welcome {u.first_name}\n\n"
    msg += f"🆔 User ID: `{data[0]}`\n"
    msg += f"👤 Username: `{data[1]}`\n"
    msg += f"🎭 Role: {data[3]}\n"
    msg += f"📨 Used OTP Today: {data[5]}\n"

    if data[3] == "premium" and data[4]:
        msg += f"💎 Premium valid until: {data[4]}\n"

    msg += f"\n💎 Premium নিতে চাইলে আপনার User ID পাঠান: {data[0]}\nAdmin: {ADMIN_USERNAME}"

    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_MENU)

async def send_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text("⚠️ Daily SMS limit reached.")
        return

    add_sms(uid)
    await update.message.reply_text(f"✅ OTP Sent! You have used {u[5]+1}/{limit} OTPs today.")

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    u = get_user(uid)

    msg = f"📊 Your Statistics\n\n"
    msg += f"🆔 `{u[0]}`\n"
    msg += f"👤 `{u[1]}`\n"
    msg += f"📞 `{u[2] if u[2] else 'N/A'}`\n"
    msg += f"🎭 {u[3]}\n"
    msg += f"📨 Used OTPs: {u[5]}\n"
    if u[3] == "premium" and u[4]:
        msg += f"💎 Premium valid until: {u[4]}\n"

    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_MENU)

# ---------- ADMIN ----------
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("🛠 Admin Panel", reply_markup=ADMIN_MENU)

async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = update.message.text
    if update.effective_user.id != ADMIN_ID:
        return

    args = t.split()
    if t.startswith("💎 Set Premium"):
        await update.message.reply_text("Use /setpremium <user_id> <days>")
    elif t.startswith("👤 Set Basic"):
        await update.message.reply_text("Use /setbasic <user_id>")
    elif t.startswith("🚫 Ban"):
        await update.message.reply_text("Use /ban <user_id>")
    elif t.startswith("✅ Unban"):
        await update.message.reply_text("Use /unban <user_id>")
    elif t.startswith("♻ Reset User"):
        await update.message.reply_text("Use /reset <user_id>")

async def setpremium(update, context):
    if update.effective_user.id != ADMIN_ID: return
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /setpremium <user_id> <days>")
        return
    uid = int(context.args[0])
    days = int(context.args[1])
    set_premium(uid, days)
    await update.message.reply_text(f"💎 User {uid} set as Premium for {days} days.")

async def setbasic(update, context):
    if update.effective_user.id != ADMIN_ID: return
    uid = int(context.args[0])
    set_basic(uid)
    await update.message.reply_text(f"👤 User {uid} set as Basic.")

async def ban(update, context):
    if update.effective_user.id != ADMIN_ID: return
    uid = int(context.args[0])
    ban_user(uid, 1)
    await update.message.reply_text(f"🚫 User {uid} banned.")

async def unban(update, context):
    if update.effective_user.id != ADMIN_ID: return
    uid = int(context.args[0])
    ban_user(uid, 0)
    await update.message.reply_text(f"✅ User {uid} unbanned.")

async def reset(update, context):
    if update.effective_user.id != ADMIN_ID: return
    uid = int(context.args[0])
    reset_user(uid)
    await update.message.reply_text(f"♻ User {uid} reset done.")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = update.message.text
    if t == "📨 Send OTP":
        await send_otp(update, context)
    elif t == "📊 Statistics":
        await statistics(update, context)
    elif t == "🔙 Back":
        await start(update, context)
    elif t in ["💎 Set Premium","👤 Set Basic","🚫 Ban","✅ Unban","♻ Reset User"]:
        await admin_action(update, context)

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
