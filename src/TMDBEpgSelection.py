#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This plugin is free software, you are allowed to
# modify it (if you keep the license),
# but you are not allowed to distribute/publish
# it without source code (this version and your modifications).
# This means you also have to distribute
# source code of your modifications.


from Screens.EpgSelection import EPGSelection
from Components.ActionMap import ActionMap
from .ScreenMain import ScreenMain
from .__init__ import _


# Overwrite EPGSelection.__init__ with our modified one
baseEPGSelection__init__ = None


def initEPGSelection():
	global baseEPGSelection__init__
	if baseEPGSelection__init__ is None:
		baseEPGSelection__init__ = EPGSelection.__init__
	EPGSelection.__init__ = EPGSelection__init__


# Modified EPGSelection __init__
def EPGSelection__init__(self, session, service, zapFunc=None, eventid=None, bouquetChangeCB=None, serviceChangeCB=None):
	baseEPGSelection__init__(self, session, service, zapFunc, eventid, bouquetChangeCB, serviceChangeCB)

	def yellowClicked():
		cur = self["list"].getCurrent()
		if cur[0] is not None:
			name = cur[0].getEventName()
		else:
			name = ""
		session.open(ScreenMain, name, 2)

	self["tmdb_actions"] = ActionMap(
		["EPGSelectActions"],
		{
			"yellow": yellowClicked,
		}
	)

	self["key_yellow"].text = _("TMDB Infos ...")
