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
import sys
import asyncio

from aiojsonrpc import Client

async def on_event(*args, **kwargs):
    print(*args, **kwargs)
    result = await client2.call('rpc_queue', 'hello', message='How are you?')
    print(result)
    # await asyncio.sleep(2)
    # print('YEASASSA')


async def run():
    await client.connect()
    await client2.connect()
    await client.subscribe('rpc_queue', events=['model.forks.created'], callback=on_event)

    # i = 0
    # while True:
    #     i += 1
    #     await asyncio.sleep(2)
    #     result = await client.call('rpc_queue', 'hello', message='How are you? ' + str(i))
    #     print(result)

if __name__ == '__main__':
    client = Client(amqp_uri='amqp://192.168.100.9')
    client2 = Client(amqp_uri='amqp://192.168.100.9')
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(run())
    event_loop.run_forever()
