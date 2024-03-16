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


from Screens.EpgSelection import EPGSelection
from Components.ActionMap import ActionMap
from .ScreenMain import ScreenMain
from .__init__ import _


original_init = None


def initEPGSelection():
	global original_init
	if original_init is None:
		original_init = EPGSelection.__init__
	EPGSelection.__init__ = our_init


def our_init(self, session, service, zapFunc=None, eventid=None, bouquetChangeCB=None, serviceChangeCB=None):
	def yellow():
		event_name = ""
		current = self["list"].getCurrent()
		if current and current[0]:
			event_name = current[0].getEventName()
		session.open(ScreenMain, event_name, 2)

	original_init(self, session, service, zapFunc, eventid, bouquetChangeCB, serviceChangeCB)
	self["tmdb_actions"] = ActionMap(
		["EPGSelectActions"],
		{
			"yellow": yellow,
		}
	)
	self["key_yellow"].setText(_("TMDB Infos ..."))
