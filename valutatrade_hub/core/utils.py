#тут воспользовался ии для понимания того, что вообще требуется
#извините
#реализована следующая логика
#все вспомогательные функции хранятся в этом файле
#из него в будущем будут вызываться конструкции,
#которые помогут в чтении файлов и их перезаписи (и т.д.)

import json
import os

#определяем базовую директорию проекта с помощью констант
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')

#определяем пути к нашим файлам с данными с помощью констант
USERS_FILE_PATH = os.path.join(DATA_DIR, 'users.json')
PORTFOLIOS_FILE_PATH = os.path.join(DATA_DIR, 'portfolios.json')

#добавляем файл с курсом валют
RATES_FILE_PATH = os.path.join(DATA_DIR, 'rates.json')

#функция для чтения
def read_json(file_path, default_data=None):
    if default_data is None:
        default_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            #читаем и возвращаем данные
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_data

#функция для чтения
def write_json(file_path, data):

    #убедимся, что всё директория вообще существует
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
    
        #записываем данные
        json.dump(data, f, indent=4, ensure_ascii=False)


