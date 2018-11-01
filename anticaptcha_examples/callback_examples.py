import asyncio

import aiohttp
import requests
import pika
import time
import json

from python3_anticaptcha import NoCaptchaTaskProxyless, CallbackClient

ANTICAPTCHA_KEY = "ae23fffcfaa29b170e3843e3a486ef19"
QUEUE_KEY = 'wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ_anticaptcha_queue'

"""
Пример показывает работу с модулем CallbackClient на основе работы с NoCaptchaTaskProxyless 
(точно так же это работает со всеми остальными доступными методами решения капчи)
предназначенным для получения ответа не капчу высланного на callback сервер.
-------------------------------------------------------------
Все решения которые получает сервер записываются в:
1. RabbitMQ очередь, в которой сообщение после прочтения пользователем удаляется
2. Кеш(memcached) в котором сообщение хранится 1 час
"""

"""
Перед тем тем как начать пользоваться сервисом нужно создать для своей задачи отдельную очередь
Очередь можно создать один раз и пользоваться постоянно

Для создания очереди нужно передать два параметра:
1. key - название очереди, чем оно сложнее тем лучше
2. vhost - название виртуального хоста(в данном случаи - `anticaptcha_vhost`)
"""

answer = requests.post('http://85.255.8.26:8001/register_key', json={'key':QUEUE_KEY, 
                                                                     'vhost':'anticaptcha_vhost'})
# если очередь успешно создана:                                                                     
if answer == 'OK':

    # Пример показывает работу антикапчи с "невидимой" рекапчёй от гугла, точно так же работает обычная рекапча от гугла.
    # Это метод для работы без прокси
    result = NoCaptchaTaskProxyless.NoCaptchaTaskProxyless(anticaptcha_key = ANTICAPTCHA_KEY, 
                                                           callbackUrl=f'http://85.255.8.26:8001/anticaptcha/nocaptcha/{QUEUE_KEY}'
                                                          ).captcha_handler(websiteURL='https://www.google.com/recaptcha/api2/demo',
                                                                            websiteKey='6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-')
    print(result)

    # получение результата из кеша
    print(CallbackClient.CallbackClient(task_id=result['taskId']).captcha_handler())
    # получение результата из RabbitMQ очереди
    print(CallbackClient.CallbackClient(task_id=result['taskId'], queue_name=QUEUE_KEY, call_type='queue').captcha_handler())

    # Асинхронный пример
    async def run():
        try:
            result = await NoCaptchaTaskProxyless.aioNoCaptchaTaskProxyless(anticaptcha_key=ANTICAPTCHA_KEY, 
                                                                            callbackUrl=f'http://85.255.8.26:8001/anticaptcha/nocaptcha/{QUEUE_KEY}'
                                                                           ).captcha_handler(websiteURL='https://www.google.com/recaptcha/api2/demo',
                                                                                             websiteKey='6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-')
            print(result)
                    
            # получение результата из кеша
            print(CallbackClient.CallbackClient(task_id=result['taskId']).captcha_handler())
            # получение результата из RabbitMQ очереди
            print(CallbackClient.CallbackClient(task_id=result['taskId'], queue_name=QUEUE_KEY, call_type='queue').captcha_handler())

        except Exception as err:
            print(err)


    if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())
        loop.close()