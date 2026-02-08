from telegram import Update, ReplyKeyboardMarkup as keyboard
from telegram.ext import (
    ApplicationBuilder as create,
    CommandHandler as command,
    MessageHandler as processing,
    ConversationHandler as control,
    ContextTypes,
    filters
)

from answer import answer
from database import init_db, add_request


TOKEN = ""

CHOOSE_DEPT, WRITE_MESSAGE = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        ["📌 Частые вопросы"],
        ["✍️ Написать в поддержку"]
    ]

    await update.message.reply_text(
        "👋 Добро пожаловать в техподдержку магазина «Продаем всё на свете»!",
        reply_markup=keyboard(buttons, resize_keyboard=True)
    )

async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📌 Часто задаваемые вопросы:\n\n"

    for key in answer:
        text += f"• {key.capitalize()}\n"

    text += "\n✍️ Напишите вопрос своими словами"
    await update.message.reply_text(text)

async def faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()

    for key, answer in answer.items():
        if key in user_text:
            await update.message.reply_text(answer)
            return

    await update.message.reply_text(
        "❌ Не нашёл ответ.\n"
        "Вы можете обратиться к специалисту 👉 ✍️ Написать в поддержку"
    )


async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        ["🛠 Проблема с сайтом / оплатой"],
        ["🛒 Проблема с товаром"]
    ]

    await update.message.reply_text(
        "Выберите тип проблемы:",
        reply_markup=keyboard(buttons, resize_keyboard=True)
    )

    return CHOOSE_DEPT

async def faq_item_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()

    if text in answer:
        await update.message.reply_text(answer[text])
        return


async def choose_department(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "сайт" in text or "оплат" in text:
        context.user_data["department"] = "programmers"
    else:
        context.user_data["department"] = "sales"

    await update.message.reply_text("✍️ Опишите вашу проблему:")
    return WRITE_MESSAGE

async def save_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    message = update.message.text
    department = context.user_data["department"]

    add_request(
        user_id=user.id,
        username=user.username,
        department=department,
        message=message
    )

    await update.message.reply_text(
        "✅ Заявка принята!\nНаши специалисты скоро с вами свяжутся."
    )

    return control.END

def main():
    init_db()

    app = create().token(TOKEN).build()

    conv = control(
        entry_points=[
            processing(filters.TEXT & filters.Regex("^✍️ Написать в поддержку$"), support_start)
        ],
        states={
            CHOOSE_DEPT: [processing(filters.TEXT, choose_department)],
            WRITE_MESSAGE: [processing(filters.TEXT, save_request)],
        },
        fallbacks=[]
    )
    
    app.add_handler(command("start", start))

    app.add_handler(conv)

    app.add_handler(
        processing(filters.TEXT & filters.Regex("^📌 Частые вопросы$"), show_faq)
    )

    app.add_handler(
        processing(filters.TEXT & filters.Regex("^(Оплата|Доставка|Возврат|Сайт)$"), faq_item_handler)
    )

    app.add_handler(
        processing(filters.TEXT & ~filters.COMMAND, faq_handler)
    )

    print("🤖 Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()
