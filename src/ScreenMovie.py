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
from twisted.internet import threads
from enigma import eServiceReference
from Components.PluginComponent import plugins
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ScrollLabel import ScrollLabel
from Screens.MoviePlayer import MoviePlayer
from Screens.HelpMenu import HelpableScreen
from Screens.ChoiceBox import ChoiceBox
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.LoadPixmap import LoadPixmap
from .__init__ import _
from .ConfigScreen import ConfigScreen
from .ScreenPeople import ScreenPeople
from .ScreenSeason import ScreenSeason
from .FileUtils import copyFile, writeFile, readFile, renameFile
from .Picture import Picture
from .Debug import logger
from .SkinUtils import getSkinPath
from .Utils import temp_dir
from .DelayTimer import DelayTimer
from .SearchMovie import SearchMovie


WHERE_SEARCH = 99


class ScreenMovie(SearchMovie, Picture, Screen, HelpableScreen):
	skin = readFile(getSkinPath("ScreenMovie.xml"))

	def __init__(self, session, movie, media, cover_url, ident, service_path, backdrop_url, search):
		logger.debug(
			"movie: %s, media: %s, cover_url: %s, ident: %s, service_path: %s, backdrop_url: %s",
			movie, media, cover_url, ident, service_path, backdrop_url
		)
		Screen.__init__(self, session)
		Picture.__init__(self)
		SearchMovie.__init__(self)
		self.title = "TMDB - The Movie Database - " + _("Movie Details")
		self.session = session
		self.movie = movie
		self.media = media
		self.cover_url = cover_url
		self.backdrop_url = backdrop_url
		self.ident = ident
		self.service_path = service_path
		self.files_saved = False
		self.overview = ""
		self.search = search

		self["genre"] = Label()
		self["genre_txt"] = Label()
		self["fulldescription"] = self.fulldescription = ScrollLabel("")
		self["rating"] = Label()
		self["votes"] = Label()
		self["votes_brackets"] = Label()
		self["votes_txt"] = Label()
		self["runtime"] = Label()
		self["runtime_txt"] = Label()
		self["year"] = Label()
		self["year_txt"] = Label()
		self["country"] = Label()
		self["country_txt"] = Label()
		self["director"] = Label()
		self["director_txt"] = Label()
		self["author"] = Label()
		self["author_txt"] = Label()
		self["studio"] = Label()
		self["studio_txt"] = Label()

		self.fields = {
			"genre": (_("Genre:"), "-"),
			"fulldescription": (None, ""),
			"rating": (None, "0.0"),
			"votes": (_("Votes:"), "-"),
			"votes_brackets": (None, ""),
			"runtime": (_("Runtime:"), "-"),
			"year": (_("Year:"), "-"),
			"country": (_("Countries:"), "-"),
			"director": (_("Director:"), "-"),
			"author": (_("Author:"), "-"),
			"studio": (_("Studio:"), "-"),
		}

		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Crew"))
		self["key_yellow"] = Label(_("Seasons")) if self.media == "tv" else Label("")
		self["key_blue"] = Label(_("more ...")) if self.service_path else Label("")

		self["searchinfo"] = Label()
		self["cover"] = Pixmap()
		self["backdrop"] = Pixmap()
		self["fsklogo"] = Pixmap()
		self["star"] = Pixmap()

		HelpableScreen.__init__(self)
		self["actions"] = HelpableActionMap(
			self,
			"TMDBActions",
			{
				"ok": (self.green, _("Crew")),
				"cancel": (self.exit, _("Exit")),
				"up": (self.fulldescription.pageUp, _("Selection up")),
				"down": (self.fulldescription.pageDown, _("Selection down")),
				"left": (self.fulldescription.pageUp, _("Page up")),
				"right": (self.fulldescription.pageDown, _("Page down")),
				"red": (self.exit, _("Exit")),
				"green": (self.green, _("Crew")),
				"yellow": (self.yellow, _("Seasons")),
				"blue": (self.menu, _("more ...")),
				"menu": (self.setup, _("Setup")),
				"eventview": (self.pluginsMenu, _("Search"))
			},
			-1,
		)

		self.onLayoutFinish.append(self.onDialogShow)

	def onDialogShow(self):
		logger.debug("movie: %s", self.movie)
		self.showPicture(self["cover"], "cover", self.ident, self.cover_url)
		self.showPicture(self["backdrop"], "backdrop", self.ident, self.backdrop_url)
		DelayTimer(10, self.getData)

	def getData(self):
		self["searchinfo"].setText(_("Looking up: %s ...") % self.movie)
		threads.deferToThread(self.getResult, self.ident, self.media, self.gotData)

	def gotData(self, result):
		if not result:
			self["searchinfo"].setText(_("No results for: %s") % self.movie)
			self.overview = ""
		else:
			self["searchinfo"].setText(self.movie)
			path = "/usr/lib/enigma2/python/Plugins/Extensions/tmdb/skin/images/star.png"
			self["star"].instance.setPixmap(LoadPixmap(path))
			path = "/usr/lib/enigma2/python/Plugins/Extensions/tmdb/skin/images/fsk_" + result["fsk"] + ".png"
			self["fsklogo"].instance.setPixmap(LoadPixmap(path))

			for field in self.fields:
				logger.debug("field: %s", field)
				logger.debug("result: %s", result[field])
				if self.fields[field][0]:
					self[field + "_txt"].setText(self.fields[field][0])
				if result[field]:
					self[field].setText(result[field])
				else:
					self[field].setText(self.fields[field][1])

			self.overview = result["overview"]

			if self.media == "movie":
				self.videos = result["videos"]
				self["key_yellow"].setText(_("Videos") + " (%s)" % len(self.videos))

	def menu(self):
		if self.service_path:
			options = [
				(_("Save movie description"), 1),
				(_("Delete movie EIT file"), 2),
				(_("Save movie cover"), 3),
				(_("Save movie backdrop"), 4),
				("1+2", 5),
				("1+3", 6),
				("1+2+3", 7),
				("1+2+3+4", 8),
				("3+4", 9)
			]
			self.session.openWithCallback(self.menuCallback, ChoiceBox, list=options)

	def menuCallback(self, ret):
		if ret is not None:
			option = ret[1]
			ident = str(self.ident)
			msg = _("File operation results:")
			service_filename = os.path.splitext(self.service_path)[0]
			logger.debug("service_filename: %s", service_filename)
			if option in [3, 6, 7, 8, 9]:
				cover = temp_dir + "cover" + ident + ".jpg"
				if os.path.isfile(cover):
					copyFile(cover, service_filename + ".jpg")
					msg += "\n" + _("Cover saved.")
					self.files_saved = True
					logger.debug("Cover %s.jpg created", service_filename)
				else:
					msg += "\n" + _("No cover available")

			if option in [4, 8, 9]:
				backdrop = temp_dir + "backdrop" + ident + ".jpg"
				if os.path.isfile(backdrop):
					copyFile(backdrop, service_filename + ".bdp.jpg")
					msg += "\n" + _("Backdrop saved.")
					self.files_saved = True
					logger.debug("Backdrop %s.bdp.jpg created", service_filename)
				else:
					msg += "\n" + _("No backdrop available")

			if option in [1, 5, 6, 7, 8]:
				text_file = service_filename + ".txt"
				if self.overview:
					writeFile(text_file, self.overview)
					logger.debug("%s created", text_file)
					msg += "\n" + _("Movie description saved.")
					self.files_saved = True
				else:
					msg += "\n" + _("No movie description available")

			if option in [2, 5, 7, 8]:
				eitFile = service_filename + ".eit"
				if os.path.isfile(eitFile):
					renameFile(eitFile, eitFile + ".bak")
					logger.debug("%s deleted", eitFile)
					msg += "\n" + _("EIT file deleted.")
				else:
					msg += "\n" + _("No EIT file available")

			self.session.open(MessageBox, msg, type=MessageBox.TYPE_INFO)

	def pluginsMenu(self):
		options = []
		self.plugins_list = plugins.getPlugins(where=WHERE_SEARCH)
		if self.plugins_list:
			if len(self.plugins_list) > 1:
				for i, plugin in enumerate(self.plugins_list):
					options.append((plugin.name, i))
				self.session.openWithCallback(self.pluginsMenuCallback, ChoiceBox, list=options)
			else:
				self.pluginsMenuCallback((None, 0))
		else:
			self.session.open(MessageBox, _("No search provider registered."), type=MessageBox.TYPE_INFO)

	def pluginsMenuCallback(self, ret):
		if ret is not None:
			option = ret[1]
			plugin = self.plugins_list[option]
			plugin(self.session, self.search)

	def setup(self):
		self.session.open(ConfigScreen)

	def yellow(self):
		if self.media == "tv":
			self.session.open(ScreenSeason, self.movie, self.ident, self.media)
		elif self.media == "movie" and self.videos:
			videolist = []
			for video in self.videos:
				vKey = video["key"]
				vName = video["name"]
				# sref ="8193:0:1:0:0:0:0:0:0:0:mp_yt%3a//lkL_84wQ9OY:VideoName"
				vLink = "8193:0:1:0:0:0:0:0:0:0:mp_yt%3a//"
				videolist.append((str(vName), str(vLink + "%s:%s" % (vKey, vName))))

			if len(videolist) > 1:
				videolist = sorted(videolist, key=lambda x: x[0])
				self.session.openWithCallback(
					self.videolistCallback,
					ChoiceBox,
					windowTitle=_("TMDB videos"),
					title=_("Please select a video"),
					list=videolist,
				)
			elif len(videolist) == 1:
				self.videolistCallback(videolist[0])

	def videolistCallback(self, ret):
		ret = ret and ret[1]
		if ret:
			self.session.open(MoviePlayer, eServiceReference(ret), streamMode=True, askBeforeLeaving=False)

	def green(self):
		self.session.open(ScreenPeople, self.movie, self.ident , self.media, self.cover_url, self.backdrop_url)

	def exit(self):
		self.close(self.files_saved)
