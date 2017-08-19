# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic

class Widget(QtGui.QWidget):
	def __init__(self, parent = None):
		super(Widget, self).__init__(parent)

	def sizeHint(self):
		return QtCore.QSize(self.geometry().width(), self.geometry().height())