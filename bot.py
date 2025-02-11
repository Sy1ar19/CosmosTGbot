from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import TG_BOT_API
from handlers import register_handlers
from database import init_db, delete_db
from aiogram.types import BotCommand

# Создаём хранилище состояний
storage = MemoryStorage()

# Создаём Dispatcher
dp = Dispatcher(storage=storage)


async def run_bot() -> None:
    """Функция запуска бота"""
    # Инициализируем базу данных перед запуском бота
    delete_db()
    init_db()

    bot = Bot(token=TG_BOT_API, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Устанавливаем меню команд
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="add_address", description="Ввести добавить адрес"),
        BotCommand(command="my_stake", description="Посмотреть застейканные средства"),
    ])

    # Регистрируем обработчики команд
    register_handlers(dp)

    # Запускаем бота
    await dp.start_polling(bot)
