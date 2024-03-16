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

import os
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from .__init__ import _
from .Debug import logger
from .Utils import temp_dir
from .FileUtils import copyFile, writeFile


class MoreOptions():
	def __init__(self, session, service_path):
		logger.debug("service_path: %s", service_path)
		self.session = session
		self.service_path = service_path
		self.ident = None

	def menu(self, ident, overview):
		logger.info("ident: %s", ident)
		self.ident = ident
		self.overview = overview
		if self.service_path:
			options = [
				(_("Save movie description"), 1),
				(_("Save movie cover"), 2),
				(_("Save movie backdrop"), 3),
				(_("Save movie backdrop as cover"), 4),
				("1+2", 5),
				("1+2+3", 6),
				("2+3", 7)
			]
			self.session.openWithCallback(
				self.menuCallback,
				ChoiceBox,
				windowTitle=_("TMDB cover/backdrop"),
				title=_("Please select a function"),
				list=options
			)

	def menuCallback(self, ret):
		if ret is not None:
			msg = ""
			option = ret[1]
			ident = str(self.ident)
			service_filename = os.path.splitext(self.service_path)[0]
			logger.debug("service_filename: %s", service_filename)
			msg += "\n" if msg else ""
			if option in [2, 5, 7]:
				cover = temp_dir + "cover" + ident + ".jpg"
				if os.path.isfile(cover):
					copyFile(cover, service_filename + ".jpg")
					msg += _("Cover saved.")
					self.files_saved = True
					logger.debug("Cover %s.jpg created", service_filename)
				else:
					msg += _("No cover available")

			if option in [3, 4, 6, 7]:
				backdrop = temp_dir + "backdrop" + ident + ".jpg"
				ext = ".jpg" if option == 4 else ".bdp.jpg"
				msg += "\n" if msg else ""
				if os.path.isfile(backdrop):
					copyFile(backdrop, service_filename + ext)
					msg += _("Backdrop saved.")
					self.files_saved = True
					logger.debug("Backdrop %s%s created", service_filename, ext)
				else:
					msg += _("No backdrop available")

			if option in [1, 5, 6]:
				text_file = service_filename + ".txt"
				msg += "\n" if msg else ""
				if self.overview:
					writeFile(text_file, self.overview)
					logger.debug("%s created", text_file)
					msg += _("Movie description saved.")
					self.files_saved = True
				else:
					msg += _("No movie description available")

			self.session.open(MessageBox, msg, type=MessageBox.TYPE_INFO)
