# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic

BlkUI, QtBaseClass = uic.loadUiType("Block.ui")

class Block(QtGui.QWidget, BlkUI):
	def __init__(self, parent = None):
		super(Block, self).__init__(parent)
		self.setupUi(self)
		self.url = None

	def setAttribute(self, title = None, icon = None, url = None, data = None):
		# if title is not None:
			# self.title.setText(unicode(title))
		if url is not None:
			self.url = url
		if data is not None:
			self.data = data
		if icon is not None:
			img = icon.scaled(
				QtCore.QSize(self.image.geometry().width(), 65536),
				QtCore.Qt.KeepAspectRatio,
				QtCore.Qt.SmoothTransformation
			)
			self.setMinimumSize(img.width(), img.height())
			self.setMaximumSize(img.width(), img.height())
			self.frame.setMinimumSize(img.width(), img.height())
			self.frame.setMaximumSize(img.width(), img.height())
			self.image.setMinimumSize(img.width(), img.height())
			self.image.setMaximumSize(img.width(), img.height())
			self.image.setPixmap(img)
	
	def mousePressEvent(self, e):
		if self.url is not None:
			self.w = QtGui.QLabel()
			
			self.show()

if __name__ == "__main__":
	import os
	print os.path.abspath(os.path.dirname(__file__)+os.path.sep) 