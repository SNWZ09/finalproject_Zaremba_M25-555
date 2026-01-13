#импортируем для задачи
#Описать ABC Currency (без реализации логики, только требования)
from abc import ABC, abstractmethod

#импорт исключения
from .exceptions import CurrencyNotFoundError


class Currency(ABC):
    def __init__(self, name: str, code: str):
        if not isinstance(name, str) or not name:
            raise ValueError('Атрибут "name" должен быть непустым.')
        
        if not isinstance(code, str) or not (2 <= len(code) <= 5) or ' ' in code:
            raise ValueError('Атрибут "code" должен быть строкой от 2 до 5 символов без пробелов.')

        self.name = name
        self.code = code.upper()

    
    @abstractmethod
    def get_display_info(self) -> str:

        pass

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(code="{self.code}")'


#наследник 1
class FiatCurrency(Currency):
    def __init__(self, name: str, code: str, issuing_country: str):
    
        #вызываем конструктор род. класса
        super().__init__(name, code)
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        return (f'[FIAT] {self.code} — {self.name} '
                f'(Issuing: {self.issuing_country})')

#наследник 2
class CryptoCurrency(Currency):
    def __init__(self, name: str, code: str, algorithm: str, market_cap: float):
        
        #вызываем конструктор род. класса
        super().__init__(name, code)
        self.algorithm = algorithm
        self.market_cap = market_cap

    def get_display_info(self) -> str:
        return (f'[CRYPTO] {self.code} — {self.name} '
                f'(Algo: {self.algorithm}, MCAP: {self.market_cap:.2e})')


#приватное хранилище наших валют
_CURRENCY_REGISTRY: dict[str, Currency] = {
    'USD': FiatCurrency(name='US Dollar', code='USD', issuing_country='United States'),
    'EUR': FiatCurrency(name='Euro', code='EUR', issuing_country='Eurozone'),
    'RUB': FiatCurrency(name='Russian Ruble', code='RUB', issuing_country='Russia'),
    'BTC': CryptoCurrency(name='Bitcoin', code='BTC', algorithm='SHA-256', market_cap=1.3e12),
    'ETH': CryptoCurrency(name='Ethereum', code='ETH', algorithm='Ethash', market_cap=4.0e11),
}


#фабрика для получения валюты по коду
def get_currency(code: str) -> Currency:
    code = code.upper()
    currency_object = _CURRENCY_REGISTRY.get(code)
    
    if not currency_object:
        raise CurrencyNotFoundError(f'Валюта с кодом "{code}" не найдена в реестре.')
        
    return currency_object
