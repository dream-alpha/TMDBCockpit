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


from twisted.internet import threads, reactor
from enigma import eServiceReference
from Components.PluginComponent import plugins
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ScrollLabel import ScrollLabel
from Screens.ChoiceBox import ChoiceBox
from Screens.MoviePlayer import MoviePlayer
from Screens.HelpMenu import HelpableScreen
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.LoadPixmap import LoadPixmap
from .__init__ import _
from .ScreenConfig import ScreenConfig
from .ScreenPeople import ScreenPeople
from .ScreenSeason import ScreenSeason
from .Picture import Picture
from .Debug import logger
from .SearchMovie import SearchMovie
from .MoreOptions import MoreOptions


WHERE_SEARCH = -99


class ScreenMovie(MoreOptions, Picture, Screen, HelpableScreen):
	def __init__(self, session, movie, media, cover_url, ident, service_path, backdrop_url):
		logger.debug(
			"movie: %s, media: %s, cover_url: %s, ident: %s, service_path: %s, backdrop_url: %s",
			movie, media, cover_url, ident, service_path, backdrop_url
		)
		Screen.__init__(self, session)
		Picture.__init__(self)
		MoreOptions.__init__(self, session, service_path)
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
		self.result = {}

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
				"blue": (self.showMenu, _("more ...")),
				"menu": (self.setup, _("Setup")),
				"eventview": (self.pluginsMenu, _("Search"))
			},
			-1,
		)

		self.onLayoutFinish.append(self.__onLayoutFinish)

	def __onLayoutFinish(self):
		logger.debug("movie: %s", self.movie)
		self.showPicture(self["cover"], "cover", self.ident, self.cover_url)
		self.showPicture(self["backdrop"], "backdrop", self.ident, self.backdrop_url)
		self["searchinfo"].setText(_("Looking up: %s ...") % self.movie)
		threads.deferToThread(self.getData, self.gotData)

	def getData(self, callback):
		result = SearchMovie().getResult(self.result, self.ident, self.media)
		logger.debug("result: %s", result)
		reactor.callFromThread(callback, result)  # pylint: disable=E1101

	def gotData(self, result):
		if not result:
			self["searchinfo"].setText(_("No results for: %s") % self.movie)
			self.overview = ""
		else:
			self["searchinfo"].setText(self.movie)
			path = "/usr/lib/enigma2/python/Plugins/Extensions/TMDBCockpit/skin/images/star.png"
			self["star"].instance.setPixmap(LoadPixmap(path))
			path = "/usr/lib/enigma2/python/Plugins/Extensions/TMDBCockpit/skin/images/fsk_" + result["fsk"] + ".png"
			self["fsklogo"].instance.setPixmap(LoadPixmap(path))

			for field in self.fields:
				# logger.debug("field: %s", field)
				# logger.debug("result: %s", result[field])
				if self.fields[field][0]:
					self[field + "_txt"].setText(self.fields[field][0])
				if result[field]:
					self[field].setText(result[field])
				else:
					self[field].setText(self.fields[field][1])

			self.overview = result["overview"]

			self.movie_title = self.original_title = ""
			if self.media == "movie":
				self.movie_title = result["title"]
				self.original_title = result["original_title"]
				self.videos = result["videos"]
				self["key_yellow"].setText(_("Videos") + " (%s)" % len(self.videos))
			elif self.media == "tv":
				self.movie_title = result["name"]

	def showMenu(self):
		self.menu(self.ident, self.overview)

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
			plugin(self.session, self.movie_title, self.original_title)

	def setup(self):
		self.session.open(ScreenConfig)

	def yellow(self):
		if self.media == "tv":
			self.session.openWithCallback(self.screenSeasonCallback, ScreenSeason, self.movie, self.ident, self.media, self.service_path)
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

	def screenSeasonCallback(self, files_saved):
		self.files_saved = files_saved

	def videolistCallback(self, ret):
		ret = ret and ret[1]
		if ret:
			self.session.open(MoviePlayer, eServiceReference(ret), streamMode=True, askBeforeLeaving=False)

	def green(self):
		self.session.open(ScreenPeople, self.movie, self.ident , self.media, self.cover_url, self.backdrop_url)

	def exit(self):
		self.close(self.files_saved)
