import logging
import sys
import asyncio

from src.backup import check_function, main_function
# from src.restore import start_bot
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
        logger.info('***'*15)
        logger.info('Запуск программы')
        logger.info('***'*15)
        check_function()
        logger.info('Проверки пройдены успешно')
        logger.info(f'Запускаем бэкапы')
        main_function()
        logger.info('Создание бэкапов завершено')

    if "--restore" in sys.argv:
        asyncio.run(start_bot())


