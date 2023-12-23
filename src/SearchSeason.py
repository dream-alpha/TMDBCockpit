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

from Components.config import config
from . import tmdbsimple as tmdb
from .Debug import logger
from .Json import Json


class SearchSeason(Json):
	def __init__(self):
		Json.__init__(self)

	def getResult(self, res, ident):
		logger.info("ident: %s", ident)
		lang = config.plugins.tmdb.lang.value
		json_data = tmdb.TV(ident).info(language=lang)
		result = {}
		self.parseJson(result, json_data, ["seasons"])
		for seasons in result["seasons"]:
			result1a = {}
			self.parseJson(result1a, seasons, ["season_number", "id"])
			season_ident = result1a["id"]
			season_number = result1a["season_number"]
			logger.debug("season_number: %s", season_number)

			json_data = tmdb.TV_Seasons(ident, season_number).info(language=lang)
			logger.debug("json_data: %s", json_data)
			result2 = {}
			self.parseJson(result2, json_data, ["name", "air_date", "title", "overview", "poster_path", "episodes"])
			air_date = "(%s)" % result2["air_date"][:4]
			title = result2["name"]
			title = "%s %s" % (title, air_date)
			overview = result2["overview"]
			cover_path = result2["poster_path"]
			logger.debug("cover_path: %s", cover_path)
			cover_url = "http://image.tmdb.org/t/p/%s/%s" % (config.plugins.tmdb.cover_size.value, cover_path)
			if ident and title:
				res.append(((title, cover_url, overview, season_ident), ))

			for names in result2["episodes"]:
				result2a = {}
				self.parseJson(result2a, names, ["id", "name", "title", "episode_number", "overview", "still_path"])
				episode_ident = result2a["id"]
				title = result2a["episode_number"]
				name = result2a["name"]
				title = "%+6s %s" % (title, name)
				overview = result2a["overview"]
				cover_path = result2a["still_path"]
				logger.debug("cover_path: %s", cover_path)
				cover_url = "http://image.tmdb.org/t/p/%s/%s" % (config.plugins.tmdb.cover_size.value, cover_path)
				if ident and title:
					res.append(((title, cover_url, overview, episode_ident), ))
		del json_data
		return res
