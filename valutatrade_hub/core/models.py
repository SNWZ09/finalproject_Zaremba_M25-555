#библиотека для хеширования паролей
import hashlib
from datetime import datetime

#импортируем сделанные исключения
from .exceptions import InsufficientFundsError


#создаем класс 'пользователь системы'
class User:
    def __init__(self, user_id, username, hashed_password, salt, registration_date):
        
        #делаем все атрибуты приватными
        self._user_id = user_id
        self._username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = datetime.fromisoformat(registration_date)
        
    #реализуем геттеры, что получать значения из переменных
    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def registration_date(self) -> datetime:
        return self._registration_date

    #реализуем сеттер для имени пользователя
    @username.setter
    def username(self, new_username):
        if not new_username:
            print('Ошибка: Имя пользователя не может быть пустым!')
            
        else:
            self._username = new_username
            print(f'Имя пользователя изменено на: {new_username}')
            
            
    #метод для показа данных пользователя
    def show_user_info(self):
        print(f'ID: {self._user_id}')
        print(f'Имя: {self._username}')
        print(f'Дата регистрации: {self._registration_date}')

    #метод смены пароля
    def change_password(self, new_password):
        
        #проверяем, что он больше 4 символов
        if len(new_password) < 4:
            print('Ошибка: Пароль должен быть не менее 4 символов.')
            return

        #складываем пароль и "соль" в одну строку
        password_with_salt = new_password + self._salt
        
        #превращаем строку в байты
        encoded_string = password_with_salt.encode('utf-8')
        
        #хешируем
        new_hashed_password = hashlib.sha256(encoded_string).hexdigest()
        
        self._hashed_password = new_hashed_password
        
        print(f'Пароль для пользователя "{self._username}" был успешно изменен.')

    #метод проверяет введённый пароль на совпадение.
    def verify_password(self, password_to_check):
        password_with_salt = password_to_check + self._salt
        
        #превращаем строку в байты
        encoded_string = password_with_salt.encode('utf-8')
        hashed_password_to_check = hashlib.sha256(encoded_string).hexdigest()

        #cравниваем
        if hashed_password_to_check == self._hashed_password:
            return True
        else:
            return False
            
            
#создаем класс 'кошелёк пользователя для одной конкретной валюты'
class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code
        self.balance = balance
            
    #геттер
    #'-> float' добавил. В интернете сказали, что нужно делать подсказку типа
    @property
    def balance(self) -> float:
        return self._balance

    #сеттер
    @balance.setter
    def balance(self, value: float):

        #проверка на отриц. значения и некорректные типы
        if not isinstance(value, (int, float)):
            raise TypeError('Баланс должен быть числом.')
        
        if value < 0:
            raise ValueError('Баланс не может быть отрицательным.')
            
        self._balance = float(value)

    #метод пополнения баланса
    def deposit(self, amount: float):
    
        #проверка на отриц. значения и некорректные типы
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError('Сумма пополнения должна быть положительной.')
            
        #увеличиваем баланс
        self._balance += amount
        print(f'Баланс {self.currency_code} пополнен на {amount}. Новый баланс: {self.balance}')

    #метод снятия 'money'
    def withdraw(self, amount: float):
    
        #проверка на отриц. значения и некорректные типы
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError('Сумма снятия должна быть положительной.')
        
        #проверяем, есть ли на счету средства для снятия
        #используем сделанное исключение
        if amount > self.balance:
            raise InsufficientFundsError(
                available=self.balance, 
                required=amount, 
                code=self.currency_code
            )     
                
        self._balance -= amount
        print(f'Со счета {self.currency_code} списано {amount}. Новый баланс: {self.balance}')
    
    #метод вывода информации о кошельке
    def get_balance_info(self):
        print(f'Кошелек: {self.currency_code}, Баланс: {self.balance}')
        

#создаем класс 'управление всеми кошельками одного пользователя'
class Portfolio:
    def __init__(self, user_id: int, wallets_data: dict):
        self._user_id = user_id
        
        #словарь для кошельков
        self._wallets: dict[str, Wallet] = {}
        
        #превращаем информацию в словарь
        for currency_code, wallet_info in wallets_data.items():
            balance = wallet_info.get("balance", 0.0)
            new_wallet = Wallet(currency_code=currency_code, balance=balance)
            self._wallets[currency_code] = new_wallet

    #геттеры
    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def wallets(self) -> dict[str, Wallet]:
        
        #возвращаем копию нашего словаря
        return self._wallets.copy()

    #метод для добавления нового кошелька в портфель
    def add_currency(self, currency_code: str):

        #на всякий случай приводим к общему виду код валюты
        currency_code = currency_code.upper()
        
        #проверяем, существует ли кошелек с такой валютой в портфеле
        if currency_code in self._wallets:
            raise ValueError(f'Кошелек для валюты {currency_code} уже существует в этом портфеле.')
        
        #создаем и добавляем в словарь
        new_wallet = Wallet(currency_code=currency_code, balance=0.0)
        self._wallets[currency_code] = new_wallet
        print(f'Новый кошелек для валюты {currency_code} успешно добавлен в портфель.')

    #метод получания объекта Wallet по коду валюты
    def get_wallet(self, currency_code: str) -> Wallet | None:
        currency_code = currency_code.upper()
        
        return self._wallets.get(currency_code)

    #метод возвращает общую стоимость всех валют пользователя
    #в указанной базовой валюте
    #по курсам, полученным из API или фиктивным данным
    def get_total_value(self, base_currency: str = 'USD') -> float:

        exchange_rates = {
            'USD': 1.0,
            'EUR': 1.16,     
            'BTC': 93583.09, 
            'RUB': 0.013,    
            'ETH': 3188.51 
        }
        
        base_currency = base_currency.upper()
        if base_currency not in exchange_rates:
            raise ValueError(f'Невозможно рассчитать стоимость в {base_currency}: нет данных о курсе.')

        total_value_in_usd = 0.0
        
        #проходим по каждому кошельку в портфеле
        for wallet in self._wallets.values():
            if wallet.currency_code in exchange_rates:
                #конвертируем
                rate = exchange_rates[wallet.currency_code]
                total_value_in_usd += wallet.balance * rate
            else:
                print(f'Предупреждение: Нет курса для {wallet.currency_code}. Валюта не будет учтена.')
        
        #конвертируем итоговую сумму из USD в требуемую валюту
        base_rate = exchange_rates[base_currency]
        final_total_value = total_value_in_usd / base_rate
        
        return final_total_value
