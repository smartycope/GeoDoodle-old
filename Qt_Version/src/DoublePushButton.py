from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import pyqtSlot, pyqtSignal, QEvent, Qt, QTimer

# Literally just copied and pasted this from here:
# https://stackoverflow.com/questions/25987166/pyqt5-qpushbutton-double-click

class QDoublePushButton(QPushButton):
    doubleClicked = pyqtSignal()
    clicked = pyqtSignal()
    delayms = 250

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.clicked.emit)
        super().clicked.connect(self.checkDoubleClick)

    @pyqtSlot()
    def checkDoubleClick(self):
        if self.timer.isActive():
            self.doubleClicked.emit()
            self.timer.stop()
        else:
            self.timer.start(self.delayms)
