#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2023 by dream-alpha
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


import os
from twisted.internet import reactor, threads
from twisted.web.client import downloadPage
from Tools.LoadPixmap import LoadPixmap
from .Debug import logger
from .Utils import temp_dir


class Picture():
	def __init__(self):
		return

	def showPicture(self, pixmap, atype, ident, url):
		logger.info("atype: %s, ident: %s, url: %s", atype, ident, url)
		path = temp_dir + atype + str(ident) + ".jpg"
		if url and not url.endswith("None") and not os.path.isfile(path):
			threads.deferToThread(self.__downloadPicture, pixmap, url, path, self.__showPicture)
		else:
			self.__showPicture(pixmap, path)

	def __showPicture(self, pixmap, path):
		logger.info("path: %s", path)
		if pixmap and pixmap.instance:
			if not path or (path and not os.path.isfile(path)):
				logger.debug("picture does not exist: %s", path)
				pixmap.hide()
			else:
				pixmap.instance.setPixmap(LoadPixmap(path))
				pixmap.show()

	def __downloadPicture(self, pixmap, url, path, callback):
		def downloadError(error):
			logger.debug("error: %s, url: %s", error, url)
			reactor.callFromThread(callback, pixmap, path)  # pylint: disable=E1101

		def downloadSuccess(*_args):
			reactor.callFromThread(callback, pixmap, path)  # pylint: disable=E1101

		logger.info("url: %s, path: %s", url, path)
		downloadPage(url, path, timeout=5).addCallback(downloadSuccess).addErrback(downloadError)
