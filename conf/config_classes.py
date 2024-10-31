from dataclasses import dataclass, field, InitVar

@dataclass
class BotoConfig:
    """
    Базовый набор атрибутов для создания подключения к s3
    """
    region_name: str = 'ru-1'
    api_version: str | None = None
    use_ssl: bool = True
    verify: str | None = None
    endpoint_url: str = 'https://s3.timeweb.cloud'
    aws_access_key_id: str = ''
    aws_secret_access_key: str = ''
    aws_session_token: str | None = None
    # config: str = ''
    s3_bucket: str = ''

    def return_data(self) -> dict:
        """
        Возвращает словарь параметров необходимых для подключения
        """
        return {k: v for k, v in self.__dict__.items() if k != 's3_bucket' and v}

@dataclass
class DatabaseForBackup:
    """
    Класс описывает базу данных, ее название и количество хранимых бэкапов
    """
    name: str
    temp_freq: InitVar[dict] = dict()
    frequency: dict = field(default_factory=dict)

    def __post_init__(self, temp_freq: dict):
        # TODO: Надо как-то перетащить значения по умолчанию в конфиг
        default_values = {
            'DAILY'     : 4,
            'WEEKLY'    : 4,
            'MONTHLY'   : 4,
            'YEARLY'    : 999,
        }
        # Такой метод выбран, чтобы отсечь неправильную передачу параметра, например, DILY, WEKLY
        for key in default_values.keys():
            self.frequency.update({key: temp_freq.get(key, default_values.get(key))})


class DataBasesList:
    """
    Получает все базы данных и устанавливает им частоту ротации
    Пример заполнения:
    databases = DataBasesList({
        '95c': {
            'key': 'value', # случайные значения. Будут проигнорированы
            'DAILY': 40
            },
        'volleyball_db': {}
    })
    """
    db_dict: dict

    _default_values = {
            'DAILY'     : 4,
            'WEEKLY'    : 4,
            'MONTHLY'   : 4,
            'YEARLY'    : 999,
        }
    
    def __init__(self, databases: dict[str: dict]):
        self.db_dict = {name: self.frequency_validator(freq) for name, freq in databases.items()}

    @staticmethod
    def frequency_validator(freq: dict):
        freq = filter(lambda x: x == isinstance())
        return {k: freq.get(k, default) for k, default in __class__._default_values.items()}
    
    @property
    def db_names(self):
        return [db_name for db_name in self.db_dict.keys()]
    

class AllDatabases:
    """
    Содержит список всех баз данных, каждая из которых является экземпляром класса DatabaseForBackup
    """
    default_freq = {
            'DAILY'     : 4,
            'WEEKLY'    : 4,
            'MONTHLY'   : 4,
            'YEARLY'    : 999,
        }

    def __init__(self):
        self.databases_dict = {}
    
    def add_database(self, db_name: str, freq: dict={}):
        freq = {k: freq.get(k, v) for k, v in self.default_freq.items()}
        self.databases_dict.update({db_name: freq})

    def get_database_freq(self, db_name) -> dict:
        return self.databases_dict.get(db_name, None)
    
    @staticmethod
    def set_default_freq(freq: dict):
        __class__.default_freq = {k: freq.get(k, v) for k, v in __class__.default_freq.items()}

    def __repr__(self) -> str:
        return f'{self.databases_dict}'

    def __iter__(self):
        for name in self.databases_dict.keys():
            yield name