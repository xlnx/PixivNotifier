# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore, uic
import Message

MsgBxUI, QtBaseClass = uic.loadUiType("MessageBox.ui")

class MessageBox(QtGui.QWidget, MsgBxUI):
	def __init__(self, parent = None):
		super(MessageBox, self).__init__(parent)
		self.setupUi(self)
		# self.scrollArea = QtGui.QScrollArea(self)
		self.msgList = []
		self.gLayout = QtGui.QGridLayout(self.sclContent)
		self.gLayout.setGeometry(QtCore.QRect(0, 0, 300, 300))
		self.gLayout.setSpacing(0)
		self.gLayout.setAlignment(QtCore.Qt.AlignTop)

	def push_back(self, unread = True, **kwargs):
		msg = Message.Message(self)
		self.msgList.append(msg)
		msg.setAttribute(**kwargs)
		self.gLayout.addWidget(msg)
		if not unread:
			pass
			# msg.setOutOfDate()
		# msg.show()
		return msg

	def erase(self, index):
		pass

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	ex = MessageBox()
	ex.show()
	ex.push_back("asd", "asdasd", "12")
	for i in range(0, 10):
		ex.push_back("1", "2", "333")
	sys.exit(app.exec_())
