import logging.config

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from django.core.management import BaseCommand

import conf.settings as settings
from cakes.logger_config import logger_config

logger = logging.getLogger("bot_logger")

logging.config.dictConfig(logger_config)

storage = MemoryStorage()
bot = Bot(token=settings.TG_TOKEN_API, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)


class Command(BaseCommand):
    def handle(self, *args, **options):
        executor.start_polling(dp, skip_updates=True)
