from PyQt6.QtWidgets import QColorDialog, QPushButton, QCommandLinkButton, QFileDialog, QLineEdit
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import pyqtSlot, QEvent, Qt
from DoublePushButton import QDoublePushButton

from Cope import debug, invertColor
from copy import deepcopy


class ColorButton(QDoublePushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAutoFillBackground(True)

        self._color = QColor(200, 200, 200)
        self.updateColor()

        self.showMenu = self.getNewColor
        self.doubleClicked.connect(self.getNewColor)
        # If we choose a new color, we want to automatically select that color
        self.doubleClicked.connect(self.clicked.emit)

    def getNewColor(self):
        self.color = QColorDialog.getColor()

    def updateColor(self):
        #* StyleSheet method
        # self.setStyleSheet(f"background-color: rgba{self.color.getRgb()};"
        #                    f"selection-background-color: rgba{self.color.getRgb()};"
        #                    f"selection-color: rgba{self.color.getRgb()};")

        #* Palette method
        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Highlight, self._color)
        pal.setColor(QPalette.ColorRole.Button, self._color)
        # the [:-1] is there to drop the alpha (we don't want to invert the alpha)
        pal.setColor(QPalette.ColorRole.ButtonText, QColor(*(invertColor(self._color.getRgb()))[:-1]))
        self.setPalette(pal)

        # This shouldn't be necissary now, I removed focus in the ui file
        # self.clearFocus()
        self.update()

    def getColor(self):
        """ Just for connecting signals """
        return self.color

    @property
    def color(self):
       return self._color
    @color.setter
    def color(self, to):
       self._color = to
       self.updateColor()


# class AbstractFileDialog(QLineEdit):
#     def __init__(self, typeFunc, params, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.file = "NOT A FILE"
#         self.setText(self.file)

#         def getFile(*_):
#             got = typeFunc(*params)
#             debug(got)
#             if not len(got) or not len(got[0]):
#                 return
#             else:
#                 self.file = got if len(got[0]) == 1 else got[0]
#                 self.setText(self.file)

#         def setFile(to):
#             self.file = to

#         self.returnPressed.connect(getFile)
#         self.textChanged['QString'].connect(setFile)
#         self.installEventFilter(self)

#     def eventFilter(self, target, event):
#         if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return and target is self:
#             debug()
#             event.accept()
#             self.returnPressed.emit()
#             return True
#         else:
#             return super().eventFilter(target, event)


# class SaveFileDialog(AbstractFileDialog):
#     def __init__(self, *args, **kwargs):
#         super().__init__(QFileDialog.getSaveFileName,
#                          (None, "Save Pattern", "~/", "GeoDoodle Pattern (*.gdl)"),
#                          *args, **kwargs)


# class OpenImageDialog(AbstractFileDialog):
#     def __init__(self, *args, **kwargs):
#         super().__init__(QFileDialog.getOpenFileName,
#                          (None, "Open Image", "~/", "Image (*.png, *.jpg, *.jpeg, *.*)"),
#                          *args, **kwargs)

# class OpenPatternDialog(AbstractFileDialog):
#     def __init__(self, *args, **kwargs):
#         super().__init__(QFileDialog.getOpenFileName,
#                          (None, "Open Pattern", "~/", "GeoDoodle Pattern (*.gdl)"),
#                          *args, **kwargs)


# class OpenFolderDialog(AbstractFileDialog):
#     def __init__(self, *args, **kwargs):
#         super().__init__(QFileDialog.getExistingDirectory,
#                          (None, "Set Folder", "~/"),
#                          *args, **kwargs)
