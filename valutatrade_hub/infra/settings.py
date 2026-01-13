#Паттерн Singleton

import os
import tomllib


class SettingsLoader:
    _instance = None
    
    #используем __new__ для реализации паттерна Singleton.
    #вызываем перед __init__ и решаем, нужно ли создавать
    #новый объект или можно вернуть уже существующий.
    #как будто бы в тысячу раз проще, чем метакласс
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SettingsLoader, cls).__new__(cls)

            #исходя из того, что написал выше
            #init только один раз используем
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self._config = {}
        self._load_config()
        self._initialized = True

    def _load_config(self):
        try:
            #находим корневую директорию проекта
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            toml_path = os.path.join(project_root, 'pyproject.toml')
            
            with open(toml_path, "rb") as f:
                data = tomllib.load(f)
                self._config = data.get("tool", {}).get('valutatrade', {})
        except FileNotFoundError:
            print('Ошибка: Файл pyproject.toml не найден')
            self._config = {}

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    def reload(self):
        print('Перезагрузка конфигурации')
        self._load_config()


#создаем единую точку доступа
settings_loader = SettingsLoader()


