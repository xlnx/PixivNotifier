# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic
import json
import time
import PixivUtil
import systray_rc
import cache

lBubbleUI, QtBaseClass = uic.loadUiType("LeftBubble.ui")
rBubbleUI, QtBaseClass1 = uic.loadUiType("RightBubble.ui")

class BubbleBase(QtGui.QWidget):
	def __init__(self, parent = None):
		super(BubbleBase, self).__init__(parent)

	def setContent(self, str):
		len = self.text.fontMetrics().width(str)
		fheight = self.text.fontMetrics().lineSpacing()
		lcount = 1 + len / self.text.geometry().width()
		self.resizeBubble(len, lcount, fheight)
		self.setGeometry(self.geometry().x(), self.geometry().y(),
			self.geometry().width(), self.textFrame.geometry().height())
		self.setMinimumSize(self.geometry().width(), self.geometry().height())
		self.setMaximumSize(self.geometry().width(), self.geometry().height())
		self.text.document().setPlainText(str)

class LeftBubble(BubbleBase, lBubbleUI):
	def __init__(self, parent = None):
		super(LeftBubble, self).__init__(parent)
		self.setupUi(self)
		self.setMinimumSize(self.geometry().width(), self.geometry().height())
	
	def resizeBubble(self, len, lcount, fheight):
		if lcount == 1:
			self.textFrame.setGeometry(self.textFrame.geometry().x(), self.textFrame.geometry().y(),
				self.textFrame.geometry().width() - (self.text.geometry().width() - len), self.textFrame.geometry().height())
		else:
			self.textFrame.setGeometry(self.textFrame.geometry().x(), self.textFrame.geometry().y(), 
				self.textFrame.geometry().width(), self.textFrame.geometry().height() + fheight * (lcount - 1))
		self.text.setGeometry(self.text.geometry().x(), self.text.geometry().y(), 
			self.text.geometry().width(), self.text.geometry().height() + fheight * (lcount - 1))

class RightBubble(BubbleBase, rBubbleUI):
	def __init__(self, parent = None):
		super(RightBubble, self).__init__(parent)
		self.setupUi(self)
		self.setMinimumSize(self.geometry().width(), self.geometry().height())
		self.setMaximumSize(self.geometry().width(), self.geometry().height())
	
	def resizeBubble(self, len, lcount, fheight):
		if lcount == 1:
			self.textFrame.setGeometry(self.textFrame.geometry().x() + (self.text.geometry().width() - len), self.geometry().y(),
				self.textFrame.geometry().width() - (self.text.geometry().width() - len), self.textFrame.geometry().height())
		else:
			self.textFrame.setGeometry(self.textFrame.geometry().x(), self.textFrame.geometry().y(), 
				self.textFrame.geometry().width(), self.textFrame.geometry().height() + fheight * (lcount - 1))
		if lcount == 1:
			self.text.setGeometry(self.text.geometry().x(), self.text.geometry().y(), 
				self.text.geometry().width() - (self.text.geometry().width() - len), self.text.geometry().height() + fheight * (lcount - 1))	
		else:
			self.text.setGeometry(self.text.geometry().x(), self.text.geometry().y(), 
				self.text.geometry().width(), self.text.geometry().height() + fheight * (lcount - 1))

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	a = LeftBubble()
	b = RightBubble()
	a.show()
	b.show()
	sys.exit(app.exec_())