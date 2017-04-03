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

__all__ = ['WorkerException']


class WorkerException(Exception):

    def __init__(self, *args, code, **kwargs):
        super(Exception, WorkerException).__init__(self, *args, **kwargs)
        #self._message = message
        self._code = code

    # @property
    # def message(self):
    #     return self.message

    @property
    def code(self):
        return self._code
