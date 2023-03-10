#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This plugin is free software, you are allowed to
# modify it (if you keep the license),
# but you are not allowed to distribute/publish
# it without source code (this version and your modifications).
# This means you also have to distribute
# source code of your modifications.

from Components.ActionMap import ActionMap
from Components.config import config, configfile, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
from .__init__ import _
from .Version import PLUGIN, VERSION


class ConfigScreen(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ["ConfigScreen", "Setup"]
		self.setup_title = _("Setup")

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

		self["key_green"] = StaticText(_("OK"))
		self["key_red"] = StaticText(_("Cancel"))

		self.list = []
		self.createConfigList()
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(PLUGIN + " - " + VERSION)

	def createConfigList(self):
		self.list = []
		self.list.append(getConfigListEntry(_("Language:"), config.plugins.tmdb.lang))
		self.list.append(getConfigListEntry(_("Skip to movie details for single result:"), config.plugins.tmdb.skip_to_movie))
		self.list.append(getConfigListEntry(_("Yellow key for TMDB infos in EPGs:"), config.plugins.tmdb.key_yellow))
		self.list.append(getConfigListEntry(_("Cover resolution:"), config.plugins.tmdb.cover_size))
		self.list.append(getConfigListEntry(_("Backdrop resolution:"), config.plugins.tmdb.backdrop_size))
		self.list.append(getConfigListEntry(_("Use internal TMDB API key:"), config.plugins.tmdb.internal_api_key))
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
