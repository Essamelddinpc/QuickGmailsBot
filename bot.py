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
BOT_TOKEN = "8302444534:AAFkFP1i6K_ftbBxT2fR_Yhmsqrc_QYWvgQ"
ADMIN_ID = 2017010463
SUPPORT_USERNAME = "@Quick_Gmails_Support"

VODAFONE_NUMBER = "01030452689"
BINANCE_ID = "884732274"

PRICE_PER_GMAIL = 0.30
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
        await query.message.edit_text("💎 اكتب كمية الجيميلات اللي عايزها:")

    elif query.data in ["vodafone", "binance"]:
        waiting_receipt[user_id] = query.data

        quantity = context.user_data.get("quantity", 0)
        total_price = context.user_data.get("total_price", 0)

        if query.data == "vodafone":
            text = (
                "📱 *Vodafone Cash*\n\n"
                f"💎 الكمية: *{quantity}*\n"
                f"💵 السعر: *${total_price}*\n\n"
                f"📞 الرقم: `{VODAFONE_NUMBER}`\n\n"
                "⚠️ يرجى دفع المبلغ المذكور\n"
                "📸 ثم ابعت صورة تأكيد الدفع"
            )
        else:
            text = (
                "💰 *Binance*\n\n"
                f"💎 الكمية: *{quantity}*\n"
                f"💵 السعر: *${total_price}*\n\n"
                f"🆔 Binance ID: `{BINANCE_ID}`\n\n"
                "⚠️ يرجى دفع المبلغ المذكور\n"
                "📸 ثم ابعت صورة تأكيد الدفع"
            )

        await query.message.edit_text(text, parse_mode="Markdown")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in waiting_quantity:
        try:
            quantity = int(update.message.text)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ من فضلك اكتب رقم صحيح")
            return

        total_price = round(quantity * PRICE_PER_GMAIL, 2)

        context.user_data["quantity"] = quantity
        context.user_data["total_price"] = total_price
        waiting_quantity.remove(user_id)

        keyboard = [
            [InlineKeyboardButton("📱 Vodafone Cash", callback_data="vodafone")],
            [InlineKeyboardButton("💰 Binance", callback_data="binance")]
        ]

        await update.message.reply_text(
            f"✅ *تفاصيل الطلب*\n\n"
            f"💎 الكمية: *{quantity}*\n"
            f"💵 السعر الإجمالي: *${total_price}*\n\n"
            "اختر طريقة الدفع:",
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
    total_price = context.user_data.get("total_price", "غير محدد")
    username = update.message.from_user.username or "بدون يوزر"

    caption = (
        "📥 *طلب شراء جديد*\n\n"
        f"👤 المستخدم: @{username}\n"
        f"🆔 ID: {user_id}\n"
        f"💎 الكمية: {quantity}\n"
        f"💵 السعر: ${total_price}\n"
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
