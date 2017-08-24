# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic
import PixivUtil
import threading
import cache

BlkUI, QtBaseClass = uic.loadUiType("Block.ui")

class Block(QtGui.QWidget, BlkUI):
	def __init__(self, parent = None):
		super(Block, self).__init__(parent)
		self.setupUi(self)
		self.connect(self, QtCore.SIGNAL('get-box-illust'), self.endFetchImg)
		self.url = None
		self.w = None
		self.icon = None
		self.original = None

	def setAttribute(self, title = None, icon = None, url = None, data = None):
		if title is not None:
			self.title.setText(unicode(title))
		det = u''
		if data is not None:
			# print data
			self.data = data
			# if star is not None:
				# det += u'☆' + unicode(star)
			# if post is not None:
				# self.post.setText(unicode(post))
		self.details.setText(det)
		if url is not None:
			self.url = url
		if icon is not None:
			self.icon = icon
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
			self.tag.setGeometry(0, self.geometry().height() - self.tag.geometry().height(),
				self.tag.geometry().width(), self.tag.geometry().height())
	
	def mousePressEvent(self, e):
		if self.url is not None:
			if self.w is None:
				self.w = QtGui.QLabel()
				self.w.setGeometry(100, 100, 100, 100)
				self.beginFetchImg()
			self.w.show()

	def beginFetchImg(self):
		self.thread = MyIllustThread(self)
		self.thread.start()

	def endFetchImg(self, img_name):
		self.original = QtGui.QPixmap(img_name)
		self.w.setPixmap(self.original)
		self.w.setGeometry(self.w.geometry().x(), self.w.geometry().y(), 
			self.original.width(), self.original.height())

class MyIllustThread(threading.Thread):
	def __init__(self, object):
		super(MyIllustThread, self).__init__()
		self.object = object

	def run(self):
		self.object.emit(QtCore.SIGNAL('get-box-illust'), cache.image.get(self.object.url, 
			headers = PixivUtil.create_header(PixivUtil.pixiv.return_to)))

if __name__ == "__main__":
	import os
	print os.path.abspath(os.path.dirname(__file__)+os.path.sep) 