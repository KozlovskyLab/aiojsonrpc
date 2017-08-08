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
from setuptools import setup

setup(name='aiojsonrpc',
      version='0.2',
      description='Distributed task execution.',
      url='http://github.com/kozlovskilab/aiojsonrpc',
      author='Vladimir Kozlovski',
      author_email='vladimir@kozlovskilab.com',
      license='MIT',
      packages=['aiojsonrpc'],
      install_requires=['asynqp'],
      zip_safe=False)
