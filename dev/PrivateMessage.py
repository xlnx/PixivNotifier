# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic
import json
import time
import PixivUtil
import systray_rc
import cache
import MessageInput

MsgUI, QtBaseClass = uic.loadUiType("PrivateMessage.ui")

activeMessage = None

class PrivateMessage(QtGui.QWidget, MsgUI):
	def __init__(self, user, icon, parent = None):
		super(PrivateMessage, self).__init__(parent)
		self.setupUi(self)

		self.messageInput = MessageInput.MessageInput(parent)
		self.messageInput.setGeometry(220, 0,
			self.messageInput.geometry().width(), self.messageInput.geometry().height())
		self.setMinimumSize(self.geometry().width(), self.geometry().height())
		self.setMaximumSize(self.geometry().width(), self.geometry().height())
		self.title.setText(user)
		self.image.setPixmap(icon)
		self.lblCount.setStyleSheet("""
			color: rgb(255, 255, 255);
		""")
		self.notify.setStyleSheet("""
			border-radius: 8px;
			background: transparent;
		""")
		self.active = False
		self.unreadCount = 0

	def mousePressEvent(self, e):
		self.setFocus()

	def updateMessage(self, msg):
		self.content.setText(getAbstract(msg))
		self.time.setText(getTime(msg))
		if not self.active:
			self.unreadCount += 1
			self.lblCount.setText(str(self.unreadCount))
			self.notify.setStyleSheet("""
				border-radius: 8px;
				background-color: rgb(226, 0, 0);
			""")
		self.messageInput.updateMessage(msg)

	def setFocus(self):
		global activeMessage
		self.messageInput.show()
		if activeMessage != None:
			activeMessage.LoseFocus()
		activeMessage = self
		self.active = True
		self.unreadCount = 0
		self.lblCount.setText("")
		self.notify.setStyleSheet("""
			border-radius: 8px;
			background: transparent;
		""")
		self.frame.setStyleSheet("""
			background-color: rgb(70, 135, 195);
			border-color: rgb(70, 135, 195);
		""")
	
	def LoseFocus(self):
		self.active = False
		self.messageInput.hide()
		self.frame.setStyleSheet("""
			QFrame#frame
			{
				background-color: rgb(81, 158, 225);
				border-color: rgb(81, 158, 225);
			}
			QFrame#frame:hover
			{
				background-color: rgb(76, 148, 211);
				border-color: rgb(76, 148, 211);
			}
		""")

def getTime(msg):
	if True:
		return msg['time']

def getAbstract(msg):
	if msg['type'] == 'text':
		return msg['content']
	else:
		return 'unknown type'

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	a = PrivateMessage("shit", QtGui.QPixmap())
	a.show()
	b = PrivateMessage("fuck", QtGui.QPixmap())
	b.show()
	for x in range(1, 100):
		a.updateMessage({
			'type': 'text',
			'content': 'asdasd',
			'time': '1:20'
		})
		# time.sleep(1)
		b.updateMessage({
			'type': 'image',
			'content': 'saw',
			'time': '1:20'
		})
		# time.sleep(1)
	sys.exit(app.exec_())