# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic
import json
import time
import PixivUtil
import systray_rc
import requests
import cache
import MessageBox
import IllustBox
import os
from PTime import getTime, genUnix

window = None
path = os.path.abspath(os.path.dirname(__file__) + os.path.sep)
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
		self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint|QtCore.Qt.WindowCloseButtonHint) 
		self.setFixedSize(self.width(), self.height())
		self.messageLookup = {}
		self.privateLookup = {}

		# messageBox 
		self.messageBox = MessageBox.MessageBox(self.tbMessage)
		self.privateBox = MessageBox.MessageBox(self.tbPrivate)
		self.illustBox = IllustBox.IllustBox(self.tbMain)

		# loginThread update UI using following signals
		self.loginThread = None
		self.connect(self, QtCore.SIGNAL("login-success"), self.login_success)
		self.connect(self, QtCore.SIGNAL("login-fail"), self.login_fail)
		self.connect(self, QtCore.SIGNAL("receive-msg"), self.dispatchMsg)
		self.connect(self, QtCore.SIGNAL("receive-priv"), self.dispatchPriv)
		self.connect(self, QtCore.SIGNAL("set-user-avatar"), self.set_user_avatar)
		self.connect(self, QtCore.SIGNAL("set-user-name"), self.set_user_name)
		self.connect(self, QtCore.SIGNAL('get-illust'), self.get_illust)
		self.btnLogin.clicked.connect(PixivSync.sync.login)

		self.trayIcon = QtGui.QSystemTrayIcon(self)
		self.trayIcon.show()

		# need login when form create
		self.setLoginMode(True)

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
		self.illustBox.reset()
		cache.config.write({
			'cookies': requests.utils.dict_from_cookiejar(PixivUtil.se.cookies),
			'pixiv_id': self.pixiv_id
			# 'password': self.password
		})

	def login_fail(self, result):
		self.showMessage(u'登录失败', result[1])

	def get_illust(self, q, r):
		self.illustBox.endAppend(q, r)

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
								(reduce(lambda x, y: unicode(x) + u', ' + unicode(y), 
									[x['name'] for x in details['users']])
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
		try:
			priv = json.loads(priv)
		except Exception, e:
			print priv
			return
		if not priv['error']:
			for x in priv['body']['message_threads']:
				id = int(x['thread_id'])
				if id not in self.privateLookup:
					self.privateLookup[id] = self.privateBox.push_back(
						unread = True,
						title = unicode(x['thread_name']),
						content = unicode(x['latest_content']),
						time = unicode(genUnix(x['modified_at'])),
						icon = cache.image.get(x['icon_url']['100x100'], 
							headers = PixivUtil.create_header(
								PixivUtil.pixiv.return_to
							))
					)
					self.privateLookup[id].timestamp = unicode(x['modified_at'])
				elif unicode(x['modified_at']) != unicode(self.privateLookup[id].timestamp):
					self.privateLookup[id].setAttribute(
						content = unicode(x['latest_content']),
						time = unicode(genUnix(x['modified_at']))
					)
					self.privateLookup[id].timestamp = unicode(x['modified_at'])
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

if __name__ == "__main__":
	PixivSync.init()