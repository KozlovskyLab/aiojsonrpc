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
import time
import asyncio
import inspect
from urllib.parse import urlparse

import aioamqp
try:
    from raven import Client as SentryClient
    from raven_aiohttp import AioHttpTransport
except ImportError:
    logging.warning("Support 'Sentry' was missing. Install the 'raven' and 'raven_aiohttp' modules to support.")

from aiojsonrpc import BaseEncoder

__all__ = ['Worker']


class Worker:
    def __init__(self, service_name: str, *, api: dict, amqp_uri: str = 'amqp://guest:guest@localhost',
                 sentry_uri: str = None, loader=None, dumper=None, encoder=None, loop=None):
        """

        Parameters
        ----------
        service_name : str
            ...
        api : dict
            ...
        amqp_uri : str, optional
            ...
        sentry_uri : str, optional
            ...
        loader :
            ...
        dumper :
            ...
        encoder :
            ...
        loop : ..., optional
            ...
        """
        self._service_name = service_name
        self._api = api
        self._amqp_uri = amqp_uri
        self._sentry_uri = sentry_uri
        self._loader = loader or json.loads
        self._dumper = dumper or json.dumps
        # TODO: this is not work now.
        self._encoder = encoder or BaseEncoder

        amqp_parsed_uri = urlparse(self._amqp_uri)
        self._rabbitmq_hostname = amqp_parsed_uri.hostname
        self._rabbitmq_port = amqp_parsed_uri.port
        self._rabbitmq_username = amqp_parsed_uri.username if amqp_parsed_uri.username is not None else 'guest'
        self._rabbitmq_password = amqp_parsed_uri.password if amqp_parsed_uri.password is not None else 'guest'

        if self._sentry_uri is not None:
            self._sentry_client = SentryClient(self._sentry_uri, transport=AioHttpTransport)

        self._loop = loop or asyncio.get_event_loop()
        self._transport = None
        self._protocol = None
        self._channel = None


    async def connect(self):
        """
        """
        try:
            self._transport, self._protocol = await aioamqp.connect(
                host=self._rabbitmq_hostname,
                port=self._rabbitmq_port,
                login=self._rabbitmq_username,
                password=self._rabbitmq_password,
                heartbeat=10,
                loop=self._loop)  # use default parameters
        except aioamqp.AmqpClosedConnection:
            logging.info("closed connections")
            return

        logging.info("connected !")

        self._channel = await self._protocol.channel()

        # For `call` method.
        await self._channel.queue_declare(queue_name=self._service_name)  # TODO: add `durable` to save queue on disk?
        # For uniform distribution of tasks.
        await self._channel.basic_qos(prefetch_count=1, prefetch_size=0, connection_global=False)
        await self._channel.basic_consume(self._on_request, queue_name=self._service_name)

        # For `broadcast` method.
        await self._channel.exchange(exchange_name=self._service_name, type_name='topic')

        # let RabbitMQ generate a random queue name
        #result = await self._channel.queue(queue_name='', exclusive=True)
        #random_queue_name = result['queue']
        #await self._channel.queue_bind(exchange_name=self._service_name, queue_name=random_queue_name, routing_key='')
        #await self._channel.basic_consume(self._on_request, queue_name=random_queue_name, no_ack=True)


    async def run(self):
        """
        """
        if self._protocol is None:
            await self.connect()

        logging.info(" [x] Awaiting RPC requests")


    async def broadcast(self, event_name: str, *args: list, **kwargs: dict):
        """

        Parameters
        ----------
        event_name : str
            ...
        args : list, optional
            ...
        kwargs : dict, optional
            ...

        Returns
        -------

        """
        creation_time = time.time()

        if self._protocol is None:
            await self.connect()

        request = dict(event=event_name, args=args, kwargs=kwargs, timings=dict(creation_time=creation_time))
        await self._channel.basic_publish(
            payload=self._dumper(request, cls=self._encoder),
            exchange_name=self._service_name,
            routing_key=event_name,  # What about that?
            properties={
                'content_type': 'application/json',
                # 'delivery_mode': 2,  # make message persistent
            })
        logging.info("The notification is successfully sent to all subscribers <event_name='{}'>.".format(event_name))


    async def _on_request(self, channel, body, envelope, properties):
        """

        Parameters
        ----------
        channel :
            ...
        body :
            ...
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
        """
        receipt_time = time.time()
        # TODO: validate content_type parameter
        request = self._loader(body.decode())
        logging.info("The request is accepted <id='{}', method='{}', args='{}'>.".format(
            properties.correlation_id,
            request['method'],
            request['args'],
            request['kwargs']))
        logging.debug(
            " - Envelope <consumer_tag='{}', delivery_tag='{}', exchange_name='{}', is_redeliver='{}', "
            "routing_key='{}'>.".format(
            envelope.consumer_tag,
            envelope.delivery_tag,
            envelope.exchange_name,
            envelope.is_redeliver,
            envelope.routing_key))
        logging.debug(
            " - Properties <app_id='{}', cluster_id='{}', content_encoding='{}', content_type='{}', "
            "correlation_id='{}', delivery_mode='{}', expiration='{}', headers='{}', message_id='{}', priority='{}', "
            "reply_to='{}', timestamp='{}', type='{}', user_id='{}'>.".format(
            properties.app_id,
            properties.cluster_id,
            properties.content_encoding,
            properties.content_type,
            properties.correlation_id,
            properties.delivery_mode,
            properties.expiration,
            properties.headers,
            properties.message_id,
            properties.priority,
            properties.reply_to,
            properties.timestamp,
            properties.type,
            properties.user_id))

        response = None

        # If not used dot notation.
        if '.' not in request['method']:
            method = self._api[request['method']]
        # If used dot notation.
        else:
            mod_name, call_path = request['method'].split('.', 1)
            method = self._api[mod_name]
            for call_name in call_path.split('.'):
                try:
                    method = getattr(method, call_name)
                except AttributeError as e:
                    response = dict(id=properties.correlation_id,
                                    error=dict(
                                        code=-32601,
                                        message='Method not found.'),
                                    timings=dict(
                                        creation_time=request['timings']['creation_time'],
                                        receipt_time=receipt_time))

                    logging.warning("Method not found <method='{}'>.".format(request['method']))


        if response is None:
            start_time = time.time()
            # Tries to call method
            try:
                if asyncio.iscoroutinefunction(method):  # TODO: this is `inspect.iscoroutinefunction(method)` not work correctly
                    result = await method(*request['args'], **request['kwargs'])
                    end_time = time.time()
                elif inspect.isasyncgenfunction(method):
                    # TODO: Change this (The results returned gradually).
                    result = []
                    async for res in method(*request['args'], **request['kwargs']):
                        result.append(res)
                    end_time = time.time()
                else:
                    result = method(*request['args'], **request['kwargs'])
                    end_time = time.time()
            except TypeError as e:
                # TODO: how send error & exit?
                # Invalid method parameter(s).
                response = dict(id=properties.correlation_id,
                                error=dict(
                                    code=-32602,
                                    message=str(e)),
                                timings=dict(
                                    creation_time=request['timings']['creation_time'],
                                    receipt_time=receipt_time,
                                    start_time=start_time))
                logging.warning('TypeError: ' + str(e))
            except Exception as e:
                # TODO: how send error & exit?
                # Internal JSON-RPC error.
                response = dict(id=properties.correlation_id,
                                error=dict(
                                    code=-32603,
                                    message=str(e)),
                                timings=dict(
                                    creation_time=request['timings']['creation_time'],
                                    receipt_time=receipt_time,
                                    start_time=start_time))
                logging.warning('Exception: ' + str(e))
                # Send error to Sentry.
                if self._sentry_uri is not None:
                    self._sentry_client.captureException()

        if response is None:
            response = dict(result=result,
                            timings=dict(
                                creation_time=request['timings']['creation_time'],
                                receipt_time=receipt_time,
                                start_time=start_time,
                                end_time=end_time,
                                exec_time=end_time-start_time))

        # If request is requires a response.
        if properties.correlation_id is not None:
            await self._channel.basic_publish(
                payload=self._dumper(response, cls=self._encoder),
                exchange_name='',
                routing_key=properties.reply_to,
                properties={
                    'correlation_id': properties.correlation_id,
                    'content_type': 'application/json',
                    # 'delivery_mode': 2,  # make message persistent
                },
            )
            logging.info(
                "The results of the function call was successfully sent back <id='{}', method='{}'>.".format(
                properties.correlation_id,
                request['method']
            ))

        # If request is not a notification.
        if envelope.exchange_name == '':
            # Send a notification about the successful delivery.
            await self._channel.basic_client_ack(delivery_tag=envelope.delivery_tag)
