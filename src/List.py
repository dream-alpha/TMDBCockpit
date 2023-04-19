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


from Components.GUIComponent import GUIComponent
from enigma import eListboxPythonMultiContent, eListbox, RT_HALIGN_LEFT, RT_VALIGN_CENTER
from skin import parseFont


class List(GUIComponent):
	GUI_WIDGET = eListbox

	def __init__(self):
		GUIComponent.__init__(self)
		self.list = eListboxPythonMultiContent()
		self.list.setBuildFunc(self.buildList)
		self.onSelectionChanged = []

	def buildList(self, entry):
		res = [None]
		res.append(
			(
				eListboxPythonMultiContent.TYPE_TEXT,
				5,
				0,
				self.list.getItemSize().width(),
				self.list.getItemSize().height(),
				0,
				RT_HALIGN_LEFT | RT_VALIGN_CENTER,
				entry[0]
			)
		)
		return res

	def applySkin(self, desktop, parent):
		if not self.visible:
			self.instance.hide()

		if self.skinAttributes is None:
			return False

		for (attrib, value) in self.skinAttributes:
			if attrib in ["font"]:
				self.list.setFont(0, parseFont(value, ((1, 1), (1, 1))))
				self.skinAttributes.remove((attrib, value))

		GUIComponent.applySkin(self, desktop, parent)
		return True

	def getCurrent(self):
		current = self.list.getCurrentSelection()
		return current and current[0]

	def postWidgetCreate(self, instance):
		instance.setContent(self.list)
		self.instance.setWrapAround(True)
		self.selectionChanged_conn = instance.selectionChanged.connect(self.selectionChanged)

	def preWidgetRemove(self, instance):
		instance.setContent(None)
		self.selectionChanged_conn = None

	def selectionChanged(self):
		for function in self.onSelectionChanged:
			function()

	def setList(self, alist):
		self.list.setList(alist)

	def moveToIndex(self, index):
		self.instance.moveSelectionTo(index)

	def getSelectionIndex(self):
		return self.list.getCurrentSelectionIndex()

	def selectionEnabled(self, enabled):
		self.instance.setSelectionEnable(enabled)

	def pageUp(self):
		self.instance.moveSelection(self.instance.pageUp)

	def pageDown(self):
		self.instance.moveSelection(self.instance.pageDown)

	def moveUp(self):
		self.instance.moveSelection(self.instance.moveUp)

	def moveDown(self):
		self.instance.moveSelection(self.instance.moveDown)
