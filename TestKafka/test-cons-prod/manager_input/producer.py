from confluent_kafka import Producer
import json
import multiprocessing
import threading
from typing import Dict, Any
import fakeserver
import time


# Параметры конфигурации producer (например адреса серверов)
# Снизу - пример конфига
# Вообще говоря, надо указывать cfg в отдельном файле config.ini
example_config = {
    'bootstrap.servers': 'kafka-1:9092', # сервер кафки
    'group.id': 'update_demo_manager',
    'auto.offset.reset': 'earliest'  # начальная точка чтения (earliest or latest)
}


#### ------------------------------------------------------------------
# Идейно: producer создает или отправляет какие то сообщения
# Сообщения имеют какие то темы, называемые Топиками (topics)
# Пусть пишем producer для компоненты, которую назовем manager_input (по сути это не так)

component = 'manager_input'   

# Создаём очередь

_requests_queue: multiprocessing.Queue = None


def proceed_to_deliver(id, details):
    # Функция добавляет сообщение в очередь на отправку
    print(f"[debug] Queueing for delivering the event: id={id}, payload={details}")
    details['source'] = component   # источник, какая часть сервиса отправляет сообщение
    _requests_queue.put(details)   # добавляем в очередь


def producer_job(_, config: Dict[str, Any], requests_queue: multiprocessing.Queue, topic: str):
    producer = Producer(config)
    
    
    def delivery_callback(err, msg):
        #    Данная функция - опциональна
        #   Нужна для отслеживания доставки сообщений
        if err:
            print(f'[error] Message of the failed delivery: {err}')
        else:
            print(f"[debug] Produced event: topic={msg.topic()}, key={msg.key()}, value={msg.value()}")
    
    while True:
        # ManagerInput не генерирует сообщения, а просто передает их, поэтому event_details выглядел бы следующим образом
        # event_details = requests_queue.get()   
        # Если бы это была другая компонента, которая, например, создает или меняет json, то могло бы быть
        event_details = fakeserver.create_device()
        
        event_details['source'] = component   # источник, откуда передаем сообщение
        # Создаем сообщение с данными
        producer.produce(topic, json.dumps(event_details), callback=delivery_callback)
        # Ожидание
        producer.poll(10000)
        producer.flush()
        time.sleep(1)


def start_producer(args, config, requests_queue):
    """
        Запуск producerа в асинхронном режиме в отдельном потоке
    """
    global _requests_queue
    _requests_queue = requests_queue
    threading.Thread(target=lambda: producer_job(args, config, requests_queue, 'manager')).start()


if __name__ == '__main__':
    start_producer(None, example_config, None)
    