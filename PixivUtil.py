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
		self.return_to = 'http://www.pixiv.net'
		
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

	def login(self, id, pswd):
		post_key = BeautifulSoup(se.get(self.base_url, headers = self.headers).text, 'lxml').find('input')['value']
		data = {
			'pixiv_id': id,
			'password': pswd,
			'return_to': self.return_to,
			'post_key': post_key
		}
		resp_text = se.post(self.login_url, data = data, headers = self.headers).text
		resp = json.loads(resp_text, "utf-8")
		if 'success' not in resp['body']:
			for x in resp['body']['validation_errors']:
				return [x, resp['body']['validation_errors'][x]]
			# return resp['body']['validation_errors']
		else:
			self.main_page_html = self.get_html(self.return_to, 3).text
			self.main_page = BeautifulSoup(self.main_page_html, 'lxml')
			post_key = self.main_page.find('input', attrs = {'name': 'tt'})['value']
			self.notify_msg = self.notify_suffix + post_key
			self.user_page_php = self.main_page.find('a', 
				attrs = {'class': 'user-name js-click-trackable-later'})['href']
			self.user_id = re.findall(r'\?id=(.+)', self.user_page_php)[0]
			self.user_page_php = self.return_to + self.user_page_php
			return None

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
		response = se.post(self.notify_work_url, 
			headers = self.notify_headers,
			data = self.notify_msg)
		# print response.text
		return response.text

pixiv = Pixiv()

if __name__ == "__main__":
	import cache
	dat = cache.config.read(('pixiv_id', 'password'))
	# import testform
	pixiv.login(dat['pixiv_id'], dat['password'])
	# testform.CheckMessageThread().start()
	print pixiv.check_msg()