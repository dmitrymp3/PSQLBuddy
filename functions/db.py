from conf.config import CommonConfig
import subprocess
import logging
from psycopg2.extensions import connection
import os
import subprocess

logger = logging.getLogger(__name__)

def do_backup(database, backup_filename):
	"""
	Создает бэкап переданной базы данных, название передается вторым аргументом
	"""
	command = [
        	'pg_dump',
	        '-U', 'postgres',
	        '-F', 'c',  # Формат: custom
	        # '-v',  # Подробный вывод
	        '-d', database,
	        '-f', CommonConfig.temp_path + '/' + backup_filename
	    ]
    
   	 # Выполняем команду резервного копирования
	try:
		subprocess.run(command, check=True)
		logger.info(f'База данных {database} успешно сохранена {CommonConfig.temp_path + "/" + backup_filename}')
	except subprocess.CalledProcessError as e:
		logger.critical(f'Ошибка при резервном копировании базы данных: {e}')
		logger.critical(repr(e))

def check_db() -> bool:
	"""
	Получаем список всех БД и убеждаемся, что присутствуют все из конфига
	"""
	return True

def drop_archive_database() -> dict:
    """
    Сначала надо удалить БД
    sudo -u postgres psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS archive";
    """
    drop_database_command = [
        'psql', '-U', 'postgres', '-d', 'postgres', '-c',
        'DROP DATABASE IF EXISTS archive;'
    ]

    try:
        subprocess.run(drop_database_command, check=True)
        result = {'status': True, 'message': f"База archive дропнута"}
    except subprocess.CalledProcessError as e:
        result = {'status': False, 'message': f"Ошибка дропа БД archive: {e}"}

    return result

def create_archive_database() -> dict:
    """
    Теперь надо создать БД
    sudo -u postgres psql -U postgres -d postgres -c "CREATE DATABASE archive";
    """
    create_database_command = [
        'psql', '-U', 'postgres', '-d', 'postgres', '-c',
        'CREATE DATABASE archive;'
    ]

    try:
        subprocess.run(create_database_command, check=True)
        result = {'status': True, 'message': f"База archive создана"}
    except subprocess.CalledProcessError as e:
        result = {'status': False, 'message': f"Ошибка создания БД archive: {e}"}

    return result

def restore_database(backup_file) -> dict:
    """
    Восстанавливаем базу данных
    """    
    # Формируем команду для восстановления
    pg_restore_command = [
        'pg_restore',
        '-U', 'postgres',
        '-d', 'archive',
        # '-v',  # Подробный вывод
        f'{CommonConfig.temp_path}/{backup_file}'
    ]
    # Выполняем команду восстановления
    try:
        subprocess.run(pg_restore_command, check=True)
        logger.info(f'База данных успешно восстановлена из {backup_file}')
        result = {'status': True, 'message': f"База данных успешно восстановлена из {backup_file}"}
    except subprocess.CalledProcessError as e:
        logger.info(f'Ошибка при восстановлении базы данных: {e}')
        result = {'status': False, 'message': f"Ошибка при восстановлении базы данных: {e}"}

    return result