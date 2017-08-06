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
from urllib.parse import urlparse
import json  # TODO: ujson (not suported `cls` param?)

logger = logging.getLogger('aiojsonrpc.base')

import asynqp

from aiojsonrpc import BaseEncoder, BaseDecoder

__all__ = ['BaseService']


class BaseService:
    def __init__(self, *, loader=None, dumper=None, encoder=None, decoder=None, loop: asyncio.AbstractEventLoop = None):
        """

        Parameters
        ----------
        loader :
            ...
        dumper :
            ...
        encoder :
            ...
        decoder :
            ...
        loop : asyncio.AbstractEventLoop, optional
            Event loop is the central execution device provided by `asyncio`.
        """
        self._loader = loader or json.loads
        self._dumper = dumper or json.dumps
        self._encoder = encoder or BaseEncoder
        self._decoder = decoder or BaseDecoder
        self._loop = loop or asyncio.get_event_loop()

        self._connection = None
        self._channel = None

    @classmethod
    async def initialize(cls, *, amqp_uri: str = 'amqp://guest:guest@localhost', loader=None, dumper=None, encoder=None,
                         decoder=None, loop: asyncio.AbstractEventLoop = None):
        """

        Parameters
        ----------
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
        loop : asyncio.AbstractEventLoop, optional
            Event loop is the central execution device provided by `asyncio`.

        Returns
        -------

        """
        raise NotImplementedError("The method `initialize` should be implemented in the parent class.")

    async def connect(self, *, amqp_uri: str = 'amqp://guest:guest@localhost'):
        """

        Parameters
        ----------
        amqp_uri : str, optional
            ...
        """
        amqp_parsed_uri = urlparse(amqp_uri)
        amqp_hostname = amqp_parsed_uri.hostname
        amqp_port = amqp_parsed_uri.port if amqp_parsed_uri.port is not None else 5672
        amqp_username = amqp_parsed_uri.username if amqp_parsed_uri.username is not None else 'guest'
        amqp_password = amqp_parsed_uri.password if amqp_parsed_uri.password is not None else 'guest'

        self._connection = await asynqp.connect(
            host=amqp_hostname,
            port=amqp_port,
            username=amqp_username,
            password=amqp_password,
            loop=self._loop
        )

        logger.info("A connection with RabbitMQ is successfully established <host='{host}', port={port}>.".format(
            host=amqp_hostname, port=amqp_port))

        self._channel = await self._connection.open_channel()

    async def disconnect(self):
        raise NotImplementedError("The method `disconnect` should be implemented in the parent class.")
