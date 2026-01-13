import hashlib
import os
import time
from datetime import datetime

#импорт SettingsLoader
from valutatrade_hub.infra.settings import settings_loader

#импорт декоратора
from valutatrade_hub.decorators import log_action
from .utils import read_json, write_json

from .currencies import get_currency
from .models import Portfolio

from .exceptions import (
    InsufficientFundsError,
    CurrencyNotFoundError,
    ApiRequestError
)

#регистрация пользователя
@log_action()
def register_user(username, password):

    #теперь получаем пути не из констант
    #как было раньше
    data_path = settings_loader.get("data_path", "data")
    users_filename = settings_loader.get("users_filename", "users.json")
    portfolios_filename = settings_loader.get("portfolios_filename", "portfolios.json")

    users_file_path = os.path.join(data_path, users_filename)
    portfolios_file_path = os.path.join(data_path, portfolios_filename)

    #проверяем длину пароля
    if len(password) < 4:
        return 'Ошибка: Пароль должен быть не короче 4 символов'

    #читаем то, что уже есть в файле
    users = read_json(users_file_path)

    #проверяем уникальность
    for user in users:
        if user['username'] == username:
            return f'Ошибка: Имя пользователя "{username}" уже занято'

    #создаем нового юзера
    new_user_id = max([user['user_id'] for user in users]) + 1 if users else 1
    
    #генерируем "соль" для пароля
    salt = str(time.time())
    
    #шифруем пароль
    password_with_salt = password + salt
    hashed_password = hashlib.sha256(password_with_salt.encode('utf-8')).hexdigest()

    #собираем всё в словарь
    new_user = {
        'user_id': new_user_id,
        'username': username,
        'hashed_password': hashed_password,
        'salt': salt,
        'registration_date': datetime.now().isoformat()
    }

    #сохраняем и записываем в файл
    users.append(new_user)
    write_json(users_file_path, users)

    #создаем ему портфель
    portfolios = read_json(portfolios_file_path)
    new_portfolio = {
        'user_id': new_user_id,
        'wallets': {}
    }
    portfolios.append(new_portfolio)
    write_json(portfolios_file_path, portfolios)

    #возвращаем сообщение о том, что всё получилось
    return f'Пользователь "{username}" зарегистрирован (id={new_user_id}). Войдите: login --username {username} --password ****'

#вход пользователя
@log_action()
def login_user(username, password):

    #теперь получаем пути не из констант
    #как было раньше
    data_path = settings_loader.get("data_path", "data")
    users_filename = settings_loader.get("users_filename", "users.json")
    users_file_path = os.path.join(data_path, users_filename)

    #читаем файл и ищем пользователя по имени
    users = read_json(users_file_path)
    user_to_login = None
    for user_data in users:
    
        #eсли нашли
        if user_data['username'] == username:
            user_to_login = user_data
            break

    #если не нашли - пользователя не существует
    if not user_to_login:
        return (f'Ошибка: Пользователь "{username}" не найден', None)

    #cравниваем хеш пароля
    salt = user_to_login['salt']
    stored_hashed_password = user_to_login['hashed_password']
    password_with_salt = password + salt
    hashed_password_to_check = hashlib.sha256(password_with_salt.encode('utf-8')).hexdigest()
    if hashed_password_to_check != stored_hashed_password:
        
        #если не совпали
        return ('Ошибка: Неверный пароль', None)
        
    return (f'Вы вошли как "{username}"', user_to_login)
    

#смотрим портфолио
def show_portfolio(user_id, username, base_currency='USD'):

    #теперь получаем пути не из констант
    #как было раньше
    data_path = settings_loader.get("data_path", "data")
    portfolios_filename = settings_loader.get("portfolios_filename", "portfolios.json")
    rates_filename = settings_loader.get("rates_filename", "rates.json")
    portfolios_file_path = os.path.join(data_path, portfolios_filename)
    rates_file_path = os.path.join(data_path, rates_filename)

    #читаем нужные файлы
    base_currency = base_currency.upper()
    portfolios = read_json(portfolios_file_path)
    rates_data = read_json(rates_file_path, default_data={})
    
    #создаем словарь с курсами относительно (доллара)
    exchange_rates = { 'USD': 1.0 }
    for key, value in rates_data.get('rates', {}).items():
        currency_code = key.split('_')[0]
        exchange_rates[currency_code] = value['rate']

    if base_currency not in exchange_rates:
        return f'Ошибка: Неизвестная базовая валюта "{base_currency}"'
        
    #ищем портфель
    user_portfolio = None
    for p in portfolios:
        if p['user_id'] == user_id:
            user_portfolio = p
            break
            
    #если нет портфеля
    if not user_portfolio or not user_portfolio['wallets']:
        return f'У пользователя "{username}" пока нет кошельков.'
        
    #расчеты
    output_lines = []
    total_value_in_base = 0.0
    base_rate_to_usd = exchange_rates[base_currency]

    #идем по каждому кошельку в портфеле
    for currency, wallet_data in user_portfolio['wallets'].items():
        balance = wallet_data.get('balance', 0.0)
        current_rate_to_usd = exchange_rates.get(currency, 0.0)
        
        #если для валюты нет курса - не можем посчитать
        if current_rate_to_usd == 0.0 and currency != 'USD':
            line = f'- {currency}: {balance:,.4f}  → (нет данных о курсе)'
            
        #если всё норм - делаем расчеты и выводим
        else:
            value_in_usd = balance * current_rate_to_usd
            value_in_base = value_in_usd / base_rate_to_usd
            total_value_in_base += value_in_base
            line = f'- {currency}: {balance:,.4f}  → {value_in_base:,.2f} {base_currency}'
        output_lines.append(line)
    
    #для более красивого вывода воспользовался ии
    #извините, до этого выводилось вообще некрасиво
    header = f'Портфель пользователя "{username}" (база: {base_currency}):'
    separator = '-' * (len(header) if len(header) > 25 else 25)
    footer = f'ИТОГО: {total_value_in_base:,.2f} {base_currency}'
    
    # Собираем все строки в один большой текст
    final_output = "\n".join([header] + output_lines + [separator, footer])
    
    return final_output
    

#покупаем валюту
@log_action()
def buy_currency(user_id, currency_to_buy, amount):

    #смотрим валюту через наше хранилище
    currency_obj = get_currency(currency_to_buy)
    
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError('"amount" должен быть положительным числом')

    #получаем пути
    data_path = settings_loader.get('data_path', 'data')
    portfolios_file_path = os.path.join(data_path, settings_loader.get('portfolios_filename'))
    portfolios = read_json(portfolios_file_path)

    #ищем портфель
    user_portfolio_dict = None
    portfolio_index = -1
    for i, p in enumerate(portfolios):
        if p.get('user_id') == user_id:
            user_portfolio_dict = p
            portfolio_index = i
            break
    
    if not user_portfolio_dict:
        raise 'ошибка: портфель пользователя не найден.'
    portfolio_obj = Portfolio(user_id, user_portfolio_dict['wallets'])
    
    #получаем (или создаем) кошелек
    wallet_obj = portfolio_obj.get_wallet(currency_obj.code)
    if not wallet_obj:
        portfolio_obj.add_currency(currency_obj.code)
        wallet_obj = portfolio_obj.get_wallet(currency_obj.code)
    
    old_balance = wallet_obj.balance
    
    wallet_obj.deposit(amount)
    new_balance = wallet_obj.balance

    #сохраняем покупку и выводим
    updated_wallets_dict = {code: {'balance': wallet.balance} for code, wallet in portfolio_obj.wallets.items()}
    portfolios[portfolio_index]['wallets'] = updated_wallets_dict
    write_json(portfolios_file_path, portfolios)

    report = (
        f"Покупка выполнена: {amount:,.4f} {currency_obj.code}\n"
        f"Изменения в портфеле:\n"
        f"- {currency_obj.code}: было {old_balance:,.4f} → стало {new_balance:,.4f}"
    )
    return report
    
#продаем валюту
@log_action()
def sell_currency(user_id, currency_to_sell, amount):

    #теперь получаем пути не из констант
    #как было раньше
    data_path = settings_loader.get("data_path", "data")
    portfolios_filename = settings_loader.get("portfolios_filename", "portfolios.json")
    rates_filename = settings_loader.get("rates_filename", "rates.json")
    portfolios_file_path = os.path.join(data_path, portfolios_filename)
    rates_file_path = os.path.join(data_path, rates_filename)

    #приводим к унифицированному виду валюту
    currency_to_sell = currency_to_sell.upper()
    
    try:
        amount = float(amount)
        if amount <= 0:
            return 'Ошибка: "amount" должен быть положительным числом'
    except (ValueError, TypeError):
        return 'Ошибка: "amount" должен быть числом'

    #читаем данные
    portfolios = read_json(portfolios_file_path)
    rates_data = read_json(rates_file_path, default_data={})

    #получаем курсы валют
    exchange_rates = { 'USD': 1.0 }
    for key, value in rates_data.get('rates', {}).items():
        currency_code = key.split('_')[0]
        exchange_rates[currency_code] = value['rate']
    
    current_rate = exchange_rates.get(currency_to_sell)
    
    #добавляем исключение
    if not current_rate:
        raise ApiRequestError(f'Не удалось получить курс для {currency_code_to_sell} → USD')


    user_portfolio = None
    portfolio_index = -1
    for i, p in enumerate(portfolios):
        if p['user_id'] == user_id:
            user_portfolio = p
            portfolio_index = i
            break
            
    #проверяем наличие портфеля       
    if not user_portfolio:
        return 'ошибка: портфель пользователя не найден.'

    #проверяем, существует ли кошелек
    if currency_to_sell not in user_portfolio['wallets']:
        return f'Ошибка: У вас нет кошелька "{currency_to_sell}". Вы не можете продать то, чего у вас нет.'
        
    current_balance = user_portfolio['wallets'][currency_to_sell].get('balance', 0.0)
    
    #проверка на достаточность средств
    #добавляем исключение
    if amount > current_balance:
        return InsufficientFundsError(
            available=current_balance,
            required=amount,
            code=currency_code_to_sell
        )

    #обновляем балансы
    new_balance = current_balance - amount
    user_portfolio['wallets'][currency_to_sell]['balance'] = new_balance
    
    revenue_in_usd = amount * current_rate
    usd_balance = user_portfolio['wallets'].get('USD', {'balance': 0.0}).get('balance', 0.0)
    user_portfolio['wallets']['USD'] = {'balance': usd_balance + revenue_in_usd}
    
    #сохраняем
    portfolios[portfolio_index] = user_portfolio
    write_json(portfolios_file_path, portfolios)
    
    #выводим
    report = (
        f"Продажа выполнена: {amount:,.4f} {currency_to_sell} по курсу {current_rate:,.2f} USD/{currency_to_sell}\n"
        f"Изменения в портфеле:\n"
        f"- {currency_to_sell}: было {current_balance:,.4f} → стало {new_balance:,.4f}\n"
        f"Оценочная выручка: {revenue_in_usd:,.2f} USD (зачислено на USD кошелек)"
    )
    
    return report
    

#получаем курсы по обмену валют
def get_exchange_rate(from_currency, to_currency):

    #теперь получаем пути не из констант
    #как было раньше
    data_path = settings_loader.get("data_path", "data")
    rates_filename = settings_loader.get("rates_filename", "rates.json")
    rates_file_path = os.path.join(data_path, rates_filename)

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    if from_currency == to_currency:
        return f'Курс {from_currency}→{to_currency}: 1.0'

    #читаем данные
    rates_data = read_json(rates_file_path, default_data={})
    
    #создаем словарь по отношению к доллару
    exchange_rates_to_usd = {'USD': 1.0}
    for key, value in rates_data.get('rates', {}).items():
        currency_code = key.split('_')[0]
        exchange_rates_to_usd[currency_code] = value['rate']

    #проверяем, есть ли такой курс в словаре
    if from_currency not in exchange_rates_to_usd:
        # Если курса нет, выбрасываем ошибку, как будто API его не предоставил.
        raise ApiRequestError(f"Курс для '{from_currency}' недоступен.")
    if to_currency not in exchange_rates_to_usd:
        raise ApiRequestError(f"Курс для '{to_currency}' недоступен.")
        
        
    #рассчитываем "перекрестные" курсы (или как их назвать..)    
    from_rate_vs_usd = exchange_rates_to_usd[from_currency]
    to_rate_vs_usd = exchange_rates_to_usd[to_currency]
    final_rate = from_rate_vs_usd / to_rate_vs_usd
    reverse_rate = to_rate_vs_usd / from_rate_vs_usd

    #реализуем время обновления
    last_update_str = rates_data.get('last_refresh', 'N/A')
    try:
        last_update_dt = datetime.fromisoformat(last_update_str)
        formatted_time = last_update_dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        formatted_time = 'неизвестно'
        
    #выводим
    report = (
        f"Курс {from_currency}→{to_currency}: {final_rate:,.8f} (обновлено: {formatted_time})\n"
        f"Обратный курс {to_currency}→{from_currency}: {reverse_rate:,.2f}"
    )
    
    return report 
