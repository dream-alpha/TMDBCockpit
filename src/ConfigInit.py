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


from Components.config import config, ConfigYesNo, ConfigSelection, ConfigSubsection
from Components.Language import language
from .LanguageSelection import LanguageSelection
from .Debug import logger, setLogLevel, log_levels


class ConfigInit(LanguageSelection):

	def __init__(self):
		logger.info("...")
		LanguageSelection.__init__(self)
		lang = language.getActiveLanguage()
		logger.debug("lang: %s", lang)
		lang_choices = self.getLangChoices(lang)
		config.plugins.tmdb = ConfigSubsection()
		config.plugins.tmdb.debug_log_level = ConfigSelection(default="DEBUG", choices=list(log_levels.keys()))
		config.plugins.tmdb.cover_size = ConfigSelection(default="original", choices=["w92", "w185", "w500", "original"])
		config.plugins.tmdb.backdrop_size = ConfigSelection(default="original", choices=["w300", "w780", "w1280", "original"])
		config.plugins.tmdb.lang = ConfigSelection(default=lang[:2], choices=lang_choices)
		config.plugins.tmdb.skip_to_movie = ConfigYesNo(default=True)
		config.plugins.tmdb.key_yellow = ConfigYesNo(default=True)

		config.plugins.tmdb.trailer_player = ConfigSelection(default="MediaPortal", choices=["MediaPortal", "MyTube"])
		setLogLevel(log_levels[config.plugins.tmdb.debug_log_level.value])
