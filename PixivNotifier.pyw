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
queryInterval = 45

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
		self.setFixedSize(self.width(), self.height())
		self.messageLookup = {}
		self.privateLookup = {}

		# messageBox 
		self.messageBox = MessageBox.MessageBox(self.tbMessage)
		self.privateBox = MessageBox.MessageBox(self.tbPrivate)

		# loginThread update UI using following signals
		self.loginThread = None
		self.connect(self, QtCore.SIGNAL("login-success"), self.login_success)
		self.connect(self, QtCore.SIGNAL("login-fail"), self.login_fail)
		self.connect(self, QtCore.SIGNAL("receive-msg"), self.dispatchMsg)
		self.connect(self, QtCore.SIGNAL("receive-priv"), self.dispatchPriv)
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
		PixivSync.sync.beginCheckMsg(queryInterval)
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
			x['unread'] = 0
			if str(x) not in self.messageLookup:
				self.messageLookup[str(x)] = True
				details = x['details']
				f = {
					'nice': lambda: (u'赞！', u'「' + details['target']['title'] + 
								u'」已收到' + unicode(details['count']) + u'个赞！', 
								cache.image.get(details['target']['url'])),
					'bookmarked': lambda: (u'收藏', u'已有' + unicode(details['content']['bookmark_count']) + 
								u'人收藏了「' + details['target']['title'] + u'」~',
								cache.image.get(details['target']['url'])),
					'commented': lambda: (u'评论', u'「' + details['target']['title'] + u'」收到了第' +
								unicode(details['content']['comment_count']) + u'条评论！',
								cache.image.get(details['target']['url'])),
					'favorited': lambda: (u'粉丝', 
								(reduce(lambda x, y: unicode(x['name']) + u', ' + unicode(y['name']), details['users'])
								if len(details['users']) > 1 else unicode(details['users'][0]['name']))  + u'成为了你的粉丝！',
								cache.image.get(details['users'][0]['url'], headers = PixivUtil.create_header(
									PixivUtil.pixiv.return_to
								))),
					"tagged": lambda: (u'追加标签', u'「' + details['target']['title'] + u'」被追加了标签' +
								(reduce(lambda x, y: unicode(x) + u', ' + unicode(y) if unicode(y) != u"「」" else unicode(x), 
									[u'「' + unicode(x) + u'」' for x in details['tag']])
								if len(details['tag']) > 1 else unicode(details['tags'][0])) + u'！', 
								cache.image.get(details['target']['url'], headers = PixivUtil.create_header(
									PixivUtil.pixiv.return_to
								)))
				} [x['type']]
				if f is None:
					raise Exception("unknown message type: " + x['type'] + " with: " + x)
				m = f()
				if unread:
					self.showMessage(m[0], m[1])
				self.messageBox.push_back(
					unread = unread,
					title = m[0], 
					content = m[1], 
					time = getTime(str(x['notified_at'])),
					icon = m[2]
				)
		if data['remaining_unread_count'] > 0:
			self.showMessage(u'未读消息', u'还有' + unicode(data['remaining_unread_count']) + u'条...')

	def dispatchPriv(self, priv):
		priv = json.loads(priv)
		if not priv['error']:
			for x in priv['body']['message_threads']:
				id = int(x['thread_id'])
				if id not in self.privateLookup:
					self.privateLookup[id] = self.privateBox.push_back(
						unread = True,
						title = unicode(x['thread_name']),
						content = unicode(x['latest_content']),
						time = unicode(x['modified_at']),
						icon = cache.image.get(x['icon_url']['100x100'], 
							headers = PixivUtil.create_header(
								PixivUtil.pixiv.return_to
							))
					)
				elif unicode(x['modified_at']) != unicode(self.privateLookup[id].time.text()):
					self.privateLookup[id].setAttribute(
						content = unicode(x['latest_content']),
						time = unicode(x['modified_at'])
					)
					self.showMessage(unicode(x['thread_name']) + (u'（' + unicode(x['unread_num']) + u'）' 
						if int(x['unread_num']) > 1 else u''), unicode(x['latest_content']))
			# ))
		else:
			print priv['message']
	
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

def getTime(s):
	import win32timezone
	import re

	t = re.findall(r', (\S*) (\S*) [0-9]+ (.{2}).(.{2})[^\+-]*([\+-])([0-9]{2})(.*)', str(s))[0]
	d = int(t[0])
	m = t[1]
	h = int(t[2])
	mm = int(t[3])
	f = t[4]
	t5 = int(t[5]) if f == '+' else -int(t[5])
	t6 = int(t[6]) if f == '+' else -int(t[6])
	dt = re.findall(r'-([0-9]+)-([0-9]+)[^\+-]*([\+-])([0-9]+):([0-9]+)', str(win32timezone.now()))[0]
	ym = int(dt[0])
	yd = int(dt[1])
	g = dt[2]
	r5 = int(dt[3]) if g == '+' else -int(dt[3])
	r6 = int(dt[4]) if g == '+' else -int(dt[4])
	h -= t5 - r5
	mm -= t6 - r6
	if mm < 0:
		h -= 1
		mm += 60
	elif mm >= 60:
		h += 1
		mm -= 60
	if h > 23:
		d += 1
		h -= 24
	elif h < 0:
		d -= 1
		h += 24
	mstr = {
		'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 
		'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
	}
	m = mstr[m]
	if m == ym and d == yd:
		return str(h).zfill(2) + ':' + str(mm).zfill(2)
	else:
		return str(m) + '/' + str(d)

if __name__ == "__main__":
	PixivSync.init()