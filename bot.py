import json
import logging
import os

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", "0"))
MINI_APP_URL = os.getenv("MINI_APP_URL", "")

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


def main_keyboard() -> ReplyKeyboardMarkup:
    catalog_button = (
        KeyboardButton("Открыть каталог", web_app=WebAppInfo(url=MINI_APP_URL))
        if MINI_APP_URL
        else KeyboardButton("Каталог")
    )
    return ReplyKeyboardMarkup(
        [
            [catalog_button],
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
    await update.message.reply_text(text, reply_markup=main_keyboard())


async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    raw_data = update.effective_message.web_app_data.data

    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError:
        await update.effective_message.reply_text(
            "Не получилось прочитать заказ. Попробуйте отправить ещё раз.",
            reply_markup=main_keyboard(),
        )
        return

    if data.get("type") != "order":
        await update.effective_message.reply_text(
            "Данные получены, но это не заказ.",
            reply_markup=main_keyboard(),
        )
        return

    items = data.get("items", [])
    item_lines = []
    for item in items:
        name = item.get("name", "Товар")
        qty = int(item.get("qty", 1))
        price = int(item.get("price", 0))
        item_lines.append(f"- {name} x{qty} = {qty * price} манат")

    order_text = (
        "Новый заказ из Mini App\n\n"
        f"Клиент в Telegram: {user.full_name}\n"
        f"Username: {format_username(user.username)}\n"
        f"Имя: {data.get('name', '-')}\n"
        f"Телефон: {data.get('phone', '-')}\n\n"
        "Товары:\n"
        + "\n".join(item_lines)
        + f"\n\nИтого: {data.get('total', 0)} манат"
    )

    await send_owner_message(context, order_text)
    await update.effective_message.reply_text(
        "Спасибо! Заказ принят. Менеджер скоро свяжется с вами.",
        reply_markup=main_keyboard(),
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text in ("Каталог", "Открыть каталог"):
        if MINI_APP_URL:
            await update.message.reply_text(
                "Нажмите кнопку «Открыть каталог» в меню, чтобы открыть красивый каталог с корзиной.",
                reply_markup=main_keyboard(),
            )
            return

        catalog = "Каталог продуктов:\n\n"
        for category, items in PRODUCTS.items():
            catalog += f"{category}\n"
            for item in items:
                catalog += f"- {item}\n"
            catalog += "\n"
        await update.message.reply_text(catalog, reply_markup=main_keyboard())
        return

    if text == "Акции":
        await update.message.reply_text(
            "Акции недели:\n\n"
            "- Бесплатная доставка от 200 манат\n"
            "- Скидка 10% на первый заказ\n"
            "- Семейный овощной набор по специальной цене",
            reply_markup=main_keyboard(),
        )
        return

    if text == "Контакты":
        await update.message.reply_text(
            f"Адрес: {BUSINESS['address']}\n"
            f"Город: {BUSINESS['city']}\n"
            f"Время работы: {BUSINESS['work_time']}\n"
            f"Телефон: {BUSINESS['phone']}",
            reply_markup=main_keyboard(),
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
            reply_markup=main_keyboard(),
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
            reply_markup=main_keyboard(),
        )
        return

    await update.message.reply_text(
        "Выберите раздел в меню или нажмите «Оставить заявку».",
        reply_markup=main_keyboard(),
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
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
