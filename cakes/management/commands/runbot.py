import logging.config

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from django.core.management import BaseCommand

import conf.settings as settings
from cakes.logger_config import logger_config
from cakes.management.commands.bot.handlers.user_handlears import register_user_handlers, bot

logger = logging.getLogger("bot_logger")

logging.config.dictConfig(logger_config)

def register_handlers(dp: Dispatcher) -> None:
    register_user_handlers(dp)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
register_handlers(dp)


async def set_commands(bot: Bot):
    commands = [
            types.BotCommand(
                command="/start",
                description="Начало",
            ),
            types.BotCommand(
                command="/admin",
                description="Меню организатора",
            ),
            types.BotCommand(
                command="/help",
                description="Справка по работе бота",
            ),
            types.BotCommand(
                command="/cancel",
                description="Отмена текущего действия, возврат в главное меню",
            ),
        ]
    await bot.set_my_commands(commands)


class Command(BaseCommand):
    def handle(self, *args, **options):
        executor.start_polling(dp, skip_updates=True)
