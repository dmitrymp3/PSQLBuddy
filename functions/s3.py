import boto3
from botocore.exceptions import ClientError
import logging
from conf.config import boto_config, temp_path, rules_for_backups, Config
# import pprint
from pprint import pprint

logger = logging.getLogger(__name__)

# Убираем логи boto, их слишком много при выгрузке файлов
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('nose').setLevel(logging.WARNING)

# Создаем клиент для коннекта к s3 хранилищу
s3 = boto3.client('s3', **boto_config.return_data())

# Добавим финальный слэш во временную папку, здесь он нужен
temp_folder = f'{temp_path}/'


def upload_file(filename):
    """
    Просто загружает файл в бакет
    """
    s3.upload_file(temp_folder + filename, boto_config.s3_bucket, filename)


def clear_s3():
    """
    Эта функция будет очищать s3 хранилище от старых бэкапов
    1. Получаем список всех бэкапов
    2. Разбиваем их по базам
    3. Разбиваем по типам
    4. Берем из конфига данные о количестве хранимых бэкапов по типам
    5. Определяем бэкапы к удалению
    6. Удаляем бэкапы
    """
    logger.info('Запускаем очистку')
    dict_of_objects: dict = s3.list_objects(Bucket=boto_config.s3_bucket).get('Contents')
    # list_of_objects = list_of_objects.get('Contents')
    objects_by_db = {}

    database_to_delete = []

    for object in dict_of_objects:
        backup_name = object.get('Key')
        # print(backup_name)
        database_name: str = backup_name.split('-')[0]
        backup_type: str = backup_name.split('-')[2].replace('.dump', '')

        if database_name not in objects_by_db:
            objects_by_db[database_name] = {}
        if backup_type not in objects_by_db[database_name]:
            objects_by_db[database_name][backup_type] = list()

        objects_by_db[database_name][backup_type].append(backup_name)

    # Проверяем каждую базу
    for database, backups in objects_by_db.items():
        # Получаем количество бэкапов из конфига
        database_rules = rules_for_backups.get(database)
        for type_of_backup, backups in backups.items():
            # Получаем количество хранимых бэкапов для этой базы данных и для этого типа бэкапов (DAILY, MONTHLY)
            counter = database_rules.get(type_of_backup) if database_rules else rules_for_backups['default'][type_of_backup]
            # Если количество бэкапов больше, чем нужно
            if len(backups) > counter:
                database_to_delete.extend(backups[0:-counter])


    for database in database_to_delete:
        try:
            s3.delete_object(Bucket=boto_config.s3_bucket, Key=database)
            logger.info(f'Удален бэкап: {database}')
        except:
            logger.warning(f'Попытка удаления бэкапа {database} была неуспешной.')
    logger.info('Очистка завершена')

def check_s3() -> dict:
    """
    Получаем список бакетов, проверяя соединение с S3
    """
    # Пробуем подключиться к s3 и получить список бакетов
    try:
        buckets_dict = s3.list_buckets()
    except ClientError as e:
        logger.critical('Неправильно указаны учетные данные')
        return False
    
    # Формируем список бакетов для второй проверки
    buckets_list = [bucket.get('Name') for bucket in buckets_dict.get('Buckets')]

    # Проверяем наличие указанного в конфиге бакета
    if boto_config.s3_bucket not in buckets_list:
        logger.critical('Неправильно введен s3 бакет')
        return False
    
    return True


#################### BOT #######################

def get_db_types() -> list:
    """
    Получаем список баз данных, которые хранятся в S3
    """
    objects: dict = s3.list_objects(Bucket=Config.bucket) # получаем список объектов в бакете
    db_names = list() # Наполняем это множество базами

    # Перебираем список объектов
    for backup in objects.get('Contents'):
        name_of_backup: str = backup.get('Key') # получаем название объекта
        db_name = name_of_backup.split('-')[0] # вытаскиваем префикс

        # Если такого префикса во множестве нету - добавляем его
        if db_name not in db_names:
            db_names.append(db_name)

    return db_names

def get_backups_by_database(database_name) -> list:
    """
    Вытаскиваем все бэкапы выбранной базы данных
    """
    database_name += '-'
    objects: dict = s3.list_objects(Bucket=Config.bucket)
    backups = list()

    for backup in objects.get('Contents'):
        if database_name in backup.get('Key'):
            backups.append(backup.get('Key'))
    return backups


def check_database(backup_name) -> bool:
    """
    Пробуем вытащить выбранный бэкап. Если получилось - вернем True
    """
    try:
        response = s3.get_object(Bucket=Config.bucket, Key=backup_name)
    except:
        return False
    
    return True

def download_database(backup_name) -> dict:
    """
    Загружаем выбранную базу данных в папку temp
    """
    try:
        # print('Начинаем загрузку файла') 
        s3.download_file(Config.bucket, backup_name, Config.path_for_backups + backup_name)
        result = {'status': True, 'message': f'Загрузка завершена'}
    except ValueError:
        result = {'status': False, 'message': f'Ошибка. Код ошибки: ' + ValueError}

    return result

def upload_database(file_to_upload):
    """
    Функция для выгрузки файла бэкапа. Бесполезная в данной реализации
    Удалить
    """
    s3.upload_file(Config.path_for_backups + file_to_upload, Config.bucket, file_to_upload)