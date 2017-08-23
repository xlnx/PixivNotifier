# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore, uic
import Block
import PixivSync

IllBxUI, QtBaseClass = uic.loadUiType("IllustBox.ui")

class IllustBox(QtGui.QWidget, IllBxUI):
	def __init__(self, parent = None):
		super(IllustBox, self).__init__(parent)
		self.setupUi(self)

		self.sclArea.verticalScrollBar().valueChanged.connect(self.checkBottom)

		self.blkList = []
		self.lw = self.geometry().width() / 2 - 10
		self.hLayout = QtGui.QGridLayout(self.sclContent)
		self.hLayout.setGeometry(QtCore.QRect(0, 0, 300, 300))
		self.hLayout.setSpacing(0)
		self.hLayout.setAlignment(QtCore.Qt.AlignTop)
		self.vcol = [QtGui.QFrame(self), QtGui.QFrame(self)]
		self.canAppend = True
		
		self.setHeight(0, 0)
		self.setHeight(1, 0)
		# self.setHeight(self.vcol[0], 400)
		# self.setHeight(self.vcol[1], 1000)
		# self.vcol[0].setStyleSheet("background: red")
		# self.vcol[1].setStyleSheet("background: black")

		self.hLayout.addWidget(self.vcol[0], 0, 0, QtCore.Qt.AlignTop)
		self.hLayout.addWidget(self.vcol[1], 0, 1, QtCore.Qt.AlignTop)

	def reset(self):
		PixivSync.sync.getRecommendedList()
		# 
		self.blkList = []
		self.canAppend = True
		self.Append()
	
	def setHeight(self, w, h):
		self.vcol[w].setMinimumSize(self.lw, h)
		self.vcol[w].setMaximumSize(self.lw, h)
	
	def checkBottom(self, pos):
		if pos == self.sclArea.verticalScrollBar().maximum():
			if self.canAppend:
				self.Append()
			# self.vcol[1].setStyleSheet("background: blue")

	def Append(self):
		if PixivSync.sync.illuThread is not None:
			self.canAppend = False
			id = 0 if self.vcol[0].geometry().height() <= self.vcol[1].geometry().height() else 1
			b = Block.Block()
			self.blkList.append(b)
			query = {
				'block': b,
				'col': id,
				'object': self
			}
			PixivSync.sync.getIllust(query)

	def endAppend(self, query, response):
		query['block'].setAttribute(title = unicode(response['illust_title']), 
			icon = QtGui.QPixmap(response['icon_filename']), 
			url = response['original-url'], data = response)
		query['block'].setGeometry(0, self.vcol[query['col']].geometry().height(),
			query['block'].geometry().width(), query['block'].geometry().height())
		self.setHeight(query['col'], self.vcol[query['col']].geometry().height() + 
			query['block'].geometry().height())
		# print response['icon_filename']
		# print query['block'].image.geometry()
		# print self.vcol[0].geometry(), self.vcol[1].geometry()
		query['block'].setParent(self.vcol[query['col']])
		query['block'].show()
		self.canAppend = True
		self.checkBottom(self.sclArea.verticalScrollBar().value())

	def erase(self, index):
		pass

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	w = IllustBox()
	w.show()
	sys.exit(app.exec_())
