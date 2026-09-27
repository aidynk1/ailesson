import asyncio
import logging
import os
from threading import Thread

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from flask import Flask


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

web_app = Flask(__name__)
dispatcher = Dispatcher()


@web_app.get("/")
def health_check():
    return {"status": "ok", "service": "telegram-bot"}, 200


@dispatcher.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        "Привет! Отправь мне любой текст, и я верну его заглавными буквами.\n"
        "Команда /help покажет справку."
    )


@dispatcher.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(
        "Я преобразую текст в верхний регистр. Просто отправь сообщение, например: «Привет»"
    )


@dispatcher.message()
async def handle_message(message: Message) -> None:
    if message.text:
        await message.answer(message.text.upper())
    else:
        await message.answer("Пожалуйста, отправь текстовое сообщение.")


def run_web_server() -> None:
    port = int(os.environ.get("PORT", "8080"))
    web_app.run(host="0.0.0.0", port=port, threaded=True, use_reloader=False)


async def run_bot(token: str) -> None:
    bot = Bot(token=token)
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("Не задан BOT_TOKEN. Добавьте токен в Secrets / переменные окружения Replit.")

    server_thread = Thread(target=run_web_server, name="health-server", daemon=True)
    server_thread.start()
    asyncio.run(run_bot(token))


if __name__ == "__main__":
    main()