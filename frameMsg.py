# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic
import json
import time

frameMsgUI, QtBaseClass = uic.loadUiType("frameMsg.ui")

class MessageFrame(QtGui.QFrame, frameMsgUI):
	def __init__(self, parent = None):
		QtGui.QFrame.__init__(self, parent)
		frameMsgUI.__init__(self, parent)
		self.setupUi(self)

	def setAttribute(self, title = None, content = None, time = None, icon = None):
		if title != None:
			self.lblTitle.setText(str(title))
		if content != None:
			self.lblContent.setText(str(content))
		if time != None:
			self.lblTime.setText(str(time))
	