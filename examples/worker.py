#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the `aiojsonrpc` package.
# (c) 2016-2017 Kozlovski Lab <welcome@kozlovskilab.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
:Authors:
    - `Vladimir Kozlovski <vladimir@kozlovskilab.com>`_
"""
import logging
import asyncio

from aiojsonrpc import Worker

worker = None

def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)


async def hello(message):
    print(message)
    #await worker.broadcast('model.forks.created', {'message': 'hello'})
    return message + ' - !'


async def run():
    global worker
    worker = Worker(service_name='rpc_queue', api={'hello': hello}, amqp_uri='amqp://192.168.100.9')
    await worker.run()

    i = 0
    while True:
        i += 1
        await worker.broadcast('model.forks.created', {'message': 'hello ' + str(i)})
        await asyncio.sleep(2)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('manual_api')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.run_forever()
