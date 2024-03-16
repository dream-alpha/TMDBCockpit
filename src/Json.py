#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2024 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.


import six
from .Debug import logger
from .Utils import checkText


class Json():
	def __init__(self):
		return

	def parseJson(self, result, source, keys):
		for key in keys:
			self.parseJsonSingle(result, source, key)

	def parseJsonSingle(self, result, source, key):
		value = "None"
		if key in source:
			value = source[key]
		if isinstance(value, six.text_type):
			value = six.ensure_str(value)
		if value is None:
			value = "None"
		result[key] = value

	def parseJsonList(self, result, key, separator):
		logger.info("result: %s, key: %s, separator: %s", result, key, separator)
		alist = ""
		if key in result:
			logger.debug("key: %s", result[key])
			for source in result[key]:
				# logger.debug("source: %s", source)
				text = checkText(source)
				# logger.debug("checked text: %s", text)
				text = six.ensure_str(text)
				if alist and text:
					alist += separator + " "
				if text:
					alist += text
			logger.debug("alist: %s", alist)
			result[key] = alist
		else:
			result[key] = ""
		logger.debug("result[key]: %s", result[key])
