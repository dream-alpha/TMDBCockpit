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

from twisted.internet import threads, reactor
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ScrollLabel import ScrollLabel
from Screens.HelpMenu import HelpableScreen
from Screens.Screen import Screen
from .__init__ import _
from .List import List
from .ScreenConfig import ScreenConfig
from .Picture import Picture
from .Debug import logger
from .DelayTimer import DelayTimer
from .SearchSeason import SearchSeason
from .MoreOptions import MoreOptions


class ScreenSeason(MoreOptions, Picture, Screen, HelpableScreen):
	def __init__(self, session, movie, ident, media, service_path):
		logger.info("movie: %s, ident: %s, media: %s", movie, ident, media)
		Screen.__init__(self, session)
		MoreOptions.__init__(self, session, service_path)
		self.title = "TMDB - The Movie Database - " + _("Seasons")
		Picture.__init__(self)
		self.session = session
		self.movie = movie
		self.ident = ident
		self.media = media
		self.service_path = service_path
		self.files_saved = False
		self.result = []
		self['searchinfo'] = Label()
		self["overview"] = self.overview_label = ScrollLabel()
		self['key_red'] = Label(_("Exit"))
		self['key_green'] = Label()
		self['key_yellow'] = Label()
		self["key_blue"] = Label(_("more ...")) if self.service_path else Label("")
		self['list'] = self.list = List()
		self['cover'] = Pixmap()
		self['backdrop'] = Pixmap()

		HelpableScreen.__init__(self)
		self["actions"] = HelpableActionMap(
			self,
			"TMDBActions",
			{
				"cancel": (self.exit, _("Exit")),
				"up": (self.list.moveUp, _("Selection up")),
				"down": (self.list.moveDown, _("Selection down")),
				"nextBouquet": (self.overview_label.pageUp, _("Details down")),
				"prevBouquet": (self.overview_label.pageDown, _("Details up")),
				"right": (self.list.pageDown, _("Page down")),
				"left": (self.list.pageUp, _("Page down")),
				"red": (self.exit, _("Exit")),
				"blue": (self.showMenu, _("more ...")),
				"menu": (self.setup, _("Setup"))
			},
			-1,
		)

		self.onLayoutFinish.append(self.onFinish)
		self["list"].onSelectionChanged.append(self.onSelectionChanged)

	def onSelectionChanged(self):
		DelayTimer.stopAll()
		if self["list"].getCurrent():
			DelayTimer(200, self.showInfo)

	def onFinish(self):
		logger.debug("Selected: %s", self.movie)
		self.showPicture(self["backdrop"], "backdrop", self.ident, None)
		threads.deferToThread(self.getData, self.gotData)

	def getData(self, callback):
		self["searchinfo"].setText(_("Looking up: %s ...") % (self.movie + " - " + _("Seasons")))
		result = SearchSeason().getResult(self.result, self.ident)
		reactor.callFromThread(callback, result)  # pylint: disable=E1101

	def gotData(self, result):
		if not result:
			self["searchinfo"].setText(_("No results for: %s") % _("Seasons"))
		else:
			self["searchinfo"].setText(self.movie + " - " + _("Seasons"))
			self["list"].setList(result)

	def showMenu(self):
		self.menu(self.ident, self.overview)

	def showInfo(self):
		self["overview"].setText("...")
		current = self['list'].getCurrent()
		if current:
			cover_url = current[1]
			self.overview = current[2]
			self.ident = current[3]
			logger.debug("ident: %s", self.ident)
			self.showPicture(self["cover"], "cover", self.ident, cover_url)
			self["overview"].setText(self.overview)

	def setup(self):
		self.session.open(ScreenConfig)

	def exit(self):
		DelayTimer.stopAll()
		self["list"].onSelectionChanged.remove(self.onSelectionChanged)
		self.close(self.files_saved)
