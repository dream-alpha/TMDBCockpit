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

from twisted.internet import threads
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Screens.HelpMenu import HelpableScreen
from Screens.Screen import Screen
from .__init__ import _
from .List import List
from .ConfigScreen import ConfigScreen
from .ScreenPerson import ScreenPerson
from .Picture import Picture
from .Debug import logger
from .SkinUtils import getSkinPath
from .FileUtils import readFile
from .DelayTimer import DelayTimer
from .SearchPeople import SearchPeople


class ScreenPeople(SearchPeople, Picture, Screen, HelpableScreen):
	skin = readFile(getSkinPath("ScreenPeople.xml"))

	def __init__(self, session, movie, ident, media, cover_url, backdrop_url):
		logger.info("movie %s, ident: %s, media: %s, cover_url: %s, backdrop_url: %s", movie, ident, media, cover_url, backdrop_url)
		Screen.__init__(self, session)
		Picture.__init__(self)
		self.title = "TMDB - The Movie Database - " + _("Crew")
		SearchPeople.__init__(self)
		self.session = session
		self.movie = movie
		self.ident = ident
		self.media = media
		self.cover_url = cover_url
		self.backdrop_url = backdrop_url

		self['searchinfo'] = Label()
		self['key_red'] = Label(_("Exit"))
		self['key_green'] = Label(_("Details"))
		self["key_yellow"] = Label()
		self['key_blue'] = Label()
		self['list'] = self.list = List()
		self['cover'] = Pixmap()
		self['backdrop'] = Pixmap()

		HelpableScreen.__init__(self)
		self["actions"] = HelpableActionMap(
			self,
			"TMDBActions",
			{
				"ok": (self.ok, _("Show details")),
				"cancel": (self.exit, _("Exit")),
				"up": (self.list.moveUp, _("Selection up")),
				"down": (self.list.moveDown, _("Selection down")),
				"right": (self.list.pageDown, _("Page down")),
				"left": (self.list.pageUp, _("Page down")),
				"red": (self.exit, _("Exit")),
				"green": (self.ok, _("Show details")),
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
		logger.debug("movie: %s", self.movie)
		self.showPicture(self["backdrop"], "backdrop", self.ident, self.backdrop_url)
		self.getData()

	def getData(self):
		self["searchinfo"].setText(_("Looking up: %s ...") % (self.movie + " - " + _("Crew")))
		threads.deferToThread(self.getResult, self.ident, self.media, self.gotData)

	def gotData(self, result):
		if not result:
			self["searchinfo"].setText(_("No results for: %s") % _("Crew"))
		else:
			self["searchinfo"].setText(self.movie + " - " + _("Crew"))
			self["list"].setList(result)
			# self.showInfo()

	def showInfo(self):
		current = self["list"].getCurrent()
		if current:
			cover_url = current[2]
			cover_ident = current[3]
			self.showPicture(self["cover"], "cover", cover_ident, cover_url)

	def ok(self):
		current = self['list'].getCurrent()
		if current:
			name = current[1]
			cover_ident = current[3]
			if cover_ident:
				self.session.open(ScreenPerson, name, cover_ident, self.ident)

	def setup(self):
		self.session.open(ConfigScreen)

	def exit(self):
		self["list"].onSelectionChanged.remove(self.onSelectionChanged)
		self.close()
