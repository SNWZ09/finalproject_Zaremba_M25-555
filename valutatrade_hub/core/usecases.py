import hashlib
import os
import time
from datetime import datetime, timedelta

#импорт декоратора
from valutatrade_hub.decorators import log_action

#импорт SettingsLoader
from valutatrade_hub.infra.settings import settings_loader

from .currencies import get_currency
from .exceptions import ApiRequestError
from .models import Portfolio
from .utils import read_json, write_json


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
    return f'"{username}" зарегистрирован (id={new_user_id}). Войдите: login --username {username} --password ****'

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
def buy_currency(user_id, currency_code, amount):

    #смотрим валюту через наше хранилище
    currency_obj = get_currency(currency_code)
    
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
def sell_currency(user_id, currency_code, amount):

    #смотрим валюту через наше хранилище
    currency_obj = get_currency(currency_code)
    
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
    user_portfolio_dict = next((p for p in portfolios if p.get('user_id') == user_id), None)
    if not user_portfolio_dict:
        raise 'ошибка: портфель пользователя не найден.'

    portfolio_obj = Portfolio(user_id, user_portfolio_dict['wallets'])
    
    wallet_to_sell = portfolio_obj.get_wallet(currency_obj.code)
    if not wallet_to_sell:
        raise f'У вас нет кошелька "{currency_obj.code}".'
        
    wallet_to_sell.withdraw(amount)

    #сохраняем и выводим
    portfolio_index = portfolios.index(user_portfolio_dict)
    updated_wallets_dict = {code: {'balance': wallet.balance} for code, wallet in portfolio_obj.wallets.items()}
    portfolios[portfolio_index]['wallets'] = updated_wallets_dict
    write_json(portfolios_file_path, portfolios)

    return f'Продажа {amount:,.4f} {currency_obj.code} прошла успешно.'
    

#получаем курсы по обмену валют
def get_exchange_rate(from_code, to_code):

    #смотрим валюту через наше хранилище
    from_curr_obj = get_currency(from_code)
    to_curr_obj = get_currency(to_code)

    #если одинаковые
    if from_curr_obj.code == to_curr_obj.code:
        return f'Курс {from_curr_obj.code}→{to_curr_obj.code}: 1.0'

    #получаем пути
    data_path = settings_loader.get('data_path', 'data')
    rates_file_path = os.path.join(data_path, settings_loader.get('rates_filename'))
    rates_ttl_seconds = settings_loader.get('rates_ttl_seconds', 300)

    #проверяем "свежесть" кэша
    #(прошло ли 300 сек)
    rates_data = read_json(rates_file_path, default_data={})
    last_refresh_str = rates_data.get('last_refresh')
    
    if last_refresh_str:
        last_refresh_dt = datetime.fromisoformat(last_refresh_str)
        
        #если кэш устарел
        if datetime.now() - last_refresh_dt > timedelta(seconds=rates_ttl_seconds):
            raise ApiRequestError('Данные о курсах устарели, не удалось обновить.')
    
    #кросс-курс
    exchange_rates_to_usd = {'USD': 1.0}
    for key, value in rates_data.get('rates', {}).items():
        exchange_rates_to_usd[key.split('_')[0]] = value['rate']
        
    from_rate = exchange_rates_to_usd.get(from_curr_obj.code)
    to_rate = exchange_rates_to_usd.get(to_curr_obj.code)

    if from_rate is None or to_rate is None:
        raise ApiRequestError(f'Недостаточно данных для расчета курса {from_code}->{to_code}')

    final_rate = from_rate / to_rate
    reverse_rate = to_rate / from_rate
    
    #вывод
    report = (
        f"Курс {from_curr_obj.code}→{to_curr_obj.code}: {final_rate:,.8f} (обновлено: {last_refresh_str})\n"
        f"Обратный курс {to_curr_obj.code}→{from_curr_obj.code}: {reverse_rate:,.2f}"
    )
    
    return report
    
    
