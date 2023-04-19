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


from Components.config import config
from . import tmdbsimple as tmdb
from .Debug import logger
from .Json import Json
from .Parsers import Parsers


class SearchPerson(Parsers, Json):
	def __init__(self):
		Parsers.__init__(self)
		Json.__init__(self)

	def getResult(self, result, ident):
		lang = config.plugins.tmdb.lang.value
		logger.debug("ident: %s", ident)
		keys = ["biography", "name", "birthday", "place_of_birth", "gender", "also_known_as", "popularity", "movie_credits", "tv_credits"]
		for lang in [config.plugins.tmdb.lang.value, "en"]:
			json_data = tmdb.People(ident).info(language=lang, append_to_response="movie_credits, tv_credits")
			# logger.debug("json_data: %s", json_data)
			self.parseJson(result, json_data, keys)
			if result["biography"]:
				break

		logger.debug("result: %s", result)

		self.parsePersonGender(result)
		self.parseJsonList(result, "also_known_as", ",")
		result["popularity"] = "%.1f" % float(result["popularity"])

		data_movies = []
		for source in [
			(result["movie_credits"], ["release_date", "title", "character"], "movie"),
			(result["tv_credits"], ["first_air_date", "name", "character"], "tv")]:
			result2 = {}
			self.parseJson(result2, source[0], ["cast"])
			logger.debug("result2: %s", result2)
			for cast in result2["cast"]:
				logger.debug("cast: %s", cast)
				movie = {}
				self.parseJson(movie, cast, source[1])
				logger.debug("movie: %s", movie)
				if source[2] == "movie":
					if movie["release_date"] != "None":
						data_movies.append(("%s %s (%s)" % (movie["release_date"], movie["title"], movie["character"])))
				else:
					if movie["first_air_date"] != "None":
						data_movies.append(("%s %s (%s)" % (movie["first_air_date"], movie["name"], movie["character"])))
		data_movies.sort(reverse=True)
		movies = "\n".join(data_movies)
		result["movies"] = movies
		del json_data
		return result
