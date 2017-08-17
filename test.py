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
					# post_key = key_soup.find('input', attrs = {'name': 'tt'})['value']
					# notify_msg = self.notify_suffix + post_key
					# response = se.post(self.notify_work_url, 
					# 	headers = self.notify_headers,
					# 	data = notify_msg)
					# print response.json()
					return True
				else:
					print 'No msg'
					return False

pixiv = Pixiv()

def login(a, b):
	return pixiv.login(a, b)
def check_msg():
	return pixiv.check_msg()

login('963504621@qq.com', 'Dij217Prim')
check_msg()
