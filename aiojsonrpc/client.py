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
import uuid
import time
import asyncio
import inspect

logger = logging.getLogger('aiojsonrpc.client')

import asynqp

from aiojsonrpc import BaseService, WorkerException

__all__ = ['ClientService']


class ClientService(BaseService):
    def __init__(self, *args, **kwargs):
        """

        Parameters
        ----------
        # TODO: See base
        """
        super(ClientService, self).__init__(*args, **kwargs)
        self._response_queue = None
        self._response = {}
        self._waiter = {}

    @classmethod
    async def initialize(cls, *, amqp_uri: str = 'amqp://guest:guest@localhost', **kwargs):
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
        """
        obj = cls(**kwargs)
        await obj.connect(amqp_uri=amqp_uri)

        return obj

    async def connect(self, *args, **kwargs):
        """

        Parameters
        ----------
        # TODO: See base
        """
        await super(ClientService, self).connect(*args, **kwargs)
        # For `call` method (for get results).
        self._response_queue = await self._channel.declare_queue(name='', exclusive=True)  # TODO: add `durable` to save queue on disk?
        consumer = await self._response_queue.consume(self._on_response, no_ack=True)

        # For `broadcast` method.
        # await self._channel.exchange_declare(exchange_name=self.service_name, type_name='fanout')

    # TODO: Add `app_id`?
    # TODO: Add `delivery_mode` to persistent
    # TODO: Add `expiration` to
    # TODO: Add `priority`
    async def call(self, rpc_service: str, rpc_method: str, *args: list, **kwargs: dict):
        """
        Performs the function on the remote server and returns the execution result or raises error.

        Parameters
        ----------
        rpc_service : str
            ...
        rpc_method : str
            ...
        args : list
            ...
        kwargs : dict
            ...
        """
        creation_time = time.time()

        correlation_id = str(uuid.uuid4())
        self._waiter[correlation_id] = asyncio.Event()
        # self._response = None

        request = dict(method=rpc_method, args=args, kwargs=kwargs, timings=dict(creation_time=creation_time))
        msg = asynqp.Message(
            body=self._dumper(request, cls=self._encoder),
            reply_to=self._response_queue.name,
            correlation_id=correlation_id,  # If notify not send it
            content_type='application/json',
            # delivery_mode=2,  # make message persistent
        )

        exchange = await self._channel.declare_exchange('', 'direct')
        exchange.publish(msg, routing_key=rpc_service)

        logger.info("The request to call the function successfully sent <id='{}', method='{}'>.".format(
            correlation_id,
            rpc_method,
        ))

        await self._waiter[correlation_id].wait()

        response = self._response[correlation_id]

        del self._response[correlation_id]
        del self._waiter[correlation_id]

        if 'result' in response:
            return response['result']

        # TODO: Raise error with same type?
        raise WorkerException(response['error']['message'], code=response['error']['code'])

    # TODO: Rename to run/notify?
    async def execute(self, rpc_service: str, rpc_method: str, *args: list, **kwargs: dict):
        """

        Parameters
        ----------
        rpc_service : str
            ...
        rpc_method : str
            ...
        args : list
            ...
        kwargs : dict
            ...
        """
        creation_time = time.time()

        request = dict(method=rpc_method, args=args, kwargs=kwargs, timings=dict(creation_time=creation_time))
        msg = asynqp.Message(
            body=self._dumper(request, cls=self._encoder),
            content_type='application/json',
            # delivery_mode=2,  # make message persistent
        )

        exchange = await self._channel.declare_exchange('', 'direct')
        exchange.publish(msg, routing_key=rpc_service)

        logger.info("The request to execute the function successfully sent <method='{}'>.".format(rpc_method))

    # TODO: Remove this from client?
    # async def broadcast(self, service: str, method: str, *args: list, **kwargs: dict):
    #     """
    #
    #     Parameters
    #     ----------
    #     service : str
    #         ....
    #     method : str
    #         ...
    #     args : list, optional
    #         ...
    #     kwargs : dict, optional
    #         ...
    #
    #     Returns
    #     -------
    #
    #     """
    #     creation_time = time.time()
    #
    #     if self._protocol is None:
    #         await self.connect()
    #
    #     request = dict(method=method, args=args, kwargs=kwargs, timings=dict(creation_time=creation_time))
    #     await self._channel.basic_publish(
    #         payload=self._dumper(request, cls=self._encoder),
    #         exchange_name=service,
    #         routing_key='',
    #         properties={
    #             'content_type': 'application/json',
    #             # 'delivery_mode': 2,  # make message persistent
    #         })
    #     logger.info("The request to notify the function successfully sent <method='{}'>.".format(method))

    async def subscribe(self, service: str, *, events: list, callback):
        """

        Parameters
        ----------
        service : str
            ...
        events : list
            ...
        callback :
            ...

        Returns
        -------

        """
        # if self._protocol is None:
        #     await self.connect()

        exchange = await self._channel.declare_exchange(name=service, type='topic', durable=False)
        queue = await self._channel.declare_queue(name='', durable=False, auto_delete=True)

        for binding_key in events:
            await queue.bind(exchange, binding_key)

        consumer = await queue.consume(self._on_event(callback), no_ack=True)

        # await self._channel.exchange(service, 'topic')
        # result = await self._channel.queue(queue_name='', durable=False, auto_delete=True)
        # queue_name = result['queue']
        #
        # for binding_key in events:
        #     await self._channel.queue_bind(
        #         exchange_name=service,
        #         queue_name=queue_name,
        #         routing_key=binding_key
        #     )
        #
        # await self._channel.basic_consume(self._on_event(callback), queue_name=queue_name)

    def _on_event(self, callback):
        """

        Parameters
        ----------
        callback

        Returns
        -------

        """
        def wrapper(msg):
            """

            Parameters
            ----------
            msg :
                ...
            """
            request = self._loader(msg.body.decode())
            if inspect.iscoroutinefunction(callback):
                result = asyncio.gather(self._loop.create_task(callback(request['event'], *request['args'], **request['kwargs'])))
                end_time = time.time()
            # elif inspect.isasyncgencallbacktion(callback):
            #     pass
            #     # TODO: Change this (The results returned gradually).
            #     result = []
            #     async for res in callback(request['event'], *request['args'], **request['kwargs']):
            #         result.append(res)
            #     end_time = time.time()
            else:
                result = callback(request['event'], *request['args'], **request['kwargs'])
                end_time = time.time()

        return wrapper

    def _on_response(self, msg: asynqp.Message):
        """

        Parameters
        ----------
        msg : asynqp.Message
            An AMQP Basic message with the following members:
                * body : bytes or str or dict
                    Representing the body of the message. Strings will be encoded according to the content_encoding
                    parameter; dicts will be converted to a string using JSON.
                * headers : dict
                    A dictionary of message headers.
                * content_type : str
                    MIME content type (defaults to ‘application/json’ if body is a dict, or ‘application/octet-stream’
                    otherwise).
                * content_encoding : str
                    MIME encoding (defaults to ‘utf-8’).
                * delivery_mode : int
                    1 for non-persistent, 2 for persistent.
                * priority : int
                    Priority - integer between 0 and 9.
                * correlation_id : str
                    Correlation id of the message (for applications).
                * reply_to : str
                    Reply-to address (for applications).
                * expiration : str
                    Expiration specification (for applications).
                * message_id : str
                    Unique id of the message (for applications).
                * timestamp : datetime.datetime
                    `datetime` of when the message was sent (default: `datetime.now()`).
                * type : str
                    Message type (for applications).
                * user_id : str
                    ID of the user sending the message (for applications).
                * app_id : str
                    ID of the application sending the message (for applications).

        Returns
        -------

        """
        if msg.correlation_id in self._waiter:
            # TODO: Validate content_type
            self._response[msg.correlation_id] = self._loader(msg.body.decode())
            self._waiter[msg.correlation_id].set()
