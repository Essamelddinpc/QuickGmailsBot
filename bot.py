from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ========= الإعدادات =========
BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
ADMIN_ID = 2017010463
SUPPORT_USERNAME = "@Quick_Gmails_Support"

VODAFONE_NUMBER = "01030452689"
BINANCE_ID = "884732274"
# =============================

waiting_quantity = set()
waiting_receipt = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 شراء جميلات", callback_data="buy")],
        [InlineKeyboardButton("🆘 الدعم", url=f"https://t.me/{SUPPORT_USERNAME.replace('@','')}")]
    ]

    await update.message.reply_text(
        "👋 أهلاً بيك\nاختار من القائمة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "buy":
        waiting_quantity.add(user_id)
        await query.message.edit_text("💎 اكتب كمية الجيميلات:")

    elif query.data in ["vodafone", "binance"]:
        waiting_receipt[user_id] = query.data

        if query.data == "vodafone":
            text = (
                "📱 *Vodafone Cash*\n\n"
                f"📞 الرقم: `{VODAFONE_NUMBER}`\n\n"
                "📸 ابعت صورة تأكيد الدفع"
            )
        else:
            text = (
                "💰 *Binance*\n\n"
                f"🆔 Binance ID: `{BINANCE_ID}`\n\n"
                "📸 ابعت صورة تأكيد الدفع"
            )

        await query.message.edit_text(text, parse_mode="Markdown")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in waiting_quantity:
        quantity = update.message.text
        context.user_data["quantity"] = quantity
        waiting_quantity.remove(user_id)

        keyboard = [
            [InlineKeyboardButton("📱 Vodafone Cash", callback_data="vodafone")],
            [InlineKeyboardButton("💰 Binance", callback_data="binance")]
        ]

        await update.message.reply_text(
            f"✅ الكمية: *{quantity}*\n\nاختر طريقة الدفع:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text("❌ استخدم الأزرار فقط")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in waiting_receipt:
        await update.message.reply_text("⏳ برجاء اتباع الخطوات بالترتيب")
        return

    method = waiting_receipt[user_id]
    quantity = context.user_data.get("quantity", "غير محدد")
    username = update.message.from_user.username or "بدون يوزر"

    caption = (
        "📥 *طلب شراء جديد*\n\n"
        f"👤 المستخدم: @{username}\n"
        f"🆔 ID: {user_id}\n"
        f"💎 الكمية: {quantity}\n"
        f"💳 الطريقة: {method}"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=caption,
        parse_mode="Markdown"
    )

    await update.message.reply_text(
        "✅ تم استلام صورة التأكيد\nسيتم المراجعة والتواصل معك"
    )

    waiting_receipt.pop(user_id)
    context.user_data.clear()


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

