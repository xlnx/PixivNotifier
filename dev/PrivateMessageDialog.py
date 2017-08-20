# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic
import json
import time
import PixivUtil
import systray_rc
import cache
import PrivateMessage

DialogUI, QtBaseClass = uic.loadUiType("PrivateMessageDialog.ui")

class PrivateMessageDialog(QtGui.QDialog, DialogUI):
	def __init__(self):
		super(PrivateMessageDialog, self).__init__()
		self.setupUi(self)
		self.setWindowFlags(QtCore.Qt.WindowTitleHint) 
		self.setFixedSize(self.width(), self.height())
		self.userMap = {}
		self.gLayout = QtGui.QGridLayout(self.sclContents)
		self.gLayout.setGeometry(QtCore.QRect(0, 0, 
			self.sclContents.geometry().width(), self.sclContents.geometry().height()))
		self.gLayout.setSpacing(0)
		self.gLayout.setAlignment(QtCore.Qt.AlignTop)

	def addUser(self, user, user_id, icon):
		if user_id in self.userMap:
			return False
		x = PrivateMessage.PrivateMessage(user, icon, self)
		self.gLayout.addWidget(x)
		self.userMap[user_id] = x
		return True

	def dispatchMsg(self, msg):
		if msg['user_id'] not in self.userMap:
			return False
		self.userMap[msg['user_id']].updateMessage(msg)
		return True

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = PrivateMessageDialog()
	window.show()
	for x in range(0, 1):
		window.addUser(user = "asdasdasd", user_id = x, icon = QtGui.QPixmap())
		s = u'我'
		for y in range(0, 500):
			s = s + u'i'
			window.dispatchMsg({
				'self_send': False,
				'user_id': x, 
				'type': 'text',
				'content': s,
				'time': "2:30"
			})
		window.dispatchMsg({
			'self_send': True,
			'user_id': x, 
			'type': 'text',
			'content': "qweqweqwe",
			'time': "2:30"
		})
		# a.updateMessage("asdasd", "1:20")
		# time.sleep(1)
		# b.updateMessage("saw", "2:30")
		# time.sleep(1)
	sys.exit(app.exec_())