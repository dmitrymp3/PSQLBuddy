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
class AllDatabases:
    """
    Содержит список всех баз данных, каждая из которых является экземпляром класса DatabaseForBackup
    """
    db_list: list
    db_names: list

    def __iter__(self):
        return self
    
    def __next__(self):
        return self


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

