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
import sys
import asyncio
import inspect
from time import time

logger = logging.getLogger('aiojsonrpc.worker')

import asynqp
try:
    from raven import Client as SentryClient
    from raven_aiohttp import AioHttpTransport
except ImportError:
    logger.warning("Support 'Sentry' was missing. Install the 'raven' and 'raven_aiohttp' modules to support.")

from aiojsonrpc import BaseService

__all__ = ['WorkerService']


class WorkerService(BaseService):
    def __init__(self, service_name: str, *, api: dict, sentry_uri: str = None, threads_number: int = 10, **kwargs):
        """

        Parameters
        ----------
        service_name : str
            ...
        api : dict
            ...
        sentry_uri : str, optional
            ...

        # TODO: See base
        """
        super(WorkerService, self).__init__(**kwargs)
        self._service_name = service_name
        self._api = api
        self._sentry_client = None
        if sentry_uri is not None:
            self._sentry_client = SentryClient(sentry_uri, transport=AioHttpTransport)
        self._threads_number = threads_number
        self._queue = asyncio.Queue(1)

    @classmethod
    async def initialize(cls, service_name: str, *, api: dict, amqp_uri: str = 'amqp://guest:guest@localhost',
                         **kwargs):
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
        obj = cls(service_name, api=api, **kwargs)
        await obj.connect(amqp_uri=amqp_uri)

        return obj

    async def connect(self, *args, **kwargs):
        """

        Parameters
        ----------
        # TODO: See base
        """
        await super(WorkerService, self).connect(*args, **kwargs)
        requests_queue = await self._channel.declare_queue(name=self._service_name)
        consumer = await requests_queue.consume(lambda msg: self._loop.create_task(self._queue.put(msg)))  # TODO: It's ok (`asyncio.ensure_future`)?

    async def _on_request(self, msg: asynqp.Message):
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
        receipt_time = time()
        logger.debug(
            "AMQP Message properties <headers='{headers}', content_type='{content_type}', "
            "content_encoding='{content_encoding}', delivery_mode={delivery_mode}, priority={priority}, "
            "correlation_id='{correlation_id}', reply_to='{reply_to}', expiration='{expiration}', "
            "message_id='{message_id}', timestamp='{timestamp}', type='{type}', user_id='{user_id}', "
            "app_id='{app_id}'>".format(
                headers=msg.headers,
                content_type=msg.content_type,
                content_encoding=msg.content_encoding,
                delivery_mode=msg.delivery_mode,
                priority=msg.priority,
                correlation_id=msg.correlation_id,
                reply_to=msg.reply_to,
                expiration=msg.expiration,
                message_id=msg.message_id,
                timestamp=msg.timestamp,
                type=msg.type,
                user_id=msg.user_id,
                app_id=msg.app_id
            )
        )

        # TODO: Validate `content_type`?
        request = self._loader(msg.body.decode(), cls=self._decoder)
        logger.info(
            "The request is accepted <id='{id}', method='{method}', args='{args}', kwargs='{kwargs}'>.".format(
                id=msg.correlation_id,
                method=request['method'],
                args=request['args'],
                kwargs=request['kwargs']
            ))

        response = None

        # If not used dot notation.
        if '.' not in request['method']:
            try:
                method = self._api[request['method']]
            except KeyError:
                response = dict(id=msg.correlation_id,
                                error=dict(
                                    code=-32601,
                                    message='Method not found.'),
                                timings=dict(
                                    creation_time=request['timings']['creation_time'],
                                    receipt_time=receipt_time))
                logger.warning("Method not found <id='{id}', method='{method}'>.".format(
                    id=msg.correlation_id, **request))
                # TODO: Send response and break?

        # If used dot notation.
        else:
            mod_name, call_path = request['method'].split('.', 1)
            method = self._api[mod_name]
            for call_name in call_path.split('.'):
                try:
                    method = getattr(method, call_name)
                except AttributeError:
                    response = dict(id=msg.correlation_id,
                                    error=dict(
                                        code=-32601,
                                        message='Method not found.'),
                                    timings=dict(
                                        creation_time=request['timings']['creation_time'],
                                        receipt_time=receipt_time))
                    logger.warning("Method not found <id='{id}', method='{method}'>.".format(
                        id=msg.correlation_id, **request
                    ))
                    # TODO: Send response and break?

        if response is None:
            start_time = time()
            # Tries to call method
            try:
                if asyncio.iscoroutinefunction(
                        method):  # TODO: this is `inspect.iscoroutinefunction(method)` not work correctly
                    result = await method(*request['args'], **request['kwargs'])
                    end_time = time()
                elif inspect.isasyncgenfunction(method):
                    # TODO: Change this (The results returned gradually).
                    result = []
                    async for res in method(*request['args'], **request['kwargs']):
                        result.append(res)
                    end_time = time()
                else:
                    result = method(*request['args'], **request['kwargs'])
                    end_time = time()
            except TypeError as e:
                exception_type, exception_value, exception_traceback = sys.exc_info()
                # Invalid method parameter(s).
                response = dict(id=msg.correlation_id,
                                error=dict(
                                    code=-32602,
                                    message=str(exception_value),
                                    type=exception_value,
                                    traceback=exception_traceback
                                ),
                                timings=dict(
                                    creation_time=request['timings']['creation_time'],
                                    receipt_time=receipt_time,
                                    start_time=start_time)
                                )
                logger.warning('TypeError: ' + str(e))
            except Exception as e:
                exception_type, exception_value, exception_traceback = sys.exc_info()
                # Internal JSON-RPC error.
                response = dict(id=msg.correlation_id,
                                error=dict(
                                    code=-32602,
                                    message=str(exception_value),
                                    type=exception_value,
                                    traceback=exception_traceback
                                ),
                                timings=dict(
                                    creation_time=request['timings']['creation_time'],
                                    receipt_time=receipt_time,
                                    start_time=start_time)
                                )
                logger.warning('Exception: ' + str(e))
                # TODO: Send traceback to client
                # Send error to Sentry.
                if self._sentry_client is not None:
                    self._sentry_client.captureException()

        if response is None:
            response = dict(result=result,
                            timings=dict(
                                creation_time=request['timings']['creation_time'],
                                receipt_time=receipt_time,
                                start_time=start_time,
                                end_time=end_time,
                                exec_time=end_time - start_time))

        # If request is requires a response.
        if msg.correlation_id is not None:
            response_msg = asynqp.Message(
                body=self._dumper(response, cls=self._encoder),
                correlation_id=msg.correlation_id,
                content_type='application/json',
            )
            exchange = await self._channel.declare_exchange('', 'direct')
            exchange.publish(response_msg, routing_key=msg.reply_to)
            logger.info(
                "The results of the function call was successfully sent back <id='{id}', "
                "method='{method}'>.".format(
                    id=msg.correlation_id, method=request['method']
                )
            )

        # Message is successfully processed
        msg.ack()

    async def run(self):
        """

        Returns
        -------
        """
        tasks = [self._run_thread(thread_id=thread_id) for thread_id in range(self._threads_number)]
        return await asyncio.wait(tasks)

    async def _run_thread(self, *, thread_id: int):
        """

        Parameters
        ----------
        thread_id : int
            ...
        """
        logger.info(
            "Thread successfully created and waiting for tasks <thread_id={thread_id}>.".format(thread_id=thread_id))
        while True:
            msg = await self._queue.get()
            await self._on_request(msg)
