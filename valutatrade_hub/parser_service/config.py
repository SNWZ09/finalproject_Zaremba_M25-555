import os
from dataclasses import dataclass, field
from typing import Tuple, Dict

#получаем ключ из файла на компьютере
#тк нельзя, чтобы он был в коде/на гитхабе
from dotenv import load_dotenv

load_dotenv() 

@dataclass(frozen=True)
class ParserConfig:

    #ключ загружается из переменной окружения при создании объекта.
    EXCHANGERATE_API_KEY: str = os.getenv("EXCHANGERATE_API_KEY")

    #эндпоинты
    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"

    #списки валют
    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES: Tuple[str, ...] = ("EUR", "GBP", "RUB")
    CRYPTO_CURRENCIES: Tuple[str, ...] = ("BTC", "ETH", "SOL")
    CRYPTO_ID_MAP: dict = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
    }
    
    #пути
    RATES_FILE_PATH: str = 'data/rates.json'
    HISTORY_FILE_PATH: str = 'data/exchange_rates.json'
    
    #сетевые параметры
    REQUEST_TIMEOUT: int = 10 

parser_config = ParserConfig()

#проверяем наличие ключа
if not parser_config.EXCHANGERATE_API_KEY:
    raise ValueError(
        'Ошибка: Переменная окружения "EXCHANGERATE_API_KEY" не установлена!'
    )
