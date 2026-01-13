import shlex

#импортируем нашу функцию с бизнес-логикой
from valutatrade_hub.core.usecases import(
    register_user, 
    login_user, 
    show_portfolio, 
    buy_currency, 
    sell_currency, 
    get_exchange_rate
)

def main():

    print("Вы находитесь в ValutaTrade HUB!")
    print("Доступные команды: register, login, show-portfolio, buy, sell, get-rate, exit")
    
    while True:
    
        #принимаем команду от пользователя
        raw_command = input("> ")
        
        #разделяем на части
        try:
            command_parts = shlex.split(raw_command)
        except ValueError:
            print('Ошибка: В команде есть незакрытые кавычки.')
            continue

        #если ввели пустую строку - ничего не делаем
        if not command_parts:
            continue

        #разделяем команду и аргументыф
        main_command = command_parts[0]
        args = command_parts[1:]
        
        if main_command == 'exit':
            print('До свидания')
            break
            
        #команда регистрации
        elif main_command == 'register':
            username = None
            password = None
            
            #парсер
            try:
                for i, arg in enumerate(args):
                    if arg == '--username':
                        username = args[i+1]
                    elif arg == '--password':
                        password = args[i+1]
            except IndexError:
                print('Ошибка: не указано значение для --username или --password.')
                continue

            if not username or not password:
                print('Использование: register --username <имя> --password <пароль>')
                continue
                
            #вызываем функцию из usecases.py
            result = register_user(username, password)
            print(result)
        
        #команда логина
        elif main_command == 'login':
            username = None
            password = None

            try:
                for i, arg in enumerate(args):
                    if arg == '--username':
                        username = args[i+1]
                    elif arg == '--password':
                        password = args[i+1]
            except IndexError:
                print('Ошибка: не указано значение для --username или --password.')
                continue

            if not username or not password:
                print('Использование: login --username <имя> --password <пароль>')
                continue

            #вызываем функцию логина
            message, user_data = login_user(username, password)
            
            #печатаем результат
            print(message)
            
            #сохраняем данные текущей сессии
            if user_data:
                current_user_session = user_data
         
        #команда показать портфолио 
        elif main_command == 'show-portfolio':
            
            #проверяем, активна ли сессия
            if not current_user_session:
                print('Ошибка: Сначала выполните login')
                continue
                
            base_currency = 'USD'
            
            if '--base' in args:
                try:
                    base_index = args.index('--base') + 1
                    base_currency = args[base_index]
                    
                #предусмотрим вывод ошибки,
                #если юзер не ввел флаг базовой валюты
                except IndexError:
                    print('Ошибка: не указана валюта для флага --base')
                    continue
            
            user_id = current_user_session['user_id']
            username = current_user_session['username']
            
            #печатаем результат
            result = show_portfolio(user_id, username, base_currency)
            print(result)
            
        
        #команда купить 
        elif main_command == 'buy':
        
            #проверяем, активна ли сессия
            if not current_user_session:
                print('Ошибка: Сначала выполните login')
                continue
                
            currency = None
            amount = None
            
            try:
                for i, arg in enumerate(args):
                    if arg == '--currency':
                        currency = args[i+1]
                    elif arg == '--amount':
                        amount = args[i+1]
            except IndexError:
                print('Ошибка: не указано значение для --currency или --amount.')
                continue

            if not currency or not amount:
                print('Использование: buy --currency <код_валюты> --amount <количество>')
                continue

            #вызываем функцию и передаем юзера
            user_id = current_user_session['user_id']
            result = buy_currency(user_id, currency, amount)
            print(result)
            
        #команда продать
        elif main_command == 'sell':
            #проверяем, активна ли сессия
            if not current_user_session:
                print('Ошибка: Сначала выполните login')
                continue
                
            currency = None
            amount = None
            
            try:
                for i, arg in enumerate(args):
                    if arg == '--currency':
                        currency = args[i+1]
                    elif arg == '--amount':
                        amount = args[i+1]
            except IndexError:
                print('Ошибка: не указано значение для --currency или --amount.')
                continue

            if not currency or not amount:
                print('Использование: sell --currency <код_валюты> --amount <количество>')
                continue
                
            #вызываем функцию и передаем юзера
            user_id = current_user_session['user_id']
            result = sell_currency(user_id, currency, amount)
            print(result)
            
        #команда узнать курс
        elif main_command == 'get-rate':
        
            #тут, кстати, сессию не проверяем
            #(ура!!!!!!!!!!!)
            from_curr = None
            to_curr = None
            
            try:
                for i, arg in enumerate(args):
                    if arg == '--from':
                        from_curr = args[i+1]
                    elif arg == '--to':
                        to_curr = args[i+1]
            except IndexError:
                print('Ошибка: не указано значение для --from или --to.')
                continue

            if not from_curr or not to_curr:
                print('Использование: get-rate --from <валюта> --to <валюта>')
                continue

            # Вызываем функцию из usecases и печатаем результат
            result = get_exchange_rate(from_curr, to_curr)
            print(result)
        

        else:
            print(f'Неизвестная команда: "{main_command}"')



if __name__ == '__main__':
    main()


