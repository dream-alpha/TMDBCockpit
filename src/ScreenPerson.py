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
from Components.ScrollLabel import ScrollLabel
from Screens.HelpMenu import HelpableScreen
from Screens.Screen import Screen
from .__init__ import _
from .Picture import Picture
from .Debug import logger
from .FileUtils import readFile
from .SkinUtils import getSkinPath
from .ConfigScreen import ConfigScreen
from .SearchPerson import SearchPerson


class ScreenPerson(SearchPerson, Picture, Screen, HelpableScreen):
	skin = readFile(getSkinPath("ScreenPerson.xml"))

	def __init__(self, session, person, cover_ident, backdrop_ident):
		logger.info("cover_ident: %s, backdrop_ident: %s", cover_ident, backdrop_ident)
		Screen.__init__(self, session)
		Picture.__init__(self)
		self.title = "TMDB - The Movie Database - " + _("Person Details")
		SearchPerson.__init__(self)
		self.session = session
		self.person = person
		self.cover_ident = cover_ident
		self.backdrop_ident = backdrop_ident

		self['searchinfo'] = Label()
		self['fulldescription'] = self.fulldescription = ScrollLabel("")
		self['cover'] = Pixmap()
		self['backdrop'] = Pixmap()

		self['key_red'] = Label(_("Exit"))
		self['key_green'] = Label()
		self['key_yellow'] = Label()
		self['key_blue'] = Label()

		HelpableScreen.__init__(self)
		self["actions"] = HelpableActionMap(
			self,
			"TMDBActions",
			{
				"cancel": (self.exit, _("Exit")),
				"up": (self.fulldescription.pageUp, _("Selection up")),
				"down": (self.fulldescription.pageDown, _("Selection down")),
				"left": (self.fulldescription.pageUp, _("Page up")),
				"right": (self.fulldescription.pageDown, _("Page down")),
				"red": (self.exit, _("Exit")),
				"menu": (self.setup, _("Setup")),
			},
			-1,
		)

		self.onLayoutFinish.append(self.onFinish)

	def onFinish(self):
		self.showPicture(self["backdrop"], "backdrop", self.backdrop_ident, None)
		self.showPicture(self["cover"], "cover", self.cover_ident, None)
		self.getData()

	def getData(self):
		self["searchinfo"].setText(_("Looking up: %s ...") % self.person)
		threads.deferToThread(self.getResult, self.cover_ident, self.gotData)

	def gotData(self, result):
		if not result:
			self["searchinfo"].setText(_("No results for: %s") % self.person)
		else:
			self["searchinfo"].setText(result["name"])
			fulldescription = result["birthday"] + ", " \
				+ result["place_of_birth"] + ", " \
				+ result["gender"] + "\n" \
				+ result["also_known_as"] + "\n" \
				+ _("Popularity") + ": " + result["popularity"] + "\n\n" \
				+ result["biography"] + "\n\n" \
				+ _("Known for:") + "\n" \
				+ result["movies"]
			self["fulldescription"].setText(fulldescription)

	def setup(self):
		self.session.open(ConfigScreen)

	def exit(self):
		self.close()
