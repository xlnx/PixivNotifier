# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import os
import time
import re
import random
import json

se = requests.session()

class Pixiv():

	def __init__(self):
		self.base_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
		self.login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
		self.notify_url = '/notify_all.php'
		self.notify_work_url = 'https://www.pixiv.net/rpc/notify.php'
		self.return_to = 'http://www.pixiv.net/'
		
		self.headers = {
			'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
						  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
		}
		self.notify_headers = {
			'Referer': 'https://www.pixiv.net/',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) ' \
						  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
			"Content-Length": "0",
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
		}
		self.notify_suffix = 'op=notify&tt='
		self.ip_list = []

	def login(self, id, pswd):
		post_key = BeautifulSoup(se.get(self.base_url, headers = self.headers).text, 'lxml').find('input')['value']
		data = {
			'pixiv_id': id,
			'password': pswd,
			'return_to': self.return_to,
			'post_key': post_key
		}
		se.post(self.login_url, data = data, headers = self.headers)

	def get_proxy(self):
		html = requests.get('http://haoip.cc/tiqu.htm')
		ip_list_temp = re.findall(r'r/>(.*?)<b', html.text, re.S)
		for ip in ip_list_temp:
			i = re.sub('\n', '', ip)
			self.ip_list.append(i.strip())
			print(i.strip())

	''' 会被反爬,改成使用代理
		def get_tml(self, url):
			response = se.get(url, headers=self.headers)
			return response
	'''
	def get_html(self, url, timeout, proxy = None, num_entries = 5):
		if proxy is None:
			try:
				return se.get(url, headers = self.headers, timeout = timeout)
			except:
				if num_entries > 0:
					print('获取网页出错,5秒后将会重新获取倒数第', num_entries, '次')
					time.sleep(5)
					return self.get_html(url, timeout, num_entries = num_entries - 1)
				else:
					print('开始使用代理')
					time.sleep(5)
					ip = ''.join(str(random.choice(self.ip_list))).strip()
					now_proxy = {'http': ip}
					return self.get_html(url, timeout, proxy = now_proxy)
		else:
			try:
				return se.get(url, headers = self.headers, proxies = proxy, timeout = timeout)
			except:
				if num_entries > 0:
					print('正在更换代理,5秒后将会重新获取第', num_entries, '次')
					time.sleep(5)
					ip = ''.join(str(random.choice(self.ip_list))).strip()
					now_proxy = {'http': ip}
					return self.get_html(url, timeout, proxy = now_proxy, num_entries = num_entries - 1)
				else:
					print('使用代理失败,取消使用代理')
					return self.get_html(url, timeout)

	def check_msg(self):
		key_soup = BeautifulSoup(self.get_html(self.return_to, 3).text, 'lxml')
		for x in key_soup.find_all('a', href = self.notify_url):
			span = BeautifulSoup(str(x), 'lxml').find('span')
			if (span != None):
				if int(span.string) > 0:
					print 'New msg: ' + span.string
					# return '{"items":[{"id":24326867,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 12:07:23 +0900","type":"nice","unread":true,"details":{"target":{"id":64422822,"type":"illust","title":"Heartbroken Koishi","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/15/04/09/26/64422822_p0_square1200.jpg"},"count":9}},{"id":317000650,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 12:07:23 +0900","type":"bookmarked","unread":true,"details":{"target":{"id":64422822,"type":"illust","title":"Heartbroken Koishi","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/15/04/09/26/64422822_p0_square1200.jpg"},"count":8,"content":{"bookmark_count":8}}},{"id":317490967,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 10:40:34 +0900","type":"bookmarked","unread":true,"details":{"target":{"id":64461432,"type":"illust","title":"Subterranean Rose","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/17/02/58/16/64461432_p0_square1200.jpg"},"count":1,"content":{"bookmark_count":1}}},{"id":24778695,"user_id":10949667,"notified_at":"Thu, 17 Aug 2017 10:40:34 +0900","type":"nice","unread":true,"details":{"target":{"id":64461432,"type":"illust","title":"Subterranean Rose","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/17/02/58/16/64461432_p0_square1200.jpg"},"count":2}},{"id":317393171,"user_id":10949667,"notified_at":"Wed, 16 Aug 2017 23:33:27 +0900","type":"bookmarked","unread":false,"details":{"target":{"id":64157922,"type":"illust","title":"こいし~","url":"https://i.pximg.net/c/128x128/img-master/img/2017/08/01/01/25/26/64157922_p0_square1200.jpg"},"count":6,"content":{"bookmark_count":6}}}],"remaining_unread_count":0}'
					post_key = key_soup.find('input', attrs = {'name': 'tt'})['value']
					notify_msg = self.notify_suffix + post_key
					response = se.post(self.notify_work_url, 
						headers = self.notify_headers,
						data = notify_msg)
					return response.text
				else:
					print 'No msg'
					return False

pixiv = Pixiv()

def login(id, pw):
	return pixiv.login(id, pw)

def check_msg():
	return pixiv.check_msg()