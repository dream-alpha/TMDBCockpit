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


import os
from twisted.internet import threads, reactor
from Tools.LoadPixmap import LoadPixmap
from .Debug import logger
from .Utils import temp_dir
from .WebRequests import WebRequests


class Picture(WebRequests):
	def __init__(self):
		WebRequests.__init__(self)

	def showPicture(self, pixmap, atype, ident, url):
		logger.info("atype: %s, ident: %s, url: %s", atype, ident, url)
		path = temp_dir + atype + str(ident) + ".jpg"
		if url and not url.endswith("None") and not os.path.isfile(path):
			threads.deferToThread(self.downloadPicture, pixmap, url, path, self.displayPicture)
		else:
			self.displayPicture(pixmap, path)

	def downloadPicture(self, pixmap, url, path, callback):
		logger.info("...")
		self.downloadFile(url, path)
		reactor.callFromThread(callback, pixmap, path)  # pylint: disable=E1101

	def displayPicture(self, pixmap, path):
		logger.info("...")
		if pixmap and pixmap.instance:
			if path and os.path.isfile(path):
				pixmap.instance.setPixmap(LoadPixmap(path))
				pixmap.show()
			else:
				logger.debug("picture does not exist: %s", path)
				pixmap.hide()
