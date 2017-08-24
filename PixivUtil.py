# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import os
import time
import re
import random
import json
import threading

se = requests.session()

class Pixiv():

	def __init__(self):
		self.base_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
		self.login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
		self.notify_url = '/notify_all.php'
		self.notify_work_url = 'https://www.pixiv.net/rpc/notify.php'
		self.return_to = 'https://www.pixiv.net'
		
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
		post_key = BeautifulSoup(get(se, self.base_url, headers = self.headers).text, 'lxml').find('input')['value']
		data = {
			'pixiv_id': id,
			'password': pswd,
			'return_to': self.return_to,
			'post_key': post_key
		}
		resp_text = post(se, self.login_url, data = data, headers = self.headers).text
		resp = json.loads(resp_text, 'utf-8')
		if 'success' not in resp['body']:
			for x in resp['body']['validation_errors']:
				return [x, resp['body']['validation_errors'][x]]
			# return resp['body']['validation_errors']
		else:
			self.pid = id
			self.pswd = pswd

			cookies = requests.utils.dict_from_cookiejar(se.cookies)
			cookies['login_ever'] = 'yes'
			cookies['user_language'] = 'zh'
			cookies['__utmc'] = '235335808'
			cookies['__utma'] = '235335808.186197117.1487139067.1503166340.1503195157.86'
			cookies['__utmb'] = '235335808.512.9.1503200678674'
			cookies['__utmz'] = '235335808.1502737260.45.7.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)'
			se.cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar = None, overwrite = True)
			return None
	
	def getServer(self):
		ss = requests.session()
		ss.cookies = se.cookies
		return ss

	def check_msg(self):
		ss = se#self.getServer()
		main_page_html = get(ss, self.return_to, timeout = 5).text
		main_page = BeautifulSoup(main_page_html, 'lxml')
		post_key = main_page.find('input', attrs = {'name': 'tt'})['value']
		notify_msg = self.notify_suffix + post_key
		rmsg =  post(ss, self.notify_work_url, 
			headers = self.notify_headers, data = notify_msg
		)
		if rmsg == None:
			return ""
		return rmsg.text

	def check_priv(self):
		ss = se
		# main_page_html = get(ss, self.return_to, timeout = 3).text
		# main_page = BeautifulSoup(main_page_html, 'lxml')
		# post_key = main_page.find('input', attrs = {'name': 'tt'})['value']
		rpriv = get(ss, self.return_to + '/rpc/index.php?mode=latest_message_threads2&num=5',#'&tt=' + post_key,
			headers = create_header(self.return_to)
		)
		if rpriv == None:
			return ""
		return rpriv.text

def create_header(url):
	return {
		'Referer': url,
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
				'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
	}

mutex = threading.Lock()

def get(ss, *args, **kwargs):
	mutex.acquire()
	while 1:
		try:
			r = ss.get(*args, **kwargs)
			break
		except Exception, e:
			print e.message
	mutex.release()
	return r

def post(ss, *args, **kwargs):
	mutex.acquire()
	while 1:
		try:
			r = ss.post(*args, **kwargs)
			break
		except Exception, e:
			print e.message
	mutex.release()
	return r

pixiv = Pixiv()

if __name__ == "__main__":
	import cache
	dat = cache.config.read(('pixiv_id', 'password'))
	# import testform
	pixiv.login(dat['pixiv_id'], dat['password'])
	# testform.CheckMessageThread().start()
	print pixiv.check_msg()