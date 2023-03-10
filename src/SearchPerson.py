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


from twisted.internet import reactor
from Components.config import config
from . import tmdbsimple as tmdb
from .__init__ import _
from .Debug import logger
from .Json import Json


class SearchPerson(Json):
	def __init__(self):
		Json.__init__(self)

	def getResult(self, ident, callback):
		lang = config.plugins.tmdb.lang.value
		logger.debug("ident: %s", ident)
		result = {}
		try:
			json_person = tmdb.People(ident).info(language=lang)
			self.parseJson(result, json_person, ["biography"])
			if not result["biography"]:
				json_person = tmdb.People(ident).info(language="en")
				self.parseJson(result, json_person, ["biography"])
			# logger.debug("json_person: %s", json_person)
			json_person_movie = tmdb.People(ident).movie_credits(language=lang)
			# logger.debug("json_person_movie: %s", json_person_movie)
			json_person_tv = tmdb.People(ident).tv_credits(language=lang)
			# logger.debug("json_person_tv: %s", json_person_tv)
		except Exception as e:
			logger.error("exception: %s", e)
			result = {}
		else:
			keys = ["name", "birthday", "place_of_birth", "gender", "also_known_as", "popularity"]
			self.parseJson(result, json_person, keys)
			logger.debug("result: %s", result)

			gender = result["gender"]
			if gender == "1":
				gender = _("female")
			elif gender == "2":
				gender = _("male")
			elif gender == "divers":
				gender = _("divers")
			else:
				gender = _("None")
			result["gender"] = gender

			self.parseJsonList(result, "also_known_as", ",")
			result["popularity"] = "%.1f" % float(result["popularity"])

			data_movies = []
			for source in [
				(json_person_movie, ["release_date", "title", "character"], "movie"),
				(json_person_tv, ["first_air_date", "name", "character"], "tv")]:
				result2 = {}
				self.parseJson(result2, source[0], ["cast"])
				logger.debug("result2: %s", result2)
				for cast in result2["cast"]:
					logger.debug("cast: %s", cast)
					movie = {}
					self.parseJson(movie, cast, source[1])
					logger.debug("movie: %s", movie)
					if source[2] == "movie":
						data_movies.append(("%s %s (%s)" % (movie["release_date"], movie["title"], movie["character"])))
					else:
						data_movies.append(("%s %s (%s)" % (movie["first_air_date"], movie["name"], movie["character"])))
			data_movies.sort(reverse=True)
			movies = "\n".join(data_movies)
			result["movies"] = movies
		reactor.callFromThread(callback, result)  # pylint: disable=E1101
