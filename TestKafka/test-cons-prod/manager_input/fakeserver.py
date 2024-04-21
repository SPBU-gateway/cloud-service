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
    
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from consumer import start_consumer
from producer import start_producer
from multiprocessing import Queue

if __name__ == "__main__":
    # Parse the command line.
    parser = ArgumentParser()
    parser.add_argument('config_file', type=FileType('r'))
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()
    

    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)
    config = dict(config_parser['default'])
    config.update(config_parser['manager'])

    requests_queue = Queue()

    start_consumer(args, config)
    start_producer(args, config, requests_queue)