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


from Components.language_cache import LANG_TEXT
from .Debug import logger


class LanguageSelection():

	def __init__(self):
		return

	def getLangChoices(self, sys_lang):
		logger.info("sys_lang: %s", sys_lang)
		if sys_lang == "en_EN":
			sys_lang = "en_GB"
		langs = LANG_TEXT[sys_lang]
		choices = []
		for lang in langs:
			if "_" in lang:
				choice = (lang[:2], langs[lang])
				choices.append(choice)
		logger.debug("choices: %s", choices)
		return choices
