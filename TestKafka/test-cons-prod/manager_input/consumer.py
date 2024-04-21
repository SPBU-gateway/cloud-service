from confluent_kafka import Consumer, OFFSET_BEGINNING
import threading
import json
from producer import proceed_to_deliver
from typing import Dict


#### ------------------------------------------------------------------
# Идейно: consumer получает какие то сообщения
# Сообщения имеют какие то темы, называемые Топиками (topics).
# Consumer "подписыватся" на сообщения, содержащие какие то топики
# Пусть пишем consumer для компоненты manager_input

example_config = {
    'bootstrap.servers': 'kafka-1:9192', # сервер кафки
    'group.id': 'update_demo_manager',
    'auto.offset.reset': 'earliest'  # начальная точка чтения (earliest or latest)
}

def handle_event(id: str, details: Dict):
    """
        Функция обрабатывает ивент
    """
    
    delivery_required = False   # Нужно ли потом перенаправить сообщение. Если нужно, то смотреть последний if в этой функции
    # Посмотрим детали ивента
    print(f"[debug] handling event {id}, {details}")
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    
    # В зависимости от того, какой тип операции, отправляем на соответсвующую компоненту с соответсвующим названием операции
    # Например
    if details['operation'] == 'download_done':
        # update downloaded, now shall store
        details['operation'] = 'commit_blob'
        details['deliver_to'] = 'storage'
        delivery_required = True                

    if details['operation'] == 'blob_committed':
        pass

    if details['operation'] == 'handle_verification_result':
        if details['verified'] is True:
            pass
        else:
            pass # Выдать ошибку

    if delivery_required:
        # Эта функция из producerа. По сути передаем обработанное сообщение producerу, который его потом перенаправит
        proceed_to_deliver(id, details)
        

def consumer_job(args, config: Dict, topic: str):
    # topic можем как и указать в функции, так и получить его извне
    
    manager_consumer = Consumer(config)
    
    # Начать ли считывать заново
    # partitions - по сути разделы (потоки) каждой темы
    def reset_offset(manager_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING   # перевод в начало
            manager_consumer.assign(partitions)
    
    manager_consumer.subscribe([topic], on_assign=reset_offset)
    
    # Получим сообщения
    try:
        while True:
            msg = manager_consumer.poll(1.0)
            if msg is None:   # Сообщений нет
                continue
            elif msg.error():   # Ошибка в сообщении
                print(f"[error] {msg.error()}") 
            else:   # Обрабатываем сообщение
                try:
                    id = msg.key().decode('utf-8')
                    details = json.loads(msg.value().decode('utf-8'))
                    handle_event(id, details)
                except Exception as e:
                    print(
                        f"[error] malformed event received from topic {topic}: {msg.value()}. {e}")    
    except KeyboardInterrupt:
        pass
    finally:
        # Покидаем группу и коммитим последние смещения
        manager_consumer.close()    
        

def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(args, config, 'manager')).start()


if __name__ == '__main__':
    start_consumer()