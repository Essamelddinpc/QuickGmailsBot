import os
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

# ================== الإعدادات ==================
BOT_TOKEN = "8302444534:AAFkFP1i6K_ftbBxT2fR_Yhmsqrc_QYWvgQ"
ADMIN_ID = 2017010463  # ← حط ID الأدمن بتاعك هنا
waiting_receipt = set()
# ===============================================


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💳 إيداع", callback_data="deposit")]
    ]
    await update.message.reply_text(
        "👋 أهلاً بك\nاختر من القائمة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# الأزرار
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # زر الإيداع
    if query.data == "deposit":
        keyboard = [
            [InlineKeyboardButton("📱 Vodafone Cash", callback_data="vodafone")],
            [InlineKeyboardButton("💰 Binance", callback_data="binance")]
        ]
        await query.message.edit_text(
            "👇 اختر طريقة الإيداع:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    #
