import logging

from functions.common import get_backup_name, clear_temp
from functions.db import do_backup, check_db
from functions.s3 import upload_file, clear_s3, check_s3
from conf.config import databases
import sys

logger = logging.getLogger(__name__)

def main_function():
    """
    Перебираем каждую базу и резервируем ее. В конце очищаем лишние бэкапы
    """
    for database in databases:
        logger.info(f'Начали обработку базы данных {database.name}')
        backup_filename = f'{database.name}-{get_backup_name()}'
        logger.info(f'Название для бэкапа: {backup_filename}')
        do_backup(database.name, backup_filename)
        logger.info(f'Создание резенвой копии завершено')
        upload_file(backup_filename)
        logger.info(f'Резервная копия выгружена на s3 хранилище')
        clear_temp()
        logger.info(f'Папка для временных файлов очищена')

    clear_s3()

def check_function() -> None:
    """
    Проверяем S3, подключение к БД. Если что идет не так - завершаем программу и пишем ошибку в лог
    """
    if not check_s3():
        logger.critical('S3 не прошел проверку. Резервирование не запущено.')
        sys.exit(1)

    # TODO: Сделать проверку наличия указанных в конфиге БД
    if not check_db():
        logger.critical('С БД что-то не так. Проверьте наличие указанных БД.')
        sys.exit(1)
    
    return True