from PyQt5.QtWidgets import QColorDialog, QPushButton, QCommandLinkButton, QFileDialog, QLineEdit
from PyQt5.QtGui import QColor

class ColorDialog(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.color = QColor(237, 126, 4)
        self.setStyleSheet(f"background-color:rgba{self.color.getRgb()}")

        def _tmp():
            self.color = QColorDialog.getColor()
            self.setStyleSheet(f"background-color:rgba{self.color.getRgb()}")

        self.showMenu = _tmp


class AbstractFileDialog(QLineEdit):
    def __init__(self, *args, save=True, **kwargs):
        super().__init__(*args, **kwargs)

        self.file = "NOT A FILE"

        self.setText(self.file)
        self.hasOpened = False


        def _tmp(event):
            if not self.hasOpened:
                self.file = QFileDialog.getSaveFileName()[0] if save else QFileDialog.getOpenFileName()[0]
                self.clearFocus()
                self.setText(self.file)
                self.hasOpened = True

        def _tmp2(*_):
            self.hasOpened = False

        self.focusInEvent = _tmp
        self.focusOutEvent = _tmp2


class SaveFileDialog(AbstractFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, save=True, **kwargs)


class OpenFileDialog(AbstractFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, save=False, **kwargs)