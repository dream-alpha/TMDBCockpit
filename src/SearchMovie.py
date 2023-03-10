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
from .Parsers import Parsers


class SearchMovie(Parsers, Json):
	def __init__(self):
		Parsers.__init__(self)
		Json.__init__(self)

	def getResult(self, ident, media, callback):
		lang = config.plugins.tmdb.lang.value
		logger.debug("ident: %s", ident)
		result = {}
		try:
			keys = ["overview", "year", "vote_average", "vote_count", "runtime", "production_countries", "production_companies", "genres", "tagline", "release_date", "seasons", "videos"]
			if media == "movie":
				json_data = tmdb.Movies(ident).info(language=lang, append_to_response="videos")
				# logger.debug("json_data: %s", json_data)
				result = {}
				self.parseJson(result, json_data, ["overview"])
				if result["overview"] == "":
					json_data = tmdb.Movies(ident).info(language="en")
				# logger.debug("json_data: %s", json_data)
				# logger.debug("keys: %s", keys)
				self.parseJson(result, json_data, keys)
				json_data = tmdb.Movies(ident).credits(language=lang)
				# logger.debug("json_data_cast: %s", json_data)
				self.parseJson(result, json_data, ["cast", "crew"])
				json_data = tmdb.Movies(ident).releases(language=lang)
				# logger.debug("json_data_fsk: %s", json_data)
				self.parseJson(result, json_data, ["countries"])
				del json_data
			elif media == "tv":
				json_data = tmdb.TV(ident).info(language=lang)
				# logger.debug("json_data: %s", json_data)
				result = {}
				self.parseJson(result, json_data, ["overview"])
				if result["overview"] == "":
					json_data = tmdb.TV(ident).info(language="en")
				# logger.debug("json_data: %s", json_data)
				keys += ["first_air_date", "origin_country", "created_by", "networks", "number_of_seasons", "number_of_episodes"]
				# logger.debug("keys: %s", keys)
				self.parseJson(result, json_data, keys)
				json_data = tmdb.TV(ident).credits(language=lang)
				# logger.debug("json_data_cast: %s", json_data)
				self.parseJson(result, json_data, ["cast", "crew"])
				json_data = tmdb.TV(ident).content_ratings(language=lang)
				# logger.debug("json_data_fsk: %s", json_data)
				self.parseJson(result, json_data, ["results"])
				del json_data
			else:
				raise Exception("unsupported media: %s" % media)
		except Exception as e:
			logger.error("exception: %s", e)
			result = {}
		else:
			# base for movie and tv series
			result["year"] = result["release_date"][:4]
			result["rating"] = "%s" % format(float(result["vote_average"]), ".1f")
			result["votes"] = str(result["vote_count"])
			result["votes_brackets"] = "(%s)" % str(result["vote_count"])
			result["runtime"] = "%s" % result["runtime"] + " " + _("min")

			self.parseCountry(result)
			self.parseGenre(result)
			self.parseCast(result)
			self.parseCrew(result)
			self.parseStudio(result)
			self.parseFsk(result, media)

			if media == "movie":
				result["seasons"] = ""
				self.parseMovieVideos(result)

			elif media == "tv":
				# modify data for TV/Series
				result["year"] = result["first_air_date"][:4]

				self.parseTVCountry(result)
				self.parseTVCrew(result)
				self.parseTVStudio(result)
				self.parseTVSeasons(result)

			result["fulldescription"] = \
				result["tagline"] + "\n" \
				+ "%s, %s, %s" % (result["genre"], result["country"], result["year"]) + "\n\n" \
				+ result["overview"] + "\n\n" + result["cast"] + "\n" + result["crew"] + "\n"\
				+ result["seasons"]

		reactor.callFromThread(callback, result)  # pylint: disable=E1101
