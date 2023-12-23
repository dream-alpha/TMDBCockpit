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
from .__init__ import _
from .Debug import logger
from .Json import Json
from .Parsers import Parsers


class SearchMovie(Parsers, Json):
	def __init__(self):
		Parsers.__init__(self)
		Json.__init__(self)

	def getResult(self, result, ident, media):
		logger.debug("ident: %s, media: %s", ident, media)
		json_data = {}
		keys_movie = ["title", "original_title", "overview", "year", "vote_average", "vote_count", "runtime", "production_countries", "production_companies", "genres", "tagline", "release_date", "seasons", "videos", "credits", "releases"]
		keys_tv = keys_movie + ["name", "first_air_date", "origin_country", "created_by", "networks", "number_of_seasons", "number_of_episodes", "credits", "content_ratings"]
		for lang in [config.plugins.tmdb.lang.value, "en"]:
			if media == "movie":
				json_data = tmdb.Movies(ident).info(language=lang, append_to_response="videos,credits,releases")
				# logger.debug("json_data: %s", json_data)
				self.parseJson(result, json_data, keys_movie)
				if result["overview"]:
					break
			if media == "tv":
				json_data = tmdb.TV(ident).info(language=lang, append_to_response="videos,credits,content_ratings")
				# logger.debug("json_data: %s", json_data)
				self.parseJson(result, json_data, keys_tv)
				if result["overview"]:
					break
			del json_data

		# base for movie and tv series
		result["year"] = result["release_date"][:4]
		result["rating"] = "%.1f" % float(result["vote_average"])
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
			"%s\n" % result["tagline"] \
			+ "%s, %s, %s\n\n" % (result["genre"], result["country"], result["year"]) \
			+ "%s \n\n" % result["overview"] \
			+ "%s\n%s\n%s\n" % (result["cast"], result["crew"], result["seasons"])
		logger.debug("result: %s", result)
		return result
