#исключения


#для ситуации
#когда валюта с указанным кодом не найдена
class CurrencyNotFoundError(Exception):
    def __init__(self, code: str):
        super().__init__(f'Неизвестная валюта "{code}"')

#для ситуации
#когда недостаточно средств 
class InsufficientFundsError(Exception):
    def __init__(self, available: float, required: float, code: str):
        
        #сохраню сообщение в отдельную переменную
        #а то очень длинно и грязно получится
        # + ещё ruff ругаться будет на длину строки
        message = (
            f'Недостаточно средств: доступно {available:,.4f} {code}, '
            f'требуется {required:,.4f} {code}'
        )
        super().__init__(message)

#для ситуации
#когда произошел сбой внешнего API
class ApiRequestError(Exception):
    def __init__(self, reason: str):
        super().__init__(f'Ошибка при обращении к внешнему API: {reason}')




