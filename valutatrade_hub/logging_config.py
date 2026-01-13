#импорт для логирования
import logging
import os
from logging.handlers import RotatingFileHandler

#импорт SettingsLoader
from valutatrade_hub.infra.settings import settings_loader


#настраиваем логгер
def setup_logging():
    log_file_path_str = settings_loader.get('log_file_path', 'logs/app.log')
    log_format = settings_loader.get(
        'log_format', 
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    #создаем папку, где будут храниться наши логи
    log_dir = os.path.dirname(log_file_path_str)
    os.makedirs(log_dir, exist_ok=True)

    #с помощью ии создал обработчик
    #максимальный размер файлов 5 мб
    #хранится в директории 3 старых записи
    file_handler = RotatingFileHandler(
        log_file_path_str, 
        maxBytes=5*1024*1024, 
        backupCount=3,
        encoding='utf-8'
    )
    
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(log_format, datefmt='%Y-%m-%dT%H:%M:%S')
    file_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO) # Базовый уровень для всего приложения
    
    if not root_logger.handlers:
        root_logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)


