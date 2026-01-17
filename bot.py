from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)
import json
import os

# ========= إعدادات =========
BOT_TOKEN = "8302444534:AAFkFP1i6K_ftbBxT2fR_Yhmsqrc_QYWvgQ"
ADMIN_ID = 2017010463

VODAFONE = "01030452689"
BINANCE = "884732274"

PRICE = 0.30
USERS_FILE = "users.json"
GMAIL_FILE = "gmails.txt"
# ===========================

# ---------- ملفات ----------
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(GMAIL_FILE):
    open(GMAIL_FILE, "w").close()

def load_users():
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_gmails():
    with open(GMAIL_FILE) as f:
        return [x.strip() for x in f if x.strip()]

def save_gmails(data):
    with open(GMAIL_FILE, "w") as f:
        f.write("\n".join(data))

# ---------- Start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    users = load_users()

    if uid not in users:
        users[uid] = {"balance": 0}
        save_users(users)

    kb = [
        [InlineKeyboardButton("💼 رصيدي", callback_data="balance")],
        [InlineKeyboardButton("➕ إيداع", callback_data="deposit")],
        [InlineKeyboardButton("🛒 شراء جميلات", callback_data="buy")]
    ]

    await update.message.reply_text(
        "👋 أهلاً بيك\nاختار من القائمة:",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ---------- أزرار ----------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    users = load_users()

    if q.data == "balance":
        await q.message.edit_text(f"💼 رصيدك الحالي: {users[uid]['balance']}$")

    elif q.data == "deposit":
        kb = [
            [InlineKeyboardButton("📱 Vodafone Cash", callback_data="dep_voda")],
            [InlineKeyboardButton("💰 Binance", callback_data="dep_binance")]
        ]
        await q.message.edit_text("اختر طريقة الإيداع:", reply_markup=InlineKeyboardMarkup(kb))

    elif q.data.startswith("dep_"):
        context.user_data["deposit_method"] = q.data
        context.user_data["waiting_amount"] = True

        await q.message.edit_text("✍️ اكتب مبلغ الإيداع بالدولار:")

    elif q.data == "buy":
        context.user_data["buying"] = True
        await q.message.edit_text("✍️ اكتب كمية الجيميلات:")

    elif q.data.startswith("approve_") or q.data.startswith("reject_"):
        if q.from_user.id != ADMIN_ID:
            await q.answer("❌ غير مسموح", show_alert=True)
            return

        _, action, uid, amount = q.data.split("_")
        users = load_users()

        if action == "approve":
            users[uid]["balance"] += float(amount)
            save_users(users)

            await q.message.edit_text("✅ تم قبول الإيداع")
            await context.bot.send_message(int(uid), f"✅ تم إضافة {amount}$ إلى رصيدك")
        else:
            await q.message.edit_text("❌ تم رفض الإيداع")
            await context.bot.send_message(int(uid), "❌ تم رفض الإيداع")

# ---------- نص ----------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)

    if context.user_data.get("waiting_amount"):
        try:
            amount = float(update.message.text)
            if amount <= 0:
                raise ValueError
        except:
            await update.message.reply_text("❌ اكتب مبلغ صحيح")
            return

        context.user_data["deposit_amount"] = amount
        context.user_data["waiting_amount"] = False
        context.user_data["waiting_receipt"] = True

        method = context.user_data["deposit_method"]
        number = VODAFONE if method == "dep_voda" else BINANCE

        await update.message.reply_text(
            f"💳 بيانات الدفع\n\n{number}\n\n📸 ابعت صورة تأكيد الدفع"
        )

        return

    if context.user_data.get("buying"):
        users = load_users()
        try:
            qty = int(update.message.text)
            if qty <= 0:
                raise ValueError
        except:
            await update.message.reply_text("❌ رقم غير صحيح")
            return

        total = round(qty * PRICE, 2)
        gmails = load_gmails()

        if users[uid]["balance"] < total:
            await update.message.reply_text("❌ رصيدك غير كافي")
            context.user_data.clear()
            return

        if len(gmails) < qty:
            await update.message.reply_text("❌ الكمية غير متوفرة")
            context.user_data.clear()
            return

        users[uid]["balance"] -= total
        save_users(users)

        send = gmails[:qty]
        save_gmails(gmails[qty:])

        await update.message.reply_text(
            "✅ تم الشراء بنجاح\n\n" + "\n".join(send)
        )

        context.user_data.clear()

# ---------- صورة ----------
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_receipt"):
        return

    uid = str(update.message.from_user.id)
    amount = context.user_data["deposit_amount"]

    kb = [[
        InlineKeyboardButton("✅ قبول", callback_data=f"deposit_approve_{uid}_{amount}"),
        InlineKeyboardButton("❌ رفض", callback_data=f"deposit_reject_{uid}_{amount}")
    ]]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"📥 طلب إيداع\n🆔 المستخدم: {uid}\n💵 المبلغ: {amount}$",
        reply_markup=InlineKeyboardMarkup(kb)
    )

    await update.message.reply_text("⏳ تم إرسال الإيصال للمراجعة")
    context.user_data.clear()

# ---------- تشغيل ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
