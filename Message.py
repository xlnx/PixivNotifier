# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic

MsgUI, QtBaseClass = uic.loadUiType("Message.ui")

class Message(QtGui.QWidget, MsgUI):
	def __init__(self, parent = None):
		super(Message, self).__init__(parent)
		self.setupUi(self)
		self.setMinimumSize(self.geometry().width(), self.geometry().height())
		self.setMaximumSize(self.geometry().width(), self.geometry().height())

	def setAttribute(self, title = None, content = None, time = None, icon = None):
		if title is not None:
			self.title.setText(unicode(title))
		if content is not None:
			self.content.setText(unicode(content))
			self.content.setToolTip(unicode(content))
		if time is not None:
			self.time.setText(unicode(time))
		if icon is not None:
			self.image.setPixmap(QtGui.QPixmap(icon).scaled(
				QtCore.QSize(self.image.geometry().width(), self.image.geometry().height())
			))

	def setOutOfDate(self):
		self.frame.setStyleSheet("""
			QFrame#frame
			{
				background-color: rgb(218, 218, 218)
			}
			QFrame#frame:hover
			{
				background-color: rgb(221, 234, 246);
				border-color: rgb(221, 234, 246);
			}
		""")
	
if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	a = Message()
	a.show()
	a.setOutOfDate()
	sys.exit(app.exec_())