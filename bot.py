import os
import json
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================== CONFIG ==================
TOKEN = os.getenv("8302444534:AAFkFP1i6K_ftbBxT2fR_Yhmsqrc_QYWvgQ")
ADMIN_ID = 2017010463  # حط ايدي الادمن هنا
USERS_FILE = "users.json"

# ================== HELPERS ==================
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_user(uid):
    users = load_users()
    if str(uid) not in users:
        users[str(uid)] = {
            "balance": 0,
            "state": None,
            "amount": 0,
            "method": None
        }
        save_users(users)
    return users

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("💰 إيداع", callback_data="deposit")],
        [InlineKeyboardButton("💳 رصيدي", callback_data="balance")]
    ]
    await update.message.reply_text(
        "أهلاً بك 👋",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================== BUTTONS ==================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    users = get_user(uid)

    if q.data == "deposit":
        kb = [
            [InlineKeyboardButton("📱 Vodafone Cash", callback_data="pay_vodafone")],
            [InlineKeyboardButton("🪙 Binance", callback_data="pay_binance")]
        ]
        await q.message.reply_text(
            "اختر طريقة الدفع:",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif q.data.startswith("pay_"):
        method = q.data.split("_")[1]
        users[uid]["method"] = method
        users[uid]["state"] = "WAIT_AMOUNT"
        save_users(users)

        await q.message.reply_text("اكتب مبلغ الإيداع:")

    elif q.data == "balance":
        await q.message.reply_text(
            f"💳 رصيدك الحالي: {users[uid]['balance']}$"
        )

    elif q.data.startswith("deposit_approve_") or q.data.startswith("deposit_reject_"):
        if q.from_user.id != ADMIN_ID:
            return

        data = q.data.split("_")
        action = data[1]
        user_id = data[2]
        amount = float(data[3])

        users = load_users()

        if action == "approve":
            users[user_id]["balance"] += amount
            save_users(users)

            await q.message.edit_caption("✅ تم قبول الإيداع")
            await context.bot.send_message(
                chat_id=int(user_id),
                text=f"✅ تم قبول الإيداع\n💰 المبلغ: {amount}$"
            )

        else:
            await q.message.edit_caption("❌ تم رفض الإيداع")
            await context.bot.send_message(
                chat_id=int(user_id),
                text="❌ تم رفض الإيداع"
            )

# ================== TEXT ==================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    users = get_user(uid)

    if users[uid]["state"] == "WAIT_AMOUNT":
        try:
            amount = float(update.message.text)
        except:
            await update.message.reply_text("❌ اكتب رقم صحيح")
            return

        users[uid]["amount"] = amount
        users[uid]["state"] = "WAIT_IMAGE"
        save_users(users)

        if users[uid]["method"] == "vodafone":
            await update.message.reply_text(
                f"💰 المبلغ: {amount}$\n"
                f"📱 رقم فودافون: 01030452689\n"
                f"📸 ابعت صورة تأكيد الدفع"
            )
        else:
            await update.message.reply_text(
                f"💰 المبلغ: {amount}$\n"
                f"🪙 Binance ID: 884732274\n"
                f"📸 ابعت صورة تأكيد الدفع"
            )

# ================== PHOTO ==================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    users = get_user(uid)

    if users[uid]["state"] != "WAIT_IMAGE":
        return

    amount = users[uid]["amount"]
    photo = update.message.photo[-1].file_id

    kb = [
        [
            InlineKeyboardButton(
                "✅ قبول",
                callback_data=f"deposit_approve_{uid}_{amount}"
            ),
            InlineKeyboardButton(
                "❌ رفض",
                callback_data=f"deposit_reject_{uid}_{amount}"
            )
        ]
    ]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo,
        caption=(
            f"📥 طلب إيداع جديد\n"
            f"👤 ID: {uid}\n"
            f"💰 المبلغ: {amount}$"
        ),
        reply_markup=InlineKeyboardMarkup(kb)
    )

    users[uid]["state"] = None
    save_users(users)

    await update.message.reply_text("⏳ تم إرسال الطلب للإدارة")

# ================== MAIN ==================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.run_polling()

if __name__ == "__main__":
    main()


