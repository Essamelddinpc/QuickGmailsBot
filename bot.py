import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ====== CONFIG ======
TOKEN = os.getenv("TOKEN")      # ضع توكن البوت في Environment Variable
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # ضع رقمك على تلجرام في Environment Variable

VODAFONE_NUMBER = "01030452689"
BINANCE_ID = "884732274"
SUPPORT_USERNAME = "@Quick_Gmails_Support"

PRICE_PER_GEM = 0.30
SPAM_COOLDOWN = 60  # seconds
# ====================

last_action = {}
waiting_deposit = set()

def is_spam(user_id):
    now = time.time()
    if user_id in last_action and now - last_action[user_id] < SPAM_COOLDOWN:
        return True
    last_action[user_id] = now
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user.username:
        await update.message.reply_text(
            "❌ لازم يكون عندك Username على تلجرام.\n"
            "حطه من الإعدادات وبعدين ابعت /start"
        )
        return
    await main_menu(update, context)

async def main_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("💎 شراء جميلات", callback_data="buy")],
        [InlineKeyboardButton("💰 إيداع", callback_data="deposit")],
        [InlineKeyboardButton("🆘 الدعم", callback_data="support")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("اختر من القائمة 👇", reply_markup=markup)
    else:
        await update.callback_query.message.edit_text("اختر من القائمة 👇", reply_markup=markup)

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if is_spam(user_id):
        await query.message.reply_text("⏳ برجاء الانتظار قبل المحاولة مرة أخرى.")
        return

    if query.data == "buy":
        keyboard = [
            [InlineKeyboardButton("100 جميلة", callback_data="gems_100")],
            [InlineKeyboardButton("250 جميلة", callback_data="gems_250")],
            [InlineKeyboardButton("500 جميلة", callback_data="gems_500")]
        ]
        await query.message.reply_text(
            "اختر الباقة 💎",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("gems_"):
        amount = int(query.data.split("_")[1])
        price = amount * PRICE_PER_GEM

        admin_msg = (
            f"🛒 طلب شراء جميلات\n\n"
            f"👤 @{query.from_user.username}\n"
            f"🆔 ID: {user_id}\n"
            f"💎 الكمية: {amount}\n"
            f"💵 السعر: {price}$"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg)

        await query.message.reply_text(
            f"✅ تم تسجيل طلبك\n\n"
            f"💎 الكمية: {amount}\n"
            f"💵 السعر: {price}$\n\n"
            "💰 قم بالإيداع ثم أرسل صورة التحويل."
        )

    elif query.data == "deposit":
        keyboard = [
            [InlineKeyboardButton("📱 Vodafone Cash", callback_data="vodafone")],
            [InlineKeyboardButton("💱 Binance", callback_data="binance")]
        ]
        await query.message.reply_text(
            "اختر طريقة الإيداع 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "vodafone":
        waiting_deposit.add(user_id)
        await query.message.reply_text(
            f"📱 Vodafone Cash\n"
            f"رقم التحويل: {VODAFONE_NUMBER}\n\n"
            "📸 ابعت صورة التحويل."
        )

    elif query.data == "binance":
        waiting_deposit.add(user_id)
        await query.message.reply_text(
            f"💱 Binance\n"
            f"Binance ID: {BINANCE_ID}\n\n"
            "📸 ابعت Screenshot التحويل."
        )

    elif query.data == "support":
        await query.message.reply_text(f"🆘 الدعم الفني:\n{SUPPORT_USERNAME}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in waiting_deposit:
        await update.message.reply_text("❌ لا يوجد طلب إيداع مفتوح.")
        return

    waiting_deposit.remove(user_id)

    caption = (
        f"💰 إثبات إيداع\n\n"
        f"👤 @{update.effective_user.username}\n"
        f"🆔 ID: {user_id}"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=caption
    )

    await update.message.reply_text(
        "✅ تم استلام إثبات الإيداع.\n"
        "⏱ سيتم التنفيذ قريبًا، شكرًا لثقتك."
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("Bot is running...")
app.run_polling()




