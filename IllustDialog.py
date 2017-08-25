# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic
import PixivUtil
import threading
import cache
import PixivNotifier
from bs4 import BeautifulSoup
import requests

DlgUI, QtBaseClass = uic.loadUiType("IllustDialog.ui")
bookmarkUrl = 'https://www.pixiv.net/bookmark_add.php?type=illust&amp;illust_id='

class MyView(QtGui.QGraphicsView):
	def __init__(self, parent = None):
		super(MyView, self).__init__(parent)
		self.setStyleSheet(qss)
		self.setFrameShape(QtGui.QFrame.NoFrame)
		self.factor = 1.0
	
	def wheelEvent(self, e):
		if e.delta() < 0:
			self.factor /= 1.2
			self.scale(1.2 / 1.0, 1.2 / 1.0)
		else:
			self.factor *= 1.2
			self.scale(1.0 / 1.2, 1.0 / 1.2)

	def mouseDoubleClickEvent(self, e):
		self.scale(self.factor, self.factor)
		self.factor = 1.0

class IllustDialog(QtGui.QMainWindow, DlgUI):
	def __init__(self, title, id, url, bookmark, parent = None):
		super(IllustDialog, self).__init__(parent)
		self.setupUi(self)
		self.setWindowTitle(title)
		self.id = str(id)
		self.url = str(url)
		self.bookmarked = bookmark
		self.bookmark.clicked.connect(self.addBookmark)
		self.image = MyView(self)
		self.image.setGeometry(0, 0, 500, 500)
		self.refreshBookmarkState()

	def setImage(self, img):
		scene = QtGui.QGraphicsScene()
		scene.addPixmap(img)
		self.image.setScene(scene)
		self.image.scale(1.0, 1.0)

	def resizeEvent(self, e):
		self.control.setGeometry(0, e.size().height() - self.control.geometry().height(), 
			e.size().width(), self.control.geometry().height())
		self.image.setGeometry(0, 0, e.size().width(), 
			e.size().height() - self.control.geometry().height())

	def addBookmark(self):
		if not self.bookmarked:
			pageHtml = PixivUtil.get(PixivUtil.pixiv.getServer(), 
				bookmarkUrl + self.id, headers = PixivUtil.create_header(self.url)).text
			page = BeautifulSoup(pageHtml, 'lxml')
			token = str(page.find('input', attrs = {'name': 'tt'})['value'])
			form = {
				'mode': 'add',
				'tt': token, 
				'id': self.id,
				'type': 'illust',
				'from_sid': '',
				'comment': '',
				'tag': '',
				'restrict': '0'
			}
		else:
			pass
		PixivUtil.post(PixivUtil.pixiv.getServer(), 
			bookmarkUrl + self.id, headers = PixivUtil.create_header(self.url),
			data = form
		)
		self.bookmarked = not self.bookmarked
		self.refreshBookmarkState()

	def refreshBookmarkState(self):
		self.bookmark.setText(u'☆' if not self.bookmarked else u'★')
		
qss = """
QGraphicsView
{
	background: transparent;
}

QScrollBar:vertical
{
    width:12px;
    background:rgba(0,0,0,0%);
    margin:0px,0px,0px,0px;
    padding-top:13px;
    padding-bottom:13px;
}
QScrollBar::handle:vertical
{
    width:12px;
    background:rgba(0,0,0,25%);
    border-radius:6px;
    min-height:20;
}
QScrollBar::handle:vertical:hover
{
    width:12px;
    background:rgba(0,0,0,50%); 
    border-radius:6px;
    min-height:20;
}
QScrollBar::add-line:vertical  
{
    height:13px;width:12px;
    border-image:url(:/images/a/3.png);
    subcontrol-position:bottom;
}
QScrollBar::sub-line:vertical 
{
    height:13px;width:12px;
    border-image:url(:/images/a/1.png);
    subcontrol-position:top;
}
QScrollBar::add-line:vertical:hover  
{
    height:13px;width:12px;
    border-image:url(:/images/a/4.png);
    subcontrol-position:bottom;
}
QScrollBar::sub-line:vertical:hover 
{
    height:13px;width:12px;
    border-image:url(:/images/a/2.png);
    subcontrol-position:top;
}
QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical   
{
    background:rgba(0,0,0,10%);
    border-radius:6px;
}

QScrollBar:horizontal
{
    height:12px;
    background:rgba(0,0,0,0%);
    margin:0px,0px,0px,0px;
    padding-left:13px;
    padding-right:13px;
}
QScrollBar::handle:horizontal
{
    height:12px;
    background:rgba(0,0,0,25%);
    border-radius:6px;
    min-width:20;
}
QScrollBar::handle:horizontal:hover
{
    height:12px;
    background:rgba(0,0,0,50%); 
    border-radius:6px;
    min-width:20;
}
QScrollBar::add-line:horizontal
{
    height:12px;width:13px;
    border-image:url(:/images/a/3.png);
    subcontrol-position:right;
}
QScrollBar::sub-line:horizontal 
{
    height:12px;width:13px;
    border-image:url(:/images/a/1.png);
    subcontrol-position:left;
}
QScrollBar::add-line:horizontal:hover  
{
    height:12px;width:13px;
    border-image:url(:/images/a/4.png);
    subcontrol-position:right;
}
QScrollBar::sub-line:horizontal:hover 
{
    height:12px;width:13px;
    border-image:url(:/images/a/2.png);
    subcontrol-position:left;
}
QScrollBar::add-page:horizontal,QScrollBar::sub-page:horizontal
{
    background:rgba(0,0,0,10%);
    border-radius:6px;
}
"""

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	w = IllustDialog()
	w.show()
	sys.exit(app.exec_())