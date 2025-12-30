import asyncio
from threading import Thread
from flask import Flask
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.handlers import router
from config import TOKEN
from app.database.models import async_main

# 1. Создаем простой веб-сервер для Render
web_app = Flask('')

@web_app.route('/')
def home():
    return "🤖 Бот работает! Статус: Online"

def run_web_app():
    web_app.run(host='0.0.0.0', port=10000)

# 2. Функция для запуска бота
async def start_bot():
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(router)
    
    # Инициализируем БД
    await async_main()
    
    print("✅ Бот запущен!")
    await dp.start_polling(bot)

# 3. Главная функция
def main():
    print("🚀 Запускаем сервер и бота...")
    
    # Запускаем веб-сервер в отдельном потоке
    server_thread = Thread(target=run_web_app, daemon=True)
    server_thread.start()
    
    # Запускаем бота
    asyncio.run(start_bot())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Бот остановлен")
    except Exception as e:
        print(f"Ошибка: {e}")