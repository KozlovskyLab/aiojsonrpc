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


async def run():
   value = await client.call('rpc_queue', 'fib', sys.argv[1])
   print(value)


if __name__ == '__main__':
    client = Client(amqp_uri='amqp://192.168.1.175')
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(run())
    event_loop.run_forever()
