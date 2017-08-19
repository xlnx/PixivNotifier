import threading
import time

class CheckMessageThread(threading.Thread):
	def __init__(self, parent = None):
		threading.Thread.__init__(self)
		self.msgQueue = []
	def run(self):
		while True:
			x = self.msgQueue[0]
			self.msgQueue.
			print self.x
			time.sleep(1)
	def change(self, x):
		self.x = x

thread = CheckMessageThread()
thread.start()
i = 0
while (1):
	print '===='
	i = i + 1
	thread.x = i
	time.sleep(2)