import os
import logging
from datetime import date
from conf.config import CommonConfig

logger = logging.getLogger(__name__)

def clean_temp():
    """
    Очищаем временную папку
    """
    files_in_temp = os.listdir(CommonConfig.temp_path)
    for filename in files_in_temp:
        os.remove(f'{CommonConfig.temp_path}/{filename}')
        logger.info(f'Файл удален: {filename}')
    logger.info(f'Все файлы удалены')

def get_backup_name() -> str:
    """
    Создаем название для бэкапа, а также определяем, к какому типу он относится (годовой, месячный или ежедневный)
    Формат возвращаемой строки: 2024_09_19-DAILY.dump
    """
    today: date = date.today()
    day_of_month: int = today.day
    day_of_week: int = today.isoweekday()
    month: int = today.month

    # Сегодняшняя дата в формате для названия
    string_date = today.strftime("%Y_%m_%d")

    # Годовой архив делается 1 января. Не удаляется никогда
    if month == 1 and day_of_month == 1:
        type_of_backup = 'YEARLY'
    elif day_of_month == 1: # Если сегодня первый день месяца - это месячный бэкап
        type_of_backup = 'MONTHLY'
    elif day_of_week == 1: # Если сегодня первый день недели - это еженедельный бэкап
        type_of_backup = 'WEEKLY'
    else: # Во всех остальных случаях это ежедневный бэкап
        type_of_backup = 'DAILY'

    return f'{string_date}-{type_of_backup}.dump'