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

pixiv_rec = 'https://www.pixiv.net/recommended.php'
pixiv_rec_get_list = 'https://www.pixiv.net/rpc/recommender.php?type=illust&sample_illusts=auto&num_recommendations=500&tt='
pixiv_illust_query1 = 'https://www.pixiv.net/rpc/illust_list.php?illust_ids='
pixiv_illust_query2 = '&verbosity=&exclude_muted_illusts=1&tt='

class IlluThread(threading.Thread):
	def __init__(self):
		super(IlluThread, self).__init__()
		self.recommended_list = []
		self.query = []
		self.preloadQ = []
		self.preloadCount = 16
		self.id = 0

	def init(self):
		self.ss = PixivUtil.pixiv.getServer()
		illus_html = PixivUtil.get(self.ss, pixiv_rec, headers = 
			PixivUtil.create_header(PixivUtil.pixiv.return_to)).text
		illus = BeautifulSoup(illus_html, 'lxml')
		self.post_key = illus.find('input', attrs = {'name': 'tt'})['value']
		self.recommended_list = json.loads(PixivUtil.get(self.ss, pixiv_rec_get_list + self.post_key,
			headers = PixivUtil.create_header(pixiv_rec)).text)['recommendations']
		self.id = 0

	def getImg(self):
		if self.id >= len(self.recommended_list):	# lack of illus
			self.init()
		iid = self.recommended_list[self.id]
		pixiv_illust_query = pixiv_illust_query1 + str(iid) + pixiv_illust_query2 + self.post_key
		while 1:
			try:
				j = json.loads(PixivUtil.get(self.ss, pixiv_illust_query, 
					headers = PixivUtil.create_header(pixiv_rec)).text)
				data = j[0]
				break
			except Exception, e:
				print j, iid
		ppage_html = PixivUtil.get(self.ss, purl + str(iid), headers = 
			PixivUtil.create_header(PixivUtil.pixiv.return_to)).text
		ppage = BeautifulSoup(ppage_html, 'lxml')
		data['original-url'] = str(
			re.findall(r'(https://i.pximg.net/img-original[^"]*)', ppage_html)[0])
		for x in ppage.find_all('img'):
			s = re.findall(r'alt="([^"]*)"', str(x))
			if len(s) > 0 and unicode(s[0], 'utf-8') == data['illust_title']:
				img_url = str(x['src'])
				break
		icon = cache.image.get(str(img_url),#data['url']), 
			headers = PixivUtil.create_header(PixivUtil.pixiv.return_to))
		
		# self.query[0]['block'].setAttribute(title = unicode(data['illust_title']), 
		# 	icon = icon)
		data['icon_filename'] = icon
		self.id += 1
		return data

	def run(self):
		while 1:
			if len(self.query) > 0:
				if len(self.preloadQ) > 0:
					data = self.preloadQ[0]
					del self.preloadQ[0]
				else:
					data = self.getImg()
				PixivNotifier.window.emit(QtCore.SIGNAL('get-illust'), self.query[0], data)
				del self.query[0]
			elif len(self.preloadQ) < self.preloadCount:
				self.preloadQ.append(self.getImg())

	def getIllust(self, data):
		self.query.append(data)

purl = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='