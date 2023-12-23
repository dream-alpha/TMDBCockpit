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


class SearchTMDB(Json):

	def __init__(self):
		Json.__init__(self)

	def getResult(self, res, text):
		logger.info("text: >%s<", text)
		lang = config.plugins.tmdb.lang.value
		json_data = {}
		results = {}
		media = "movie"
		json_data = tmdb.Search().multi(query=text, language=lang)
		self.parseJson(results, json_data, ["results"])
		logger.debug("json_data: %s", json_data)

		for entry in results["results"]:
			logger.debug("entry: %s", entry)
			result = {}
			keys = ["media_type", "id", "title", "name", "release_date", "first_air_date", "poster_path", "backdrop_path", "profile_path"]
			self.parseJson(result, entry, keys)

			ident = result["id"]
			title = result["title"] if media == "movie" else result["name"]
			cover_url = "http://image.tmdb.org/t/p/%s%s" % (config.plugins.tmdb.cover_size.value, result["poster_path"])
			backdrop_url = "http://image.tmdb.org/t/p/%s%s" % (config.plugins.tmdb.backdrop_size.value, result["backdrop_path"])

			logger.debug("ident: %s, title: %s, media: %s", ident, title, media)
			if ident and title and media:
				res.append(((title, ident, media, cover_url, backdrop_url), ))
				break
		del json_data
		return res
