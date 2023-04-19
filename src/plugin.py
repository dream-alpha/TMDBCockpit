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
from Plugins.Plugin import PluginDescriptor
from .__init__ import _
from .Debug import logger
from .Version import VERSION
from .ConfigInit import ConfigInit
from .EpgSelection import initEPGSelection
from .ScreenMain import ScreenMain
from .ScreenTMDB import ScreenTMDB
from .SkinUtils import loadPluginSkin


WHERE_TMDB_INFOS = -98


def eventinfo(session, **__):
	service = session.nav.getCurrentService()
	info = service.info()
	event = info.getEvent(0)  # 0 = now, 1 = next
	event_name = event and event.getEventName() or info.getName() or ""
	session.open(ScreenMain, event_name, 2)


def queryInfos(search, callback, **__):
	ScreenTMDB(search, callback)


def movieList(session, service, **__):
	logger.info("...")
	session.open(ScreenMain, service, 1)


def main(session, **__):
	session.open(ScreenMain, "", 3)


def autoStart(reason, **kwargs):
	if reason == 0:  # startup
		if "session" in kwargs:
			logger.info("+++ Version: %s starts...", VERSION)
			# session = kwargs["session"]
			if config.plugins.tmdb.key_yellow.value:
				initEPGSelection()
			loadPluginSkin("skin.xml")
	elif reason == 1:  # shutdown
		logger.info("--- shutdown")
	else:
		logger.info("reason not handled: %s", reason)


def Plugins(**__):
	logger.info("+++ Plugins")
	ConfigInit()

	descriptors = [
		PluginDescriptor(
			where=[
				PluginDescriptor.WHERE_AUTOSTART,
				PluginDescriptor.WHERE_SESSIONSTART,
			],
			fnc=autoStart
		),
		PluginDescriptor(
			name="TMDB",
			description=_("TMDB Infos ..."),
			where=[
				PluginDescriptor.WHERE_MOVIELIST,
			],
			fnc=movieList
		),
		PluginDescriptor(
			name="TMDB",
			description=_("TMDB Infos ..."),
			where=[
				WHERE_TMDB_INFOS,
			],
			fnc=queryInfos
		),
		PluginDescriptor(
			name="TMDB",
			description=_("TMDB Infos ..."),
			where=[
				PluginDescriptor.WHERE_EVENTINFO,
			],
			fnc=eventinfo
		),
		PluginDescriptor(
			name=_("TMDBCockpit"),
			where=[
				PluginDescriptor.WHERE_PLUGINMENU,
			],
			icon="TMDBCockpit.png",
			description=_("Access TMDB movie infos"),
			fnc=main
		)
	]
	return descriptors
