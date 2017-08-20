# -*- coding:utf8 -*- 
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import sys

app = QApplication(sys.argv)

window = QMainWindow()
window.show()
animation = QPropertyAnimation(window, "geometry")
animation.setDuration(10000)
animation.setStartValue(QRect(0, 0, 100, 30))
#animation.setKeyValueAt(0.5, QRect(240, 240, 100, 30));
animation.setEndValue(QRect(250, 250, 100, 30))
# animation.setEasingCurve(QEasingCurve.OutBounce)
animation.start()

app.exec_()
