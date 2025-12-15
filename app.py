import random
import os
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, InlineQueryHandler, CommandHandler
from uuid import uuid4
from flask import Flask, request, jsonify

# --- НАСТРОЙКИ ---
# Токен берется из переменной окружения Railway (очень важно для безопасности)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "ВАШ_ТОКЕН_ЗДЕСЬ_ДЛЯ_ЛОКАЛЬНОГО_ТЕСТА")
# PORT больше не нужен, его обработает Gunicorn
# PORT = int(os.environ.get("PORT", 5000)) 

# Главная картинка (URL для превью)
MAIN_PHOTO = "https://tkrim.ru/images/stati/8weJe2QW.jpg"

# Тексты типов диггеров (19 вариантов)
# ... (Оставьте здесь ВЕСЬ ваш список TEXTS из 19 элементов) ...
TEXTS = [
    "<b>ТЫ ДИГГЕР НА:</b> <tg-spoiler>0% - грязный чоп 👮🏿‍♂️</tg-spoiler>\n\n"
    "• Дяденька отпустите меня!\n"
    "• Нет, ты останешься гнить в бомбаре с гп5 мухэхэхэхэ))\n\n"
    "🤖 @Diggerspbdigger",
    
    # ... ОСТАЛЬНЫЕ ТИПЫ ...
    
    "<b>ТЫ ДИГГЕР НА:</b> <tg-spoiler>14% - Эмка 🐒</tg-spoiler>\n\n"
    "• Еблан который нихуя не может (рофл)\n\n"
    "🤖 @Diggerspbdigger",
]

# Инициализация Flask и PTB
app = Application.builder().token(TOKEN).build()
flask_app = Flask(__name__) # <--- ЭТОТ ОБЪЕКТ МЫ БУДЕМ ИСПОЛЬЗОВАТЬ В GUNICORN

# --- ОБРАБОТЧИКИ (без изменений) ---

async def start_command(update: Update, context):
    """Обработчик команды /start."""
    await update.message.reply_text(
        "👋 <b>Digger Level Bot (Webhooks)</b>\n\n"
        "<b>Как использовать:</b>\n"
        "1. В любом чате\n"
        "2. Введи: @username_бота и пробел\n"
        "3. Появится '🚷 Узнай на сколько ты диггер!' с картинкой.\n"
        "4. **Нажми** на карточку — в чат отправится **случайный** тип из 19!\n\n"
        "🤖 @Diggerspbdigger",
        parse_mode='HTML'
    )

async def inline_handler(update: Update, context):
    query_text = update.inline_query.query.strip()
    
    if query_text == "":
        random_text = random.choice(TEXTS)
        
        message_content = InputTextMessageContent(
            message_text=random_text,
            parse_mode='HTML'
        )
        
        result = InlineQueryResultArticle(
            id=str(uuid4()),
            title="🚷 Узнай на сколько ты диггер!",
            description="Нажми, чтобы получить СЛУЧАЙНЫЙ тип диггера! (19 типов)",
            thumbnail_url=MAIN_PHOTO, 
            input_message_content=message_content,
        )

        await update.inline_query.answer([result], cache_time=0)
        return
    else:
        await update.inline_query.answer([], cache_time=0)


# Добавляем обработчики в Application
app.add_handler(CommandHandler("start", start_command)) 
app.add_handler(InlineQueryHandler(inline_handler))


# --- ФУНКЦИИ WEBHOCK ---

@flask_app.route('/')
def home():
    """Проверка доступности сервера."""
    return "Digger Level Bot is running with Webhooks!", 200

@flask_app.route('/webhook', methods=['POST'])
async def webhook():
    """Обработка входящих обновлений от Telegram."""
    if request.method == "POST":
        json_data = request.get_json(force=True)
        update = Update.de_json(json_data, app.bot)
        await app.process_update(update)
        return "ok", 200
    return jsonify({}), 405

# --- НАСТРОЙКА WEBHOOK ПРИ ЗАГРУЗКЕ МОДУЛЯ (НОВЫЙ БЛОК КОДА) ---

# Gunicorn загружает модуль app.py, выполняя этот код.
# Мы используем это для настройки Webhook до запуска сервера.

print("--- ⚙️ Настройка Webhook... ---")

# Render использует переменную RENDER_EXTERNAL_HOSTNAME, Railway - RAILWAY_STATIC_URL
WEBHOOK_DOMAIN = os.environ.get("RENDER_EXTERNAL_HOSTNAME") or \
                 os.environ.get("RAILWAY_STATIC_URL") or \
                 os.environ.get("RAILWAY_PUBLIC_DOMAIN")

if WEBHOOK_DOMAIN:
    full_webhook_url = f"https://{WEBHOOK_DOMAIN}/webhook"
    print(f"Установка Webhook на: {full_webhook_url}")
    # Эта команда устанавливает Webhook в Telegram
    app.bot.set_webhook(url=full_webhook_url)
else:
    print("Переменная среды хостинга не найдена. Webhook не установлен.")
    
# --- (УДАЛЕНА ФУНКЦИЯ run_web_server) ---

if __name__ == '__main__':
    # Эта часть используется только для локального тестирования
    PORT = int(os.environ.get("PORT", 5000))
    print("Запуск локального сервера (только для тестирования)...")
    flask_app.run(debug=True, port=PORT)
