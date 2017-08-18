import sys
from PyQt4 import QtGui, QtCore
import msgList

class Main(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		self.setGeometry(600, 300, 400, 400)
		b = QtGui.QPushButton(self)
		self.connect(b, QtCore.SIGNAL("clicked()"), self.a)
		b.setGeometry(
			0, 300, 100, 50
		)
		b.show()
		b = QtGui.QPushButton(self)
		self.connect(b, QtCore.SIGNAL("clicked()"), self.b)
		b.setGeometry(
			200, 300, 100, 50
		)
		b.show()
		self.msgs = msgList.MessageList(self)
		self.msgs.push_back("sadads")

	def a(self):
		self.msgs.push_back("asdasd")

	def b(self):
		self.msgs.erase(0)

app = QtGui.QApplication(sys.argv)
form = Main()
form.show()
sys.exit(app.exec_())
