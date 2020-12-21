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

from aiojsonrpc import WorkerService, ClientService


class TestService(WorkerService, ClientService):
    NAME = 'test_service'

    def __init__(self, *args, **kwargs):
        super(WorkerService, self).__init__(*args, **kwargs)

    @classmethod
    async def initialize(cls, service_name: str, *, api: dict, amqp_uri: str = 'amqp://guest:guest@localhost',
                         loader=None, dumper=None, encoder=None, decoder=None, sentry_uri=None,
                         threads_number: int = 10, loop=None):
        """

        Parameters
        ----------
        service_name : str
            ...
        api : dict
            ...
        amqp_uri : str, optional
            ...
        loader :
            ...
        dumper :
            ...
        encoder :
            ...
        decoder :
            ...
        sentry_uri : str, optional
            ...
        threads_number : int, optional
            ...
        loop : asyncio.AbstractEventLoop, optional
            Event loop is the central execution device provided by `asyncio`.
        """
        await super(WorkerService, cls).initialize(service_name=cls.NAME, api=api, amqp_uri=amqp_uri, loader=loader,
                                                 dumper=dumper, encoder=None, decoder=None, sentry_uri=sentry_uri,
                                                 threads_number=threads_number, loop=loop)
        await super(ClientService, cls).initialize(amqp_uri=amqp_uri, loader=loader, dumper=dumper, encoder=encoder,
                                                   decoder=decoder, loop=loop)

    async def ping(self, i):
        print('Ping #{}'.format(i))
        await self.run(self.NAME, 'pong', i)

    async def pong(self, i):
        i += 1
        print('Pong #{}'.format(i))
        await self.run(self.NAME, 'ping', i)


async def run():
    service = await TestService.initialize('test_service', api={}, amqp_uri='amqp://192.168.100.9')
    await service.run()


if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(run())
    event_loop.run_forever()
