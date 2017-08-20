# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic
import json
import time
import PixivUtil
import systray_rc
import cache
import MessageBox

window = None

import PixivSync
# import threading

WindowUI, QtBaseClass = uic.loadUiType("PixivNotifier.ui")

class Window(QtGui.QMainWindow, WindowUI):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		WindowUI.__init__(self)
		self.setupUi(self)

		# set window attribute
		self.setWindowFlags(QtCore.Qt.WindowTitleHint) 
		self.messageLookup = {}

		# messageBox 
		self.messageBox = MessageBox.MessageBox(self.tbCreator)

		# loginThread update UI using following signals
		self.loginThread = None
		self.connect(self, QtCore.SIGNAL("login-success"), self.login_success)
		self.connect(self, QtCore.SIGNAL("login-fail"), self.login_fail)
		self.connect(self, QtCore.SIGNAL("receive-msg"), self.dispatchMsg)
		self.connect(self, QtCore.SIGNAL("set-user-avatar"), self.set_user_avatar)
		self.connect(self, QtCore.SIGNAL("set-user-name"), self.set_user_name)
		self.btnLogin.clicked.connect(PixivSync.sync.login)

		#设置一个iconComboBox
		self.iconComboBox = QtGui.QComboBox()
		self.iconComboBox.addItem(
			QtGui.QIcon('favicon.ico'), "Dmyz")
#-------------------通知区域图标右键菜单start------------------
		self.minimizeAction = QtGui.QAction(u"最小化", self,
				triggered=self.hide)
		self.restoreAction = QtGui.QAction(u"显示窗口", self,
				triggered=self.showNormal)
		self.quitAction = QtGui.QAction(u"退出", self,
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
		self.setFixedSize(self.width(), self.height())

		# need login when form create
		self.setLoginMode(True)

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

	def setLoginMode(self, login = True):
		if login:
			self.pnlLogin.show()
			self.pnlMain.hide()
		else:
			self.pnlMain.show()
			self.pnlLogin.hide()

	def login_success(self):
		# self.showMessage(u'PixivNotifier', u'ログインして完成する')
		# self.hide()
		self.setLoginMode(False)
		PixivSync.sync.fetchUserData()
		PixivSync.sync.beginCheckMsg()
		cache.config.write({
			'pixiv_id': self.pixiv_id,
			'password': self.password
		})

	def login_fail(self, result):
		self.showMessage(u'登录失败', result[1])

	def dispatchMsg(self, msg):
		data = json.loads(msg)
		for x in data['items']:
			unread = x['unread']
			x[unread] = False
			if str(x) not in self.messageLookup:
				self.messageLookup[str(x)] = True
				details = x['details']
				f = {
					'nice': lambda: (u'赞！', u'「' + details['target']['title'] + 
								u'」已收到' + str(details['count']) + u'个赞！', 
								cache.image.get(details['target']['url'])),
					'bookmarked': lambda: (u'收藏', u'已有' + str(details['content']['bookmark_count']) + 
								u'人收藏了「' + details['target']['title'] + u'」~',
								cache.image.get(details['target']['url'])),
					'commented': lambda: (u'评论', u'「' + details['target']['title'] + u'」收到了第' +
								str(details['content']['comment_count']) + u'条评论！',
								cache.image.get(details['target']['url'])),
					'favorited': lambda: (u'新粉丝', 
								(reduce(lambda x, y: str(x['name']) + u', ' + str(y['name']), details['users'])
								if len(details['users']) > 1 else str(details['users'][0]['name']))  + u'关注了你！',
								cache.image.get(details['users'][0]['url'], headers = PixivUtil.create_header(
									PixivUtil.pixiv.return_to
								)))
				}[x['type']]
				if f is None:
					raise Exception("unknown message type: " + x['type'] + " with: " + x)
				m = f()
				if unread:
					self.showMessage(m[0], m[1])
				self.messageBox.push_back(
					title = m[0].encode('gbk'), 
					content = m[1].encode('gbk'), 
					time = str(x['notified_at']),
					icon = m[2],
					unread = unread
				)
		if data['remaining_unread_count'] > 0:
			self.showMessage(u'未读消息', u'还有' + str(data['remaining_unread_count']) + u'条...')
	
	def set_round_img(self, lbl, img):
		w = lbl.geometry().width()
		h = lbl.geometry().height()
		size = QtCore.QSize(w, h)
		img = img.scaled(size)
		mask = QtGui.QBitmap(size)
		painter = QtGui.QPainter(mask)
		painter.setRenderHint(QtGui.QPainter.Antialiasing)
		painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
		painter.fillRect(0, 0, w, h, QtCore.Qt.white)
		painter.setBrush(QtGui.QColor(0, 0, 0))
		painter.drawRoundedRect(0, 0, w, h, 99, 99)
		del painter
		# try:
		img.setMask(mask)
		# except Exception, e:
			# print e.message
		self.userAvatar.setPixmap(img)

	def set_user_avatar(self, img):
		self.set_round_img(self.userAvatar, QtGui.QPixmap(img))

	def set_user_name(self, s):
		self.userName.setText(s)
		self.userNameShadow.setText(s)

if __name__ == "__main__":
	PixivSync.init()