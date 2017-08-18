# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic
import json
import time
import frameMsg

frameMsgListUI, QtBaseClass = uic.loadUiType("frameMsgList.ui")

class MessageList(QtGui.QFrame, frameMsgListUI):
	def __init__(self, parent = None):
		QtGui.QFrame.__init__(self, parent)
		frameMsgListUI.__init__(self, parent)
		self.setupUi(self)
		self.msgList = []

	def push_back(self, title = None, content = None, time = None, icon = None):
		msg = frameMsg.MessageFrame(self)
		height = msg.geometry().height()
		msg.setGeometry(
			0, len(self.msgList) * height,
			msg.geometry().width(), msg.geometry().height()
		)
		msg.setAttribute(title = title, content = content, time = time, icon = icon)
		msg.show()
		self.msgList.append(msg)

	def erase(self, index):
		self.msgList[index].hide()
		height = self.msgList[index].geometry().height()
		del self.msgList[index]
		for i in range(index, len(self.msgList)):
			self.msgList[i].setGeometry(
				self.msgList[i].geometry().x(),
				self.msgList[i].geometry().y() - height,
				self.msgList[i].geometry().width(),
				self.msgList[i].geometry().height()
			)