import os
import logging

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", "0"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


BUSINESS = {
    "name": "Fresh Market",
    "city": "Ваш город",
    "phone": "+993 XX XXX XX XX",
    "address": "ул. Центральная, 10",
    "work_time": "09:00 - 21:00",
}


PRODUCTS = {
    "Овощи и фрукты": [
        "Помидоры - 25 манат/кг",
        "Огурцы - 18 манат/кг",
        "Яблоки - 20 манат/кг",
    ],
    "Молочные продукты": [
        "Молоко - 15 манат",
        "Сметана - 18 манат",
        "Сыр домашний - 45 манат/кг",
    ],
    "Бакалея": [
        "Рис - 22 манат/кг",
        "Макароны - 12 манат",
        "Масло - 35 манат",
    ],
}


MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["Каталог", "Акции"],
        ["Оставить заявку", "Контакты"],
        ["Задать вопрос"],
    ],
    resize_keyboard=True,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"Здравствуйте! Это {BUSINESS['name']}.\n\n"
        "Свежие продукты для дома и бизнеса.\n"
        "Выберите нужный раздел:"
    )
    await update.message.reply_text(text, reply_markup=MAIN_KEYBOARD)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text == "Каталог":
        catalog = "Каталог продуктов:\n\n"
        for category, items in PRODUCTS.items():
            catalog += f"{category}\n"
            for item in items:
                catalog += f"- {item}\n"
            catalog += "\n"
        await update.message.reply_text(catalog, reply_markup=MAIN_KEYBOARD)
        return

    if text == "Акции":
        await update.message.reply_text(
            "Акции недели:\n\n"
            "- Бесплатная доставка от 200 манат\n"
            "- Скидка 10% на первый заказ\n"
            "- Семейный овощной набор по специальной цене",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    if text == "Контакты":
        await update.message.reply_text(
            f"Адрес: {BUSINESS['address']}\n"
            f"Город: {BUSINESS['city']}\n"
            f"Время работы: {BUSINESS['work_time']}\n"
            f"Телефон: {BUSINESS['phone']}",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    if text == "Оставить заявку":
        context.user_data["waiting_order"] = True
        await update.message.reply_text(
            "Напишите одним сообщением: что хотите заказать, ваше имя и телефон.\n\n"
            "Пример:\n"
            "Анна, +993 XX XXX XX XX, хочу овощной набор и молоко"
        )
        return

    if context.user_data.get("waiting_order"):
        context.user_data["waiting_order"] = False
        await send_owner_message(
            context,
            "Новая заявка\n\n"
            f"Клиент: {user.full_name}\n"
            f"Username: {format_username(user.username)}\n"
            f"Сообщение: {text}",
        )
        await update.message.reply_text(
            "Спасибо! Заявка принята. Менеджер скоро свяжется с вами.",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    if text == "Задать вопрос":
        context.user_data["waiting_question"] = True
        await update.message.reply_text("Напишите ваш вопрос одним сообщением.")
        return

    if context.user_data.get("waiting_question"):
        context.user_data["waiting_question"] = False
        await send_owner_message(
            context,
            "Новый вопрос\n\n"
            f"Клиент: {user.full_name}\n"
            f"Username: {format_username(user.username)}\n"
            f"Вопрос: {text}",
        )
        await update.message.reply_text(
            "Спасибо! Я передал вопрос менеджеру.",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    await update.message.reply_text(
        "Выберите раздел в меню или нажмите «Оставить заявку».",
        reply_markup=MAIN_KEYBOARD,
    )


async def send_owner_message(context: ContextTypes.DEFAULT_TYPE, text: str):
    if not OWNER_CHAT_ID:
        logger.warning("OWNER_CHAT_ID is not set, owner notification skipped")
        return
    await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=text)


def format_username(username: str | None) -> str:
    return f"@{username}" if username else "нет"


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
