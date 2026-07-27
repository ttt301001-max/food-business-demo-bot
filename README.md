# Food Business Demo Bot

Шаблон Telegram-бота визитки для продуктового бизнеса.

## Что умеет бот

- Показывает приветствие бизнеса
- Открывает каталог товаров
- Показывает акции
- Показывает контакты
- Принимает заявку от клиента
- Отправляет заявку владельцу в Telegram
- Принимает вопросы от клиентов
- Открывает Mini App каталог с корзиной

## Файлы

- `bot.py` - код бота
- `requirements.txt` - зависимости Python
- `Procfile` - команда запуска для Railway
- `.python-version` - версия Python для Railway
- `mise.toml` - настройка установки Python на Railway
- `docs/index.html` - Telegram Mini App каталог
- `docs/.nojekyll` - настройка GitHub Pages для статического сайта

## Переменные Railway

В Railway нужно добавить:

```txt
BOT_TOKEN=токен_бота_из_BotFather
OWNER_CHAT_ID=ваш_telegram_id
MINI_APP_URL=https://ваш-github-username.github.io/название-репозитория/
```

## Как запустить

1. Создайте бота в `@BotFather`.
2. Получите `BOT_TOKEN`.
3. Узнайте свой Telegram ID через `@userinfobot`.
4. Загрузите эти файлы в GitHub.
5. В Railway выберите `Deploy from GitHub`.
6. Добавьте переменные `BOT_TOKEN` и `OWNER_CHAT_ID`.
7. Включите GitHub Pages из папки `docs`.
8. Добавьте в Railway переменную `MINI_APP_URL`.
9. Перезапустите проект.

## Что менять под клиента

В файле `bot.py` измените блок `BUSINESS`:

```python
BUSINESS = {
    "name": "Fresh Market",
    "city": "Ваш город",
    "phone": "+993 XX XXX XX XX",
    "address": "ул. Центральная, 10",
    "work_time": "09:00 - 21:00",
}
```

И блок `PRODUCTS`, чтобы заменить товары, категории и цены.

## Админка владельца

Владелец, чей Telegram ID указан в `OWNER_CHAT_ID`, может открыть админку командой:

```txt
/admin
```

В админке есть:

- статистика пользователей и заявок
- последние заказы
- рассылка акций всем пользователям
- возврат в обычное меню клиента
