# -*- coding: utf-8 -*-
import requests
import os
import json
import os.path 

def getFileExt(path): 
	return os.path.splitext(path)[1]

def getFileDir(file):
	return os.path.split(file)[0]

class imgCache:
	def __init__(self):
		self.setCacheDir('imgCache/')

	def setCacheDir(self, dir):
		self.cacheDir = dir
		if not os.path.isdir(dir):
			os.mkdir(dir)

	def downloadImg(self, url, fileName):
		ir = requests.get(url)
		if ir.status_code == 200:
			open(fileName, 'wb').write(ir.content)

	def get(self, url):
		fname = self.cacheDir + hex(hash(url)) + getFileExt(url)
		if not os.path.isfile(fname):
			self.downloadImg(url, fname)
		return fname

image = imgCache()

class dataCache:
	def __init__(self):
		self.setFileName("userData/config.json")

	def setFileName(self, s):
		self.fileName = s
		d = getFileDir(s)
		if not os.path.isdir(d):
			os.mkdir(d)
	
	def read(self, list):
		result = {}
		if os.path.isfile(self.fileName):
			f = open(self.fileName, 'r')
			data = json.load(f)
			for x in list:
				if x in data:
					result[x] = data[x]
			f.close()
		return result 

	def write(self, map):
		data = {}
		if os.path.isfile(self.fileName):
			f = open(self.fileName, 'r')
			data = json.load(f)
			f.close
		for x in map:
			data[x] = map[x]
		f = open(self.fileName, 'w')
		json.dump(data, f)
		f.close()

config = dataCache()

# src = "https://i.pximg.net/c/128x128/img-master/img/2017/08/15/04/09/26/64422822_p0_square1200.jpg"
# print cache.getImg(src)
