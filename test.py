import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
class Tooltip(QtGui.QWidget):

    def __init__(self,parent = None):
        QtGui.QWidget.__init__(self,parent)

        self.setGeometry(300,300,250,150)
        self.setWindowTitle('Tooltip')

        x = self.setToolTip('This is a QWidget widget')
        QtGui.QToolTip.setFont(QtGui.QFont('oldEnglish',10))

app = QtGui.QApplication(sys.argv)

tooltip = Tooltip()
tooltip.show()

sys.exit(app.exec_())