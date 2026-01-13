import logging
from abc import ABC, abstractmethod
from typing import Dict

import requests

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.config import parser_config

#логгер
logger = logging.getLogger(__name__)


#создаем абстрактный базовый класс
#с единым методом
class BaseApiClient(ABC):

    @abstractmethod
    
    #Dict[str, float] 
    #потому что будет иметь вид
    #{"BTC_USD": 59337.21, ...}
    def fetch_rates(self) -> Dict[str, float]:
        pass

class CoinGeckoClient(BaseApiClient):
    def fetch_rates(self) -> Dict[str, float]:
        
        #получаем ссылку
        ids_to_fetch = [
            parser_config.CRYPTO_ID_MAP[code]
            for code in parser_config.CRYPTO_CURRENCIES
            if code in parser_config.CRYPTO_ID_MAP
        ]
        
        params = {
            'ids': ",".join(ids_to_fetch),
            'vs_currencies': parser_config.BASE_CURRENCY.lower()
        }

        logger.info(f'CoinGecko: Запрос курсов для {params['ids']}')

        #отправляем запрос
        try:
            response = requests.get(
                parser_config.COINGECKO_URL,
                params=params,
                timeout=parser_config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
        
            raw_data = response.json()
            logger.debug(f'CoinGecko: Получен ответ: {raw_data}')

        except requests.exceptions.RequestException as e:
            #получаем сетевые ошибки
            #(вдруг возникнут)
            raise ApiRequestError(f'Сетевая ошибка при запросе к CoinGecko: {e}')

        standardized_rates = {}
        
        #создаем словарь
        reverse_id_map = {v: k for k, v in parser_config.CRYPTO_ID_MAP.items()}

        for api_id, rate_data in raw_data.items():
            ticker = reverse_id_map.get(api_id)
            
            #извлекаем курс к базовой валюте
            rate = rate_data.get(parser_config.BASE_CURRENCY.lower())

            if ticker and rate:
                key = f'{ticker}_{parser_config.BASE_CURRENCY}'
                standardized_rates[key] = float(rate)

        logger.info(f'CoinGecko: Успешно обработано {len(standardized_rates)} курсов.')
        return standardized_rates



class ExchangeRateApiClient(BaseApiClient):

    def fetch_rates(self) -> Dict[str, float]:
    
        #получаем ссылку
        url = (
            f'{parser_config.EXCHANGERATE_API_URL}/'
            f'{parser_config.EXCHANGERATE_API_KEY}/latest/'
            f'{parser_config.BASE_CURRENCY}'
        )
        
        logger.info(f'ExchangeRate-API: Запрос курсов относительно {parser_config.BASE_CURRENCY}')

        #отправляем запрос
        try:
            response = requests.get(url, timeout=parser_config.REQUEST_TIMEOUT)
            response.raise_for_status()
            raw_data = response.json()
            logger.debug(f'ExchangeRate-API: Получен ответ: {raw_data}')

        except requests.exceptions.RequestException as e:
            #получаем сетевые ошибки
            #(вдруг возникнут)
            raise ApiRequestError(f'Сетевая ошибка при запросе к ExchangeRate-API: {e}')
        

        #стандартизируем данные
        standardized_rates = {}
        api_rates = raw_data.get('rates', {})
        
        #берем валюты, которые у нас были изначально
        for code in parser_config.FIAT_CURRENCIES:
            rate = api_rates.get(code)
            if rate:
                key = f'{code}_{parser_config.BASE_CURRENCY}'
                standardized_rates[key] = float(rate)
        
        logger.info(f'ExchangeRate-API: Успешно обработано {len(standardized_rates)} курсов.')
        
        return standardized_rates


