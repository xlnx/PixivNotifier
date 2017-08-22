# -*- coding: utf-8 -*-
import re
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
import PixivNotifier

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

class CheckMessageThread(threading.Thread):
	def __init__(self, interval):
		super(CheckMessageThread, self).__init__()
		self.exitSignal = False
		self.interval = interval
	def run(self):
		# PixivNotifier.window.emit(QtCore.SIGNAL("receive-msg"), '{"items":[{"id":24326867,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 12:07:23 +0900","type":"nice","unread":true,"details":{"target":{"id":64422822,"type":"illust","title":"Heartbroken Koishi","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/15/04/09/26/64422822_p0_square1200.jpg"},"count":9}},{"id":317000650,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 12:07:23 +0900","type":"bookmarked","unread":true,"details":{"target":{"id":64422822,"type":"illust","title":"Heartbroken Koishi","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/15/04/09/26/64422822_p0_square1200.jpg"},"count":8,"content":{"bookmark_count":8}}},{"id":317490967,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 10:40:34 +0900","type":"bookmarked","unread":true,"details":{"target":{"id":64461432,"type":"illust","title":"Subterranean Rose","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/17/02/58/16/64461432_p0_square1200.jpg"},"count":1,"content":{"bookmark_count":1}}},{"id":24778695,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 10:40:34 +0900","type":"nice","unread":true,"details":{"target":{"id":64461432,"type":"illust","title":"Subterranean Rose","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/17/02/58/16/64461432_p0_square1200.jpg"},"count":2}},{"id":317393171,"user_id":10949667,"notified_at":"Wed, 16 Aug 2017 23:33:27 +0900","type":"bookmarked","unread":false,"details":{"target":{"id":64157922,"type":"illust","title":"こいし~","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/01/01/25/26/64157922_p0_square1200.jpg"},"count":6,"content":{"bookmark_count":6}}}],"remaining_unread_count":0}')
		while not self.exitSignal:
			msg = PixivUtil.pixiv.check_msg()
			# print msg
			PixivNotifier.window.emit(QtCore.SIGNAL("receive-msg"), msg)
			priv = PixivUtil.pixiv.check_priv()
			PixivNotifier.window.emit(QtCore.SIGNAL("receive-priv"), priv)
			time.sleep(self.interval)

class UserDataThread(threading.Thread):
	def __init__(self):
		super(UserDataThread, self).__init__()
		self.ci = cache.imgCache('userData/' + PixivUtil.pixiv.user_id + '/')
		self.di = cache.dataCache('userData/' + PixivUtil.pixiv.user_id + '/user_data.json')
		
	def updateUserProfile(self):
		s = self.di.read([u'ニックネーム'], 'user_profile')
		if u'ニックネーム' in s:
			PixivNotifier.window.emit(QtCore.SIGNAL('set-user-name'), s[u'ニックネーム'])

	def updateUserAvatar(self):
		s = self.ci.find(name = 'user_avatar.jpg')
		if s is not None:
			PixivNotifier.window.emit(QtCore.SIGNAL('set-user-avatar'), s)

	def updateUserData(self):
		self.updateUserAvatar()
		self.updateUserProfile()

	def pullUserData(self):
		# pull user_page
		ss = PixivUtil.pixiv.getServer()
		sync.user_page_url = PixivUtil.pixiv.user_page_php
		sync.user_page_html = PixivUtil.get(ss, sync.user_page_url, 
			headers = PixivUtil.create_header('http://www.pixiv.net')).text
		sync.user_page = BeautifulSoup(sync.user_page_html, 'lxml')
		try:
			user_img = sync.user_page.find('img', 
				attrs = {'class': 'user-image'})['src']
		except Exception, e:
			user_img = sync.user_page.find('a', 
				attrs = {'class': '_user-icon size-80 cover-texture'})['style']
			user_img = re.findall(r"url\('([^\)]*)'\)", user_img)[0]

		# pull user_image
		img_name = self.ci.update(user_img, 'user_avatar', headers = PixivUtil.create_header(sync.user_page_url))
		PixivNotifier.window.emit(QtCore.SIGNAL('set-user-avatar'), img_name)
		self.updateUserAvatar()

		# pull user_data
		user_data = sync.user_page.find_all('table', attrs = {'class': 'ws_table'})
		for y in user_data[0].find_all('tr'):
			self.di.write({y.find('td', attrs = {'class': 'td1'}).string:
				y.find('td', attrs = {'class': 'td2'}).string}, 'user_profile')
		self.updateUserProfile()
		if len(user_data) > 1:
			for y in user_data[1].find_all('tr'):
				self.di.write({y.find('td', attrs = {'class': 'td1'}).string: 
					y.find('td', attrs = {'class': 'td2'}).string}, 'environment')
		
		# pull user_illust
		sync.user_illust_list = []
		ill_list = sync.user_page.find_all('a', attrs = {'class': 'active_gray'})
		sync.user_illust_url = PixivUtil.pixiv.return_to + '/' + str(ill_list[0]['href'])
		sync.user_illust_html = PixivUtil.get(ss, sync.user_illust_url,
			headers = PixivUtil.create_header(sync.user_page_url)).text
		sync.user_illust = BeautifulSoup(sync.user_illust_html, 'lxml')

		ddi = cache.dataCache('userData/' + PixivUtil.pixiv.user_id + '/illust/data.json')
		# print sync.user_illust_html
		for x in sync.user_illust.find_all('li', attrs = {'class': 'image-item'}):
			y = x.find('h1', attrs = {'class', 'title'})
			if y != None:
				bk = x.find('a', attrs = {'class', 'bookmark-count _ui-tooltip'})
				val = re.findall(r'<a[^>]*><i[^>]*></i>([^<]*)</a>', str(bk))[0]
				value = {
					'page_url': PixivUtil.pixiv.return_to + '/' + str(y.parent['href']),
					'id': int(re.findall(r'illust_id=(.*)', str(y.parent['href']))[0]),
					'title': y.string,
					'rating': int(x.find('a', attrs = {'class', 'report-link rating-count'}).find('span').string),
					'comment': int(x.find('a', attrs = {'class', 'report-link comments'}).find('span').string),
					'view': int(x.find('a', attrs = {'class', 'report-link views'}).find('span').string),
					'bookmark': {
						'count': int(val),
						'details': PixivUtil.pixiv.return_to + str(bk['href'])
					}
				}
				html = PixivUtil.get(ss, value['page_url']).text
				ilpg = BeautifulSoup(html, 'lxml')
				img_url = None
				for x in ilpg.find_all('img'):
					s = re.findall(r'alt="([^"]*)"', str(x))
					if len(s) > 0 and unicode(s[0], 'utf-8') == value['title']:
						img_url = str(x['src'])
						break
				value['url'] = img_url
				sync.user_illust_list.append(value)
				ddi.write(value, str(value['id']))
				cci = cache.imgCache('userData/' + PixivUtil.pixiv.user_id + '/illust/')
				# if img_url is not None:
				cci.get(img_url, headers = PixivUtil.create_header(value['page_url']), name = str(value['id']))

		# pull user_bookmark
		sync.user_bookmark_url = PixivUtil.pixiv.return_to + str(ill_list[0]['href'])

	def run(self):
		self.updateUserData()
		self.pullUserData()

def init():
	app = QtGui.QApplication(sys.argv)
	# try:
	QtGui.QApplication.setQuitOnLastWindowClosed(False)
	QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName("system"))
	QtCore.QTextCodec.setCodecForCStrings(QtCore.QTextCodec.codecForName("system"))
	QtCore.QTextCodec.setCodecForLocale(QtCore.QTextCodec.codecForName("system"))

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
	# except Exception, e:
		# print e.message
	sys.exit(app.exec_())