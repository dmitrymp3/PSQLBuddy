import logging
import sys
import asyncio

from src.backup import check_function, backup_function
from bot.bot_init import start_bot

# Создаем логгер
logging.basicConfig(
    # filename='common.log', 
    encoding='UTF-8', 
    level=logging.DEBUG, 
    format='%(asctime)s %(message)s', 
    datefmt='[%Y-%m-%d %H:%M]'
    )
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if "--backup" in sys.argv:
        logger.info('Запуск программы')
        check_function()
        backup_function()
        logger.info('Создание бэкапов завершено')

    if "--restore" in sys.argv:
        asyncio.run(start_bot())


