# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic
import json
import time
import PixivUtil
import systray_rc
import cache
import MessageBubble

InputUI, QtBaseClass = uic.loadUiType("MessageInput.ui")

class MessageInput(QtGui.QWidget, InputUI):
	def __init__(self, parent = None):
		super(MessageInput, self).__init__(parent)
		self.setupUi(self)
		self.gLayout = QtGui.QGridLayout(self.sclContents)
		self.gLayout.setGeometry(QtCore.QRect(0, 0, 
			self.sclContents.geometry().width(), self.sclContents.geometry().height()))
		self.gLayout.setSpacing(12)
		self.gLayout.setAlignment(QtCore.Qt.AlignBottom)
	
	def updateMessage(self, msg):
		bbl = []
		if msg['self_send']:
			bbl = MessageBubble.RightBubble(self)
		else:
			bbl = MessageBubble.LeftBubble(self)
		if msg['type'] == 'text':
			bbl.setContent(msg['content'])
		else:
			pass
		self.gLayout.addWidget(bbl)

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	w = MessageInput()
	w.show()
	for x in range(1, 5):
		w.updateMessage({
			'self_send': False
		})
		w.updateMessage({
			'self_send': True
		})
	sys.exit(app.exec_())