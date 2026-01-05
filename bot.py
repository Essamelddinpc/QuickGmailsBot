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

    # اختيار طريقة الدفع
    elif query.data in ["vodafone", "binance"]:
        waiting_receipt.add(user_id)

        method = "Vodafone Cash" if query.data == "vodafone" else "Binance"

        await query.message.edit_text(
            f"✅ تم اختيار *{method}*\n\n"
            "📸 من فضلك ابعت *صورة تأكيد التحويل*",
            parse_mode="Markdown"
        )


# استقبال الصور
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in waiting_receipt:
        await update.message.reply_text(
            "⏳ برجاء الانتظار قبل المحاولة مرة أخرى"
        )
        return

    photo = update.message.photo[-1]
    username = update.message.from_user.username or "بدون يوزر"

    caption = (
        "📥 *طلب إيداع جديد*\n\n"
        f"👤 المستخدم: @{username}\n"
        f"🆔 ID: {user_id}"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo.file_id,
        caption=caption,
        parse_mode="Markdown"
    )

    await update.message.reply_text(
        "✅ تم استلام صورة التأكيد\nسيتم المراجعة في أقرب وقت"
    )

    waiting_receipt.remove(user_id)


# أي رسالة نصية
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ الرجاء استخدام الأزرار فقط"
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
