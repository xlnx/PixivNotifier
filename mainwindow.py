# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic
import json
import time
import pixiv
import systray_rc
import thread
# import threading

window = []

WindowUI, QtBaseClass = uic.loadUiType("mainwindow.ui")

class Window(QtGui.QMainWindow, WindowUI):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		WindowUI.__init__(self)
		self.setupUi(self)

		#设置一个iconComboBox
		self.iconComboBox = QtGui.QComboBox()
		self.iconComboBox.addItem(
			QtGui.QIcon('favicon.ico'), "Dmyz")
#-------------------通知区域图标右键菜单start------------------
		self.minimizeAction = QtGui.QAction(u"最小化", self,
				triggered=self.hide)
		self.restoreAction = QtGui.QAction(u"&amp;显示窗口", self,
				triggered=self.showNormal)
		self.quitAction = QtGui.QAction(u"&amp;退出", self,
				triggered=QtGui.qApp.quit)
		#弹出的菜单的行为，包括退出，还原，最小化
		self.trayIconMenu = QtGui.QMenu(self)
		self.trayIconMenu.addAction(self.restoreAction)
		self.trayIconMenu.addAction(self.minimizeAction)
		self.trayIconMenu.addAction(self.quitAction)
		self.trayIcon = QtGui.QSystemTrayIcon(self)
		self.trayIcon.setContextMenu(self.trayIconMenu)
#-------------------通知区域图标右键菜单end------------------
		#设置通知区域的ICON
		self.iconComboBox.currentIndexChanged.connect(
			self.setIcon)

		#通知区域icon显示
		self.iconComboBox.setCurrentIndex(1)
		self.trayIcon.show()
		self.trayIcon.activated.connect(
			self.iconActivated)
		self.setWindowFlags(QtCore.Qt.WindowTitleHint) 
		self.setFixedSize(self.width(), self.height())

		self.btnLogin.clicked.connect(self.loginProc)

	def iconActivated(self, reason):
		if reason in (QtGui.QSystemTrayIcon.Trigger,
					  QtGui.QSystemTrayIcon.DoubleClick):
			self.showNormal()
		elif reason == QtGui.QSystemTrayIcon.MiddleClick:
			self.showMessage()

	def setIcon(self, index):
		icon = self.iconComboBox.itemIcon(0)
		self.trayIcon.setIcon(icon)
		self.setWindowIcon(icon)
		self.trayIcon.setToolTip(
			self.iconComboBox.itemText(index))

	def showMessage(self, title, msg, icon = QtGui.QSystemTrayIcon.MessageIcon()):
		self.trayIcon.showMessage(title, msg, icon, 1500)

	def loginProc(self):
		pixiv.login(str(self.lePixivID.text()), str(self.lePassword.text()))
		# self.showMessage(u'PixivNotifier', u'ログインして完成する')
		self.hide()
		thread.start_new_thread(check_message, {60 * 1})

def check_message(interval):
	while (True):
		msg = pixiv.check_msg()
		if msg != None:
			handle_msg(msg)
		time.sleep(interval)

def nice(id, user_id, time, details):
	window.showMessage(u'赞！', u'「' + 
		details['target']['title'] + 
		u'」已收到' + str(details['count']) + u'个赞！')

def bookmarked(id, user_id, time, details):
	window.showMessage(u'收藏', u'已有' + str(details['content']['bookmark_count']) + 
		u'人收藏了「' + details['target']['title'] + u'」~')

def handle_msg(msg):
	data = json.loads(msg)
	for x in data['items']:
		if x['unread']:
			handle_result = {
				'nice': nice,
				'bookmarked': bookmarked
			}[x['type']](id = x['id'], user_id = x['user_id'], 
				time = x['notified_at'], details = x['details'])
	if data['remaining_unread_count'] > 0:
		window.showMessage(u'未读消息', u'还有' + str(data['remaining_unread_count']) + u'条...')

def test():
	src = '{"items":[{"id":24326867,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 12:07:23 +0900","type":"nice","unread":true,"details":{"target":{"id":64422822,"type":"illust","title":"Heartbroken Koishi","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/15/04/09/26/64422822_p0_square1200.jpg"},"count":9}},{"id":317000650,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 12:07:23 +0900","type":"bookmarked","unread":true,"details":{"target":{"id":64422822,"type":"illust","title":"Heartbroken Koishi","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/15/04/09/26/64422822_p0_square1200.jpg"},"count":8,"content":{"bookmark_count":8}}},{"id":317490967,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 10:40:34 +0900","type":"bookmarked","unread":true,"details":{"target":{"id":64461432,"type":"illust","title":"Subterranean Rose","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/17/02/58/16/64461432_p0_square1200.jpg"},"count":1,"content":{"bookmark_count":1}}},{"id":24778695,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 10:40:34 +0900","type":"nice","unread":true,"details":{"target":{"id":64461432,"type":"illust","title":"Subterranean Rose","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/17/02/58/16/64461432_p0_square1200.jpg"},"count":2}},{"id":317393171,"user_id":10949667,"notified_at":"Wed, 16 Aug 2017 23:33:27 +0900","type":"bookmarked","unread":false,"details":{"target":{"id":64157922,"type":"illust","title":"こいし~","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/01/01/25/26/64157922_p0_square1200.jpg"},"count":6,"content":{"bookmark_count":6}}}],"remaining_unread_count":0}'
	handle_msg(src)

if __name__ == '__main__':

	import sys
	app = QtGui.QApplication(sys.argv)
	QtGui.QApplication.setQuitOnLastWindowClosed(False)

	window = Window()
	if True:
		window.show()

	sys.exit(app.exec_())