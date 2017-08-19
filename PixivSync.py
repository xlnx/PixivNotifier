# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup
from PyQt4 import QtCore, QtGui, uic
import json
import time
import cache
import thread
import threading
import PixivUtil
import requests

class Sync():
	def __init__(self):
		self.loginLock = False
		self.msgThread = None
		self.userThread = None

	def isLogining(self):
		return self.loginLock

	def login(self):
		if not self.loginLock:
			self.loginLock = True
			thread.start_new_thread(self.pixivLogin, ())
			return True
		return False
			
	def isFetchingUserData(self):
		return self.userThread is not None

	def fetchUserData(self):
		if self.userThread is None:
			self.userThread = UserDataThread()
			self.userThread.start()
			return True
		return False

	def isCheckingMsg(self):
		return self.msgThread is not None

	def beginCheckMsg(self, interval = 60):
		if self.msgThread is None:
			self.msgThread = CheckMessageThread(interval)
			self.msgThread.start()
			return True
		return False

	def endCheckMsg(self):
		if self.msgThread is not None:
			self.msgThread.exitSignal = True
			return True
		return False

	def pixivLogin(self):
		import PixivNotifier
		PixivNotifier.window.lePixivID.setReadOnly(True)
		PixivNotifier.window.lePassword.setReadOnly(True)
		PixivNotifier.window.btnLogin.setEnabled(False)
		PixivNotifier.window.pixiv_id = str(PixivNotifier.window.lePixivID.text())
		PixivNotifier.window.password = str(PixivNotifier.window.lePassword.text())
		result = PixivUtil.pixiv.login(PixivNotifier.window.pixiv_id, PixivNotifier.window.password)
		if result is None:
			PixivNotifier.window.emit(QtCore.SIGNAL("login-success"))
		else:
			PixivNotifier.window.emit(QtCore.SIGNAL("login-fail"), result)
		PixivNotifier.window.lePixivID.setReadOnly(False)
		PixivNotifier.window.lePassword.setReadOnly(False)
		PixivNotifier.window.btnLogin.setEnabled(True)
		self.loginLock = False

sync = Sync()

def init():
	app = QtGui.QApplication(sys.argv)
	import PixivNotifier
	try:
		QtGui.QApplication.setQuitOnLastWindowClosed(False)

		PixivNotifier.window = PixivNotifier.Window()
		user = cache.config.read(('pixiv_id', 'password'))
		if 'pixiv_id' in user and 'password' in user:
			PixivNotifier.window.lePixivID.setText(user['pixiv_id'])
			PixivNotifier.window.lePassword.setText(user['password'])
			PixivNotifier.window.btnLogin.setFocus()
			sync.login()
		else:
			PixivNotifier.window.lePixivID.setFocus()
		PixivNotifier.window.show()
	except Exception, e:
		print e.message
	sys.exit(app.exec_())

class CheckMessageThread(threading.Thread):
	def __init__(self, interval):
		super(CheckMessageThread, self).__init__()
		self.exitSignal = False
		self.interval = interval
	def run(self):
		import PixivNotifier
		PixivNotifier.window.emit(QtCore.SIGNAL("receive-msg"), '{"items":[{"id":24326867,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 12:07:23 +0900","type":"nice","unread":true,"details":{"target":{"id":64422822,"type":"illust","title":"Heartbroken Koishi","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/15/04/09/26/64422822_p0_square1200.jpg"},"count":9}},{"id":317000650,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 12:07:23 +0900","type":"bookmarked","unread":true,"details":{"target":{"id":64422822,"type":"illust","title":"Heartbroken Koishi","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/15/04/09/26/64422822_p0_square1200.jpg"},"count":8,"content":{"bookmark_count":8}}},{"id":317490967,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 10:40:34 +0900","type":"bookmarked","unread":true,"details":{"target":{"id":64461432,"type":"illust","title":"Subterranean Rose","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/17/02/58/16/64461432_p0_square1200.jpg"},"count":1,"content":{"bookmark_count":1}}},{"id":24778695,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 10:40:34 +0900","type":"nice","unread":true,"details":{"target":{"id":64461432,"type":"illust","title":"Subterranean Rose","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/17/02/58/16/64461432_p0_square1200.jpg"},"count":2}},{"id":317393171,"user_id":10949667,"notified_at":"Wed, 16 Aug 2017 23:33:27 +0900","type":"bookmarked","unread":false,"details":{"target":{"id":64157922,"type":"illust","title":"こいし~","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/01/01/25/26/64157922_p0_square1200.jpg"},"count":6,"content":{"bookmark_count":6}}}],"remaining_unread_count":0}')
		while not self.exitSignal:
			msg = PixivUtil.pixiv.check_msg()
			# print msg
			PixivNotifier.window.emit(QtCore.SIGNAL("receive-msg"), msg)
			time.sleep(self.interval)

class UserDataThread(threading.Thread):
	def __init__(self):
		super(UserDataThread, self).__init__()
	def run(self):
		import PixivNotifier
		ci = cache.imgCache('userData/' + PixivUtil.pixiv.user_id + '/')
		s = ci.find(name = 'user_avatar.jpg')
		if s != None:
			PixivNotifier.window.emit(QtCore.SIGNAL('set-user-avatar'), s)
			
		ss = requests.session()
		user_link = PixivUtil.pixiv.user_page_php
		sync.user_page_html = ss.post(user_link,
			headers = PixivUtil.pixiv.headers,
			cookies = PixivUtil.se.cookies
		).text
		sync.user_page = BeautifulSoup(sync.user_page_html, 'lxml')
		user_img = sync.user_page.find('img', 
			attrs = {'class': 'user-image'})['src']
		img_name = ci.update(user_img, 'user_avatar', headers = { 'Referer': user_link })
		PixivNotifier.window.emit(QtCore.SIGNAL('set-user-avatar'), img_name)