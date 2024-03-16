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


from .__init__ import _
from .Json import Json


class Parsers(Json):
	def __init__(self):
		Json.__init__(self)

	def parseCountry(self, result):
		country_string = ""
		for country in result["production_countries"]:
			result1 = {}
			self.parseJson(result1, country, ["iso_3166_1"])
			if country_string:
				country_string += "/"
			country_string += result1["iso_3166_1"]
		result["country"] = country_string
		result.pop("production_countries", None)

	def parseGenre(self, result):
		genre_string = ""
		for genre in result["genres"]:
			result1 = {}
			self.parseJson(result1, genre, ["name"])
			if genre_string:
				genre_string += ", "
			genre_string += result1["name"]
		result["genre"] = genre_string

	def parseCast(self, result):
		cast_string = ""
		result1 = result["credits"]
		for cast in result1["cast"]:
			result2 = {}
			self.parseJson(result2, cast, ["name", "character"])
			cast_string += "%s (%s)\n" % (result2["name"], result2["character"])
		result["cast"] = cast_string

	def parseCrew(self, result):
		crew_string = ""
		director = ""
		author = ""
		result1 = result["credits"]
		for crew in result1["crew"]:
			result2 = {}
			self.parseJson(result2, crew, ["name", "job"])
			crew_string += "%s (%s)\n" % (result2["name"], result2["job"])
			if result2["job"] == "Director":
				if director:
					director += "\n"
				director += result2["name"]
			if result2["job"] == "Screenplay" or result2["job"] == "Writer":
				if author:
					author += "\n"
				author += result2["name"]
		result["crew"] = crew_string
		result["director"] = director
		result["author"] = author

	def parseStudio(self, result):
		studio_string = ""
		for studio in result["production_companies"]:
			result1 = {}
			self.parseJson(result1, studio, ["name"])
			if studio_string:
				studio_string += ", "
			studio_string += result1["name"]
		result["studio"] = studio_string

	def parseFsk(self, result, media):
		fsk = ""
		keys = []
		if media == "movie":
			keys = ["countries", "certification"]
			result1 = result["releases"]
		elif media == "tv":
			keys = ["results", "rating"]
			result1 = result["content_ratings"]
		if keys:
			for country in result1[keys[0]]:
				result2 = {}
				self.parseJson(result2, country, ["iso_3166_1", keys[1]])
				if result2["iso_3166_1"] == "DE":
					fsk = result2[keys[1]].strip("+")
		result["fsk"] = fsk

	def parseMovieVideos(self, result):
		result1 = {}
		self.parseJson(result1, result["videos"], ["results"])
		result["videos"] = result1["results"]
		videos = []
		for video in result["videos"]:
			result1 = {}
			self.parseJson(result1, video, ["site"])
			if result1["site"] == "YouTube":
				videos.append(video)
		result["videos"] = videos

	def parseTVCountry(self, result):
		self.parseJsonList(result, "origin_country", "/")
		result["country"] = result["origin_country"]

	def parseTVCrew(self, result):
		director = ""
		for directors in result["created_by"]:
			result1 = {}
			self.parseJson(result1, directors, ["name"])
			if director:
				director += "\n"
			director += result1["name"]
		result["director"] = _("Various")
		result["author"] = director

	def parseTVStudio(self, result):
		studio_string = ""
		for studio in result["networks"]:
			result1 = {}
			self.parseJson(result1, studio, ["name"])
			if studio_string:
				studio_string += ", "
			studio_string += result1["name"]
		result["studio"] = studio_string

	def parseTVSeasons(self, result):
		seasons = result["number_of_seasons"]
		episodes = result["number_of_episodes"]
		result["runtime"] = "%s %s / %s %s" % (seasons, _("Seasons"), episodes, _("Episodes"))

		seasons_string = ""
		for seasons in result["seasons"]:
			result1 = {}
			self.parseJson(result1, seasons, ["season_number", "episode_count", "air_date"])
			# logger.debug("seasons: %s", result1)
			if int(result1["season_number"]) >= 1:
				seasons_string += "%s %s: %s %s (%s)\n" % (_("Season"), result1["season_number"], result1["episode_count"], _("Episodes"), result1["air_date"][:4])
		result["seasons"] = seasons_string

	def parsePersonGender(self, result):
		gender = result["gender"]
		if gender == 1:
			gender = _("female")
		elif gender == 2:
			gender = _("male")
		elif gender == "divers":
			gender = _("divers")
		else:
			gender = _("not specified")
		result["gender"] = gender
