#создаем декоратор, который и будет использовать логгер

import inspect
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def log_action(verbose: bool = False):
    def decorator(func):
        
        #сохраняем метаданные
        @wraps(func)
        def wrapper(*args, **kwargs):
            
            #собираем нужную информацию
            log_data = {}
            action_name = func.__name__.upper()
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            #и заполняем log_data
            log_data['user_id'] = bound_args.arguments.get('user_id')
            log_data['username'] = bound_args.arguments.get('username')
            log_data['currency'] = (bound_args.arguments.get('currency_to_buy') or 
                                    bound_args.arguments.get('currency_to_sell') or
                                    bound_args.arguments.get('currency_code_to_sell'))
            log_data['amount'] = bound_args.arguments.get('amount')
            
            #пытаемся выполнить функцию
            try:
                result_value = func(*args, **kwargs)
                log_data['result'] = 'OK'
                if verbose:
                    log_data['details'] = str(result_value)

                return result_value
                
            #а тут обрабатываем исключения
            except Exception as e:
                # --- 3. Обработка исключений ---
                log_data['result'] = 'ERROR'
                log_data['error_type'] = type(e).__name__
                log_data['error_message'] = str(e)
                raise
                
            finally:
            
                #собираем и запиываем лог
                #(она происходит вне зависимости, была ли ошибка)
                log_message_parts = [
                    action_name,
                    f'user="{log_data.get('username') or log_data.get('user_id')}"',
                ]
                if log_data.get('currency'):
                    log_message_parts.append(f'currency="{log_data['currency']}"')
                    
                
                log_message_parts.append(f"result={log_data['result']}")
                if log_data['result'] == 'ERROR':
                    log_message_parts.append(f'error="{log_data['error_type']}: {log_data['error_message']}"')
                if verbose and log_data.get('details'):
                    log_message_parts.append(f'details="{log_data['details']}"')

                final_log_message = " ".join(log_message_parts)
                
                logger.info(final_log_message)

        return wrapper
    return decorator
