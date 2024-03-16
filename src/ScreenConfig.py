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


from Components.ActionMap import ActionMap
from Components.config import config, configfile, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Screens.Screen import Screen
from .__init__ import _
from .Version import PLUGIN, VERSION


class ScreenConfig(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = "ScreenConfig"

		self.onChangedEntry = []
		self.list = []
		ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)

		self["actions"] = ActionMap(
			["TMDBActions"],
			{
				"cancel": self.exit,
				"save": self.ok,
				"red": self.exit,
				"green": self.ok,
			},
			-2
		)

		self["key_green"] = Label(_("OK"))
		self["key_red"] = Label(_("Cancel"))

		self.list = []
		self.createConfigList()
		self.onLayoutFinish.append(self.__onLayoutFinish)

	def __onLayoutFinish(self):
		self.setTitle(PLUGIN + " - " + VERSION)

	def createConfigList(self):
		self.list = []
		self.list.append(getConfigListEntry(_("Language:"), config.plugins.tmdb.lang))
		self.list.append(getConfigListEntry(_("Skip to movie details for single result:"), config.plugins.tmdb.skip_to_movie))
		self.list.append(getConfigListEntry(_("Yellow key for TMDB infos in EPGs:"), config.plugins.tmdb.key_yellow))
		self.list.append(getConfigListEntry(_("Cover resolution:"), config.plugins.tmdb.cover_size))
		self.list.append(getConfigListEntry(_("Backdrop resolution:"), config.plugins.tmdb.backdrop_size))
		self.list.append(getConfigListEntry(_("Player for trailers:"), config.plugins.tmdb.trailer_player))
		self["config"].setList(self.list)

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def ok(self):
		for x in self["config"].list:
			x[1].save()
		configfile.save()
		self.close()

	def exit(self):
		self.close()
