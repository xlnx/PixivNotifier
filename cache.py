# -*- coding: utf-8 -*-
import requests
import os
import json
import os.path 
import PixivNotifier
import PixivUtil

def getFileExt(path): 
	return os.path.splitext(path)[1]

def getFileDir(file):
	return os.path.split(file)[0]

class imgCache:
	def __init__(self, d = 'imgCache/'):
		self.setCacheDir(d)

	def setCacheDir(self, dir):
		# dir = PixivNotifier.path + '/' + dir
		self.cacheDir = dir
		if not os.path.isdir(dir):
			os.mkdir(dir)

	def downloadImg(self, url, fileName, headers = {}):
		while 1:
			try:
				ir = PixivUtil.get(
					PixivUtil.pixiv.getServer(), url, headers = headers)
				break
			except Exception, e:
				continue
		if ir.status_code == 200:
			open(fileName, 'wb').write(ir.content)

	def find(self, url = "", name = None):
		if name == None:
			fname = self.cacheDir + hex(abs(hash(url))) + getFileExt(url)
		else:
			fname = self.cacheDir + name + getFileExt(url)
		if os.path.isfile(fname):
			return fname
		return None

	def get(self, url, name = None, headers = {}):
		if name == None:
			fname = self.cacheDir + hex(abs(hash(url))) + getFileExt(url)
		else:
			fname = self.cacheDir + name + getFileExt(url)
		if not os.path.isfile(fname):
			self.downloadImg(url, fname, headers)
		return fname

	def update(self, url, name = None, headers = {}):
		if name == None:
			fname = self.cacheDir + hex(abs(hash(url))) + getFileExt(url)
		else:
			fname = self.cacheDir + name + getFileExt(url)
		# if not os.path.isfile(fname):
		self.downloadImg(url, fname, headers)
		return fname

image = imgCache()

class dataCache:
	def __init__(self, d = 'userData/config.json'):
		self.setFileName(d)

	def setFileName(self, s):
		# s = PixivNotifier.path + '/' + s
		self.fileName = s
		d = getFileDir(s)
		if not os.path.isdir(d):
			os.mkdir(d)
	
	def read(self, list, section = None):
		result = {}
		if os.path.isfile(self.fileName):
			f = open(self.fileName, 'r')
			data = json.load(f)
			for x in list:
				if section is None:
					if x in data:
						result[x] = data[x]
				else:
					if section in data and x in data[section]:
						result[x] = data[section][x]
			f.close()
		return result 

	def write(self, map, section = None):
		data = {}
		if os.path.isfile(self.fileName):
			f = open(self.fileName, 'r')
			data = json.load(f)
			f.close
		if section is None:
			for x in map:
				data[x] = map[x]
		else:
			if not section in data:
				data[section] = {}
			for x in map:
				data[section][x] = map[x]
		f = open(self.fileName, 'w')
		json.dump(data, f)
		f.close()

config = dataCache()

# src = "https://i.pximg.net/c/128x128/img-master/img/2017/08/15/04/09/26/64422822_p0_square1200.jpg"
# print cache.getImg(src)
