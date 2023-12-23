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


class SearchPeople(Json):
	def __init__(self):
		Json.__init__(self)

	def getResult(self, res, ident, media):
		logger.info("ident: %s", ident)
		json_data = {}
		lang = config.plugins.tmdb.lang.value
		if media == "movie":
			json_data = tmdb.Movies(ident).credits(language=lang)
			logger.debug("json_data: %s", json_data)
		if media == "tv":
			json_data = tmdb.TV(ident).info(language=lang, append_to_result="credits")
			logger.debug("json_data: %s", json_data)

		result = {}
		self.parseJson(result, json_data, ["cast", "seasons", "credits"])

		for casts in result["cast"]:
			result2 = {}
			keys = ["id", "name", "profile_path", "character"]
			self.parseJson(result2, casts, keys)
			cover_ident = result2["id"]
			name = result2["name"]
			title = "%s (%s)" % (result2["name"], result2["character"])
			cover_path = result2["profile_path"]
			cover_url = "http://image.tmdb.org/t/p/%s/%s" % (config.plugins.tmdb.cover_size.value, cover_path)
			if cover_ident and name != "None":
				res.append(((title, name, cover_url, cover_ident), ))

		if media == "tv":
			season_number = 1
			for season in result["seasons"]:
				# logger.debug("######: %s", season)
				result2 = {}
				keys2 = ["season_number", "id", "name", "air_date"]
				self.parseJson(result2, season, keys2)
				season_number = result2["season_number"]
				# logger.debug("#########: %s", result2["season_number"])
				cover_ident = result2["id"]
				name = result2["name"]
				date = result2["air_date"][:4]
				title = "%s (%s)" % (name, date)
				logger.debug("title: %s", title)
				logger.debug("name: %s", name)
				if name != "None":
					res.append(((title, name, None, ""), ))

					json_data = tmdb.TV_Seasons(ident, season_number).credits(language=lang)
					result3 = {}
					self.parseJson(result3, json_data, ["cast"])
					for casts in result3["cast"]:
						result4 = {}
						keys4 = ["id", "name", "character", "profile_path"]
						self.parseJson(result4, casts, keys4)
						cover_ident = result4["id"]
						name = result4["name"]
						character = result4["character"]
						title = "    %s (%s)" % (name, character)
						cover_path = result4["profile_path"]
						cover_url = "http://image.tmdb.org/t/p/%s%s" % (config.plugins.tmdb.cover_size.value, cover_path)

						if cover_ident and name != "None":
							res.append(((title, name, cover_url, cover_ident), ))
		del json_data
		logger.debug("res: %s", res)
		return res
