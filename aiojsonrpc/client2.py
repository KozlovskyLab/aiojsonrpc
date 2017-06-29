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
import json
import uuid
import time
import asyncio
import inspect
from urllib.parse import urlparse

import asynqp

from aiojsonrpc import WorkerException, BaseEncoder

__all__ = ['Client']

logger = logging.getLogger('favbet.__main__')


class Client:
    def __init__(self, *, amqp_uri: str = 'amqp://guest:guest@localhost', loader=None, dumper=None, encoder=None,
                 loop=None):
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
        loop : ...
            ...
        """
        # self.service_name = service_name
        self._amqp_uri = amqp_uri
        self._loader = loader or json.loads
        self._dumper = dumper or json.dumps
        self._encoder = encoder or BaseEncoder

        amqp_parsed_uri = urlparse(self._amqp_uri)
        self._rabbitmq_hostname = amqp_parsed_uri.hostname
        self._rabbitmq_port = amqp_parsed_uri.port if amqp_parsed_uri.port is not None else 5672
        self._rabbitmq_username = amqp_parsed_uri.username if amqp_parsed_uri.username is not None else 'guest'
        self._rabbitmq_password = amqp_parsed_uri.password if amqp_parsed_uri.password is not None else 'guest'

        self._loop = loop or asyncio.get_event_loop()
        self._transport = None
        self._protocol = None
        self._channel = None
        self._callback_queue = None
        # self._correlation_id = None
        # self._response = None
        self._waiter = None


    @classmethod
    async def initialize(cls, *, amqp_uri: str = 'amqp://guest:guest@localhost', loader=None, dumper=None, encoder=None,
                         reconnecting: bool = True, loop=None):
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
        reconnecting : bool, optional
            ...
        loop : ...
            ...
        """
        obj = cls(amqp_uri=amqp_uri, loader=loader, dumper=dumper, encoder=encoder, loop=loop)
        await obj.connect(reconnecting=reconnecting)

        return obj


    async def connect(self, *, reconnecting: bool = True):
        """

        Parameters
        ----------
        reconnecting : bool, optional
            ...
        """
        self._connection = await asynqp.connect(
            host=self._rabbitmq_hostname,
            port=self._rabbitmq_port,
            username=self._rabbitmq_username,
            password=self._rabbitmq_password,
            loop=self._loop
        )

        logger.info("A connection with RabbitMQ is successfully established <host='{host}', port={port}.".format(
            host=self._rabbitmq_hostname, port=self._rabbitmq_port))

        self._channel = await self._connection.open_channel()
        # For `call` method (for get results).
        self._callback_queue = await self._channel.declare_queue(name='', exclusive=True)  # TODO: add `durable` to save queue on disk?

        consumer = await self._callback_queue.consume(self._on_response, no_ack=True)

        #await self._channel.basic_consume(self._on_response, no_ack=True, queue_name=self._callback_queue)

        # For `broadcast` method.
        # await self._channel.exchange_declare(exchange_name=self.service_name, type_name='fanout')


    # async def disconnect(self):
    #     await self._protocol.close()
    #
    #
    # async def main_loop(self):
    #     try:
    #         while True:
    #             if self._protocol is None:
    #                 await self.connect()
    #             await self._protocol.wait_closed()
    #             await self.disconnect()
    #     except aioamqp.AmqpClosedConnection:
    #         await self.main_loop()
    #     finally:
    #         await self.disconnect()


    # TODO: Add `app_id`?
    # TODO: Add `delivery_mode` to persistent
    # TODO: Add `expiration` to
    # TODO: Add `priority`
    async def call(self, service: str, method: str, *args: list, **kwargs: dict):
        """
        Performs the function on the remote server and returns the execution result or raises error.

        Parameters
        ----------
        service : str
            ...
        method : str
            ...
        args : list
            ...
        kwargs : dict
            ...
        """

        creation_time = time.time()

        # if self._protocol is None:
        #     await self.connect()

        self._waiter = asyncio.Event()
        self._response = None
        self._correlation_id = str(uuid.uuid4())

        request = dict(method=method, args=args, kwargs=kwargs, timings=dict(creation_time=creation_time))
        msg = asynqp.Message(
            body=self._dumper(request, cls=self._encoder),
            reply_to=self._callback_queue.name,
            correlation_id=self._correlation_id,  # If notify not send it
            content_type='application/json',
            # delivery_mode=2,  # make message persistent
        )

        exchange = await self._channel.declare_exchange('', 'direct')
        exchange.publish(msg, routing_key=service)


        # await self._channel.basic_publish(
        #     payload=self._dumper(request, cls=self._encoder),
        #     exchange_name='',
        #     routing_key=service,
        #     properties={
        #         'reply_to': self._callback_queue,
        #         'correlation_id': self._correlation_id,  # If notify not send it
        #         'content_type': 'application/json',
        #         # 'delivery_mode': 2,  # make message persistent
        #     })
        logger.info("The request to call the function successfully sent <id='{}', method='{}'>.".format(
            self._correlation_id,
            method,
        ))

        await self._waiter.wait()

        if 'result' in self._response:
            return self._response['result']

        # TODO: Raise error with same type?
        # self._response = None
        raise WorkerException(self._response['error']['message'], code=self._response['error']['code'])


    # TODO: Rename to run?
    async def execute(self, service: str, method: str, *args: list, **kwargs: dict):
        """

        Parameters
        ----------
        service : str
            ...
        method : str
            ...
        args : list
            ...
        kwargs : dict
            ...
        """
        creation_time = time.time()

        # if self._protocol is None:
        #     await self.connect()

        request = dict(method=method, args=args, kwargs=kwargs, timings=dict(creation_time=creation_time))
        await self._channel.basic_publish(
            payload=self._dumper(request, cls=self._encoder),
            exchange_name='',
            routing_key=service,
            properties={
                'content_type': 'application/json',
                # 'delivery_mode': 2,  # make message persistent
            })
        logger.info("The request to execute the function successfully sent <method='{}'>.".format(method))


    # await self._protocol.close()


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


    def _on_response(self, msg):
        """

        Parameters
        ----------
        channel :
        body :
        envelope :
            An instance of envelope. Envelope class which encapsulate a group of amqp parameter such as:
                * consumer_tag
                * delivery_tag
                * exchange_name
                * is_redeliver
                * routing_key
        properties :
            A message properties, an instance of properties with the following members:
                * app_id
                    Application identifier string, for example, "eventoverse" or "webcrawler".
                * cluster_id
                    ...
                * content_encoding
                    MIME content encoding of message payload. Has the same purpose/semantics as HTTP Content-Encoding
                    header.
                * content_type
                    MIME content type of message payload. Has the same purpose/semantics as HTTP Content-Type header.
                * correlation_id
                    ID of the message that this message is a reply to. Applications are encouraged to use this
                    attribute instead of putting this information into the message payload.
                * delivery_mode
                    ...
                * expiration
                    Message expiration specification as a string.
                * headers
                    ...
                * message_id
                    Message identifier as a string. If applications need to identify messages, it is recommended that
                    they use this attribute instead of putting it into the message payload.
                * priority
                    Message priority, from 0 to 9.
                * reply_to
                    Commonly used to name a reply queue (or any other identifier that helps a consumer application to
                    direct its response). Applications are encouraged to use this attribute instead of putting this
                    information into the message payload.
                * timestamp
                    Timestamp of the moment when message was sent, in seconds since the Epoch.
                * type
                    Message type as a string. Recommended to be used by applications instead of including this
                    information into the message payload.
                * user_id
                    Sender's identifier. Note that RabbitMQ will check that the [value of this attribute is the same as
                    username AMQP connection was authenticated with]
                    (http://www.rabbitmq.com/extensions.html#validated-user-id), it SHOULD NOT be used to transfer, for
                    example, other application user ids or be used as a basis for some kind of Single Sign-On solution.

        Returns
        -------

        """
        if self._correlation_id == msg.correlation_id:
            # TODO: Validate content_type
            self._response = self._loader(msg.body.decode())

        self._waiter.set()