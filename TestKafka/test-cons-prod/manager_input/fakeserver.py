import random
import time


# Этот файл имитирует работу какого-то сервиса 
def create_device():
    """
        Генерирует рандомный девайс
    """
    return {
        'device_name': 'device_' + str(random.randint(1, 100)),
        'category_name': 'category_' + str(random.randint(1, 100)),
        'device_ip': '192.0.0.' + str(random.randint(1, 9)),
        'time_created': int(time.time())
    }
    
