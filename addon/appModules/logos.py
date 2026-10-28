# NVDA add-on for Logos Bible Study
# Copyright 2025 Leonard de Ruijter <alderuijter@gmail.com>
# License: GNU General Public License version 2.0

import re

import appModuleHandler
import controlTypes
import textInfos
import UIAHandler
from NVDAObjects.UIA import UIA

_brokenNameregex = re.compile(r"^\w+\.\w+\.\w+")
_ensureLabelRoles = {controlTypes.ROLE_BUTTON, controlTypes.ROLE_TOGGLEBUTTON, controlTypes.ROLE_EDITABLETEXT}


class BrokenNameElement(UIA):
	name: str

	def _get_name(self):
		if desc := self.description:
			self.description = None
			return desc
		return self._recursiveName or self.UIAAutomationId

	def _get__recursiveName(self) -> str | None:
		cachedChildren = self._get_UIAChildren()
		if not cachedChildren:
			return None
		names = []
		for index in range(cachedChildren.length):
			elem = cachedChildren.getElement(index)
			if elem.CachedControlType != UIAHandler.UIA.UIA_TextControlTypeId:
				continue
			names.append(elem.cachedName)
		return " ".join(names)


class BrokenDocumentTextInfo(textInfos.offsets.OffsetsTextInfo):
	locationText = None
	encoding = None

	def _get_unit_mouseChunk(self):
		return textInfos.UNIT_STORY

	def _getStoryText(self):
		return self.obj.UIAValue

	def _getStoryLength(self):
		return len(self._getStoryText())

	def _get_boundingRects(self):
		return [self.obj.location]

	def _getCaretOffset(self):
		text = self._getStoryText()
		if text.startswith(("\r\n") * 4):
			return 0
		totalLength = len(text)
		strippedLength = len(text.lstrip("\r\n"))
		return totalLength - strippedLength


class BrokenDocument(UIA):
	TextInfo = BrokenDocumentTextInfo
	# value = None

	def turnPage(self, previous=False):
		obj = self.next.next.next
		if not previous:
			obj = obj.next
		obj.doAction()


class AppModule(appModuleHandler.AppModule):
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if not isinstance(obj, UIA):
			return
		if (not obj.name and obj.role in _ensureLabelRoles) or _brokenNameregex.match(obj.name):
			clsList.insert(0, BrokenNameElement)
		UIAClassName = obj.UIAElement.cachedClassName
		if UIAClassName == "Document" and not obj.UIATextPattern:
			clsList.insert(0, BrokenDocument)
