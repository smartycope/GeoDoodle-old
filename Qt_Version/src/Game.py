# from PIL import Image, ImageDraw, ImageColor
import json
import os
import pickle
from copy import deepcopy
from os.path import join

from PyQt5 import *
from PyQt5 import QtCore, QtGui, QtMultimedia, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget
from PyQt5.QtWebEngineWidgets import *
import PyQt5.QtWebEngineWidgets

from ColorDialog import ColorDialog
from Cope import DIR, UI, DATA, darken, debug, debugged, getTime, timeFunc, todo, collidePoint
from Geometry import *
from Line import Line
from Paper import Paper
from Pattern import Pattern
from Point import CoordPoint, TLPoint, GLPoint, InfPoint

# SAVES_FOLDER = DIR + 'saves/'
# DOT_SPREAD_LIMIT = 12
# MIRROR_LINE_COLOR = (87, 11, 13)
# OFFSCREEN_AMOUNT = 0
# DOT_COLOR = (0, 200, 0)
# DOT_SIZE = 2
# FOCUS_COLOR = (32, 45, 57)
# FOCUS_RADIUS = 5
# DRAG_DELAY = 15
# EXPORT_LINE_THICKNESS = 2

# BACKGROUND_COLOR = (200, 160, 100)

#* How much we're allowed to seperate patterns * their size - depricated
MAX_SPREAD_MULTIPLIER = 2
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)


class Game(QMainWindow):
    def __init__(self):
        super(Game, self).__init__()
        uic.loadUi(join(UI, "main.ui"), self)
        self.setWindowTitle('GeoDoodle')

        #* Set key repeat

        #* Set resizeable (if not already)

        #* Set as an optional fullscreen

        #* Set a default window size (does Qt already handle this?)

        #* Set up a settings file
        # with open(DIR + 'settings.jsonc', 'r') as file:
        #     self.settings = json.load(file)

        #* Set up the current draw color
        # self.currentDrawColor = self.settings['toolbarColors'][0]

        #* Offscreen amount
        # self.offScreenAmount = OFFSCREEN_AMOUNT * DOTSPREAD

        # self.paper = Paper(self)
        # self.setCentralWidget(self.paper)
        # self.paper = self.centralWidget()

        #* self.setSizeIncrement(self.paper.dotSpread, self.paper.dotSpread)

        # self.setAttribute(Qt.AA_ShareOpenGLContexts)
        # QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

        self.fullscreen = False
        self.bindMenuBar()
        self.toolbar = None
        self.colors = [QColor(i) for i in ('black', 'red', 'green', 'yellow', 'orange', 'blue', 'purple', 'white', 'brown', 'pink')]
        self.actions = []

        self.createToolbar()

        self.installEventFilter(self)
        self.setGeometry(100 / self.width(), 100 / self.height(), self.width(), self.height())
        # for i in self.actions:
        #     i.installEventFilter(self)


    #* Key presses aren't widget specific, so they're handled by the window
    def eventFilter(self, target, event):
        if event.type() == QEvent.KeyPress:
            self.paper.keyPressed(event)

        return super().eventFilter(target, event)


    def bindMenuBar(self):
        self.new_.triggered.connect(self.paper.new_)
        self.open.triggered.connect(self.paper.open)
        self.save.triggered.connect(self.paper.save)
        self.saveAs.triggered.connect(self.paper.saveAs)
        self.export_.triggered.connect(self.paper.export)
        self.quit.triggered.connect(self.exit)

        self.preferencesMenu.triggered.connect(self._preferencesMenu)
        self.undo.triggered.connect(self.paper.undo)
        self.redo.triggered.connect(self.paper.redo)

        self.fullscreen_.triggered.connect(self.toggleFullscreen)
        self.showToolbar.triggered.connect(self.toggleToolbar)
        self.showLen.triggered.connect(self.paper.setShowLen)

        self.repeatMenu.triggered.connect(self._repeatMenu)
        self.addBound.triggered.connect(self.paper.toggleBoundsMode)
        self.clearAll.triggered.connect(self.paper.clearAll)
        # mirror
        # mirrorInvert
        # mirrorVertical
        # mirrorHorizontal
        # mirrorCrossing

        self.controlsMenu.triggered.connect(self._controlsMenu)
        self.aboutMenu.triggered.connect(self._aboutMenu)
        self.creditsMenu.triggered.connect(self._creditsMenu)
        self.licenseMenu.triggered.connect(self._licenseMenu)
        self.donateMenu.triggered.connect(self._donateMenu)
        self.statusMenu.triggered.connect(self._statusMenu)
        self.aboutQt.triggered.connect(lambda *_: QMessageBox.aboutQt(None))
        # tb.actionTriggered[QAction].connect(self.toolbtnpressed)


    def _preferencesMenu(self):
        self.optionsMenu = uic.loadUi(join(UI, "preferences.ui"))
        self.setWindowTitle('Preferences')
        self.setModal(True)
        # self.optionsMenu
        # self.shortCuts = {}

        def restoreDefaults():
            todo('set defaults')

        def setShortcut():
            todo('custom shortcuts')

        def setBackground(selector):
            debug(selector)
            if selector == "Color":
                self.paper.background = self.optionsMenu.backgroundColor.getColor()
            elif selector == "Pattern":
                todo('figure out how to select a pattern/gradient')
                self.paper.background = self.optionsMenu.backgroundColor.getColor()
            elif selector == "Image":
                self.paper.background = self.optionsMenu.backgroundPath.file
            elif selector == "Map Image":
                todo('get an image from the map')
                self.paper.background = (255, 160, 100, 255)
            else:
                raise UserWarning("Something has gone horribly, horribly wrong.")


        #* Bind the dot unit mesurement to look pretty
        self.optionsMenu.dotSpreadMeasure.setSuffix(' ' + self.optionsMenu.dotSpreadUnit.text())
        self.optionsMenu.dotSpreadUnit.textEdited.connect(lambda s: self.optionsMenu.dotSpreadMeasure.setSuffix(' ' + s))

        #* Connect the restoreDefaults button
        self.optionsMenu.restoreDefaults.clicked.connect(restoreDefaults)

        #* Set all the values from paper
        if type(self.paper.background) is tuple:
            self.optionsMenu.backgroundColor.setColor(self.paper.background)
        elif type(self.paper.background) is str:
            self.optionsMenu.backgroundPath.file = self.paper.background
        # elif type(self.paper.background) is QGradient:
        #*     todo('Setting QGradient')
        # elif type(self.paper.background) is QImage:
        #*     todo('Setting QImage')

        self.optionsMenu.dotColor.setColor(self.paper.dotColor)
        self.optionsMenu.focusColor.setColor(self.paper.focusColor)

        self.optionsMenu.dotSpread.setValue(self.paper.dotSpread)
        self.optionsMenu.dotSpreadMeasure.setValue(self.paper.dotSpreadMeasure)
        self.optionsMenu.dotSpreadUnit.setText(self.paper.dotSpreadUnit)

        self.optionsMenu.exportThickness.setValue(self.paper.exportThickness)
        self.optionsMenu.savePath.setText(self.paper.savePath)
        self.optionsMenu.exportPath.setText(self.paper.exportPath)

        #* Fill the drop down menus
        self.optionsMenu.backgroundType.addItems(("Color", "Pattern", "Image", "Map Image"))


        #* Connect the background menu
        self.optionsMenu.backgroundType.currentIndexChanged["QString"].connect(setBackground)

        # TODO Set up the shortcuts
        self.optionsMenu.setShortcut.clicked.connect(setShortcut)

        #* Connect the ok button
        self.optionsMenu.accepted.connect(lambda *_: self.paper.updateSettings(self.optionsMenu))
        self.optionsMenu.accepted.connect(lambda *_: setBackground(self.optionsMenu.backgroundType.currentText()))

        self.optionsMenu.show()


    def toggleFullscreen(self):
        todo('toggleFullscreen')
        # pygame.display.toggle_fullscreen()

        # if not self.fullscreen:
        #     self.mainSurface = pygame.display.set_mode(self.screenSize, self.fullscreenWindowFlags)
        #     self.startingPoint = Pointf(self.screenSize) / 2
        #     self.dots = genDotArrayPoints(self.screenSize, OFFSCREEN_AMOUNT, DOTSPREAD)
        # else:
        #     self.mainSurface = pygame.display.set_mode(self.windowedSize, self.windowedWindowFlags)
        #     self.startingPoint = Pointf(self.windowedSize) / 2
        #     self.dots = genDotArrayPoints(self.windowedSize, OFFSCREEN_AMOUNT, DOTSPREAD)

        # self.fullscreen = not self.fullscreen


    def createToolbar(self):
        class QDoubleAction(QAction):
            # I have NO idea why this is static, and but it only works if it is.
            doubleClicked = pyqtSignal()
            def __init__(self, *args, delay=250, **kwargs):
                QPushButton.__init__(self, *args, **kwargs)
                # self.doubleClicked = pyqtSignal()
                self.delay = delay
                self.timer = QTimer()
                self.timer.setSingleShot(True)
                def tmp():
                    self.triggered.emit()
                    self.timer.stop()
                self.timer.timeout.connect(tmp)
                super().triggered.connect(self.checkDoubleClick)

            @pyqtSlot()
            def checkDoubleClick(self):
                if self.timer.isActive():
                    self.doubleClicked.emit()
                    self.timer.stop()
                else:
                    self.timer.start(self.delay)

        class QDoubleButton(QToolButton):
            # I have NO idea why these are static, and but it only works if it is.
            doubleClicked = pyqtSignal()
            clicked = pyqtSignal()

            def __init__(self, *args, delay=250, **kwargs):
                QPushButton.__init__(self, *args, **kwargs)
                # self.doubleClicked = pyqtSignal()
                self.delay = delay
                self.timer = QTimer()
                self.timer.setSingleShot(True)
                def tmp():
                    self.clicked.emit()
                    self.timer.stop()
                self.timer.timeout.connect(tmp)
                super().clicked.connect(self.checkDoubleClick)

            @pyqtSlot()
            def checkDoubleClick(self):
                if self.timer.isActive():
                    self.doubleClicked.emit()
                    self.timer.stop()
                else:
                    self.timer.start(self.delay)

        class ToolColorButton(QDoubleButton):
            colors = [QColor(i) for i in ('black', 'red', 'green', 'yellow', 'orange', 'blue', 'purple', 'white', 'brown', 'pink')]
            colorChanged = pyqtSignal(tuple)

            def __init__(self, index, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.color = self.colors[index]
                self.setObjectName(str(index+1))
                self.setText(str(index+1))
                self.setMinimumWidth(45)
                self.setShortcut(QKeySequence(str(index-1)))
                self.updateColor()

                self.clicked.connect(self.updateColor)
                self.doubleClicked.connect(self.getColor)

            def updateColor(self):
                #* StyleSheet method
                self.setStyleSheet(f"widget-animation-duration:40;"
                                   f"background-color: rgba{self.color.getRgb()};"
                                   f"color: rgba{self.color.getRgb()};"
                                   f"selection-background-color: rgba{self.color.getRgb()};"
                                   f"selection-color: rgba{self.color.getRgb()};")

                #* Palette method
                # pal = QPalette()
                # pal.setColor(QPalette.Highlight, self.colors[i])
                # pal.setColor(QPalette.Button, self.colors[i])
                # pal.setColor(QPalette.ButtonText, self.colors[i])
                # self.actions[i].setPalette(pal)

                # self.paper.currentDrawColor = self.colors[i].getRgb()

                self.colorChanged.emit(self.color.getRgb())

                # self.clearFocus()
                self.setFocus()
                self.update()

            def getColor(self):
                self.color = QColorDialog.getColor()
                self.updateColor()


        self.toolbar = self.addToolBar("")

        #* Configure the toolbar setup
        self.toolbar.setLayout(QHBoxLayout())
        self.toolbar.layout().setSpacing(25)

        #* Make simple expanding widgets to center the colors
        rSpacer = QWidget()
        lSpacer = QWidget()
        rSpacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lSpacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toolbar.addWidget(rSpacer)

        #* Actually add the buttons
        for i in range(10):
            button = ToolColorButton(i)
            button.colorChanged.connect(self.paper.setCurrentDrawColor)
            self.toolbar.addWidget(button)

        self.toolbar.addWidget(lSpacer)
        self.toolbar.hide()


    def toggleToolbar(self, on):
        if on: #self.getMenuBarAction('View', 'Toggle Toolbar').isChecked():
            self.toolbar.show()
        else:
            self.toolbar.hide()


    def _repeatMenu(self):
        class PatternMenu(QDialog):
            def __init__(self, *args, pattern=None, **kwargs):
                super().__init__(*args, **kwargs)
                assert pattern
                uic.loadUi(join(UI, "repeat.ui"), self)
                self.pattern = pattern

                self.setWindowTitle('Repeat Pattern')
                self.setModal(True)

                #* Set the minimum values for the sliders
                self.xOffset.setMinimum(-self.pattern.size[0] + 1)
                self.yOffset.setMinimum(-self.pattern.size[1] + 1)

                #* If you want to by default set the new color to black
                self.paper.currentDrawColor = (0, 0, 0)

                #* Connect the sliders manually, since they have nessicary parameters
                self.xOffset.sliderMoved.connect(lambda pos: self.update(xpos=pos))
                self.yOffset.sliderMoved.connect(lambda pos: self.update(ypos=pos))

                #* Fill the flip drop down menus
                self.flipRowOrientation.addItems(('None', 'Vertically', 'Horizontally'))
                self.flipColumnOrientation.addItems(('None', 'Vertically', 'Horizontally'))

                #*// Connect the drop down menus

                #* Connect the restore defaults button
                self.restoreDefaults.clicked.connect(self.setDefaults)


                #* I SHOULDN'T HAVE TO DO THIS.
                self.paper.width = 402
                self.paper.height = 318

                self.paper.setGeometry(0, 0, 402, 318)

                #* Connect the ok button
                self.okCancel.accepted.connect(self.update)

                # self.paper.currentLine = Line(0, GLPoint(-1, -1, *self.paper.s), color=(0, 0, 0))
                # self.paper.currentLine.finish(GLPoint(-1, -1, *self.paper.s), *self.paper.s, self.paper.lineVbo, self.paper.lines)

                # self.paper.reset()
                self.paper.doReset = True
                self.update()
                self.show()

            @pyqtSlot()
            def update(self, xpos=None, ypos=None):
                # super().update()
                if xpos is None:
                    xpos = self.xOffset.value()
                if ypos is None:
                    ypos = self.yOffset.value()

                # debug(self.paper.lines, self.paper.width, self.paper.height)

                # debug(self.paper.size(), color=2)
                self.paper.reset()

                # self.paper.resetLineVbo()

                #* Update all of the pattern options in paper
                self.paper.overlap = (xpos, ypos)
                self.paper.includeHalfsies = self.includeHalfsies.isChecked()
                self.paper.rowSkip = self.rowSkip.value()
                self.paper.rowSkipAmount = self.rowSkipAmount.value()
                self.paper.columnSkip = self.columnSkip.value()
                self.paper.columnSkipAmount = self.columnSkipAmount.value()
                self.paper.flipRow = self.flipRow.value()
                self.paper.flipRowOrientation = self.flipRowOrientation.currentText()
                self.paper.flipColumn = self.flipColumn.value()
                self.paper.flipColumnOrientation = self.flipColumnOrientation.currentText()

                self.paper.update()
                self.paper.repeatPattern(self.pattern)

                return super().update()

            @pyqtSlot()
            def setDefaults(self):
                self.paper.reset()

                self.paper.overlap = (0, 0)
                self.paper.includeHalfsies = True
                self.paper.rowSkip = 1
                self.paper.rowSkipAmount = 0
                self.paper.columnSkip = 1
                self.paper.columnSkipAmount = 0

                self.paper.flipRow = 1
                self.paper.flipRowOrientation = 'None'
                self.paper.flipColumn = 1
                self.paper.flipColumnOrientation = 'None'

                self.xOffset.setSliderPosition(0)
                self.yOffset.setSliderPosition(0)

                self.includeHalfsies.setChecked(True)

                self.rowSkip.setValue(1)
                self.rowSkipAmount.setValue(0)
                self.columnSkip.setValue(1)
                self.columnSkipAmount.setValue(0)


        if len(self.paper.bounds) > 1:
            try:
                pattern = self.paper.getPattern()
            except UserWarning as err:
                debug(err, color=-1)
                return

            def transferSettings():
                self.paper.overlap = self.patternMenu.paper.overlap
                self.paper.includeHalfsies = self.patternMenu.paper.includeHalfsies
                self.paper.rowSkip = self.patternMenu.paper.rowSkip
                self.paper.rowSkipAmount = self.patternMenu.paper.rowSkipAmount
                self.paper.columnSkip = self.patternMenu.paper.columnSkip
                self.paper.columnSkipAmount = self.patternMenu.paper.columnSkipAmount
                self.paper.flipRow = self.patternMenu.paper.flipRow
                self.paper.flipRowOrientation = self.patternMenu.paper.flipRowOrientation
                self.paper.flipColumn = self.patternMenu.paper.flipColumn
                self.paper.flipColumnOrientation = self.patternMenu.paper.flipColumnOrientation

            self.patternMenu = PatternMenu(self, pattern=pattern)
            self.patternMenu.okCancel.accepted.connect(transferSettings)
            self.patternMenu.okCancel.accepted.connect(lambda: self.paper.repeatPattern(self.patternMenu.pattern))


    def _controlsMenu(self):
        controls = 'Important Controls:\n'\
        '\n'\
        'Left click/space bar: start/finish a line\n'\
        'Right click/c: start/finish a line and start a new one\n'\
        'Middle click/q: delete bound or lines (for now, will eventually switch to moving the pattern)\n'\
        'Scroll: zoom in/out (not implemented yet)\n'\
        'o: open the preferences menu\n'\
        'Q: delete all lines\n'\
        'b: add a bound\n'\
        'r: repeat the lines in the selected area across the screen\n'\
        'l: toggle line lengths\n'\
        'm: mirror lines (not implemented yet)\n'\
        't: toggle color toolbar (works, but colors are currently broken)\n'\
        'f: toggle fullscreen (not implemented yet)\n'\
        'ctrl+s: save the pattern for later editing\n'\
        'ctrl+o: open a saved pattern\n'\
        'ctrl+n: make a new pattern (not implemeted yet)\n'\
        'ctrl+shift+s: save as (not implemented yet)\n'\
        'ctrl+e: export pattern as an image (I don\'t think this works. I haven\'t tried.)\n'\
        'ctrl+z: undo (not implemented yet)\n'\
        'ctrl+y: redo (not implemented yet)\n'\
        'Esc: exit'

        QMessageBox.information(None, 'Controls', controls)

    def _aboutMenu(self):
        about = 'Welcome to GeoDoodle!\n'\
        'GeoDoodle is a graph paper-like doodling program. At least, that\'s what it was originally intended for. '\
        'It turned out to be useful for things from quilting to landscaping, and I\'ve tried to include features for each.\n'\
        '\n'\
        'If you have any problems, if it crashes, if something doesn\'t work how you like it to, or you have ideas for it, '\
        'please let me know so I can fix it or add it in. This is the alpha test, so I would love your feedback. '\
        'Just text or email me at smartycope@gmail.com / (208)513-0110\n'\
        '\n'\
        'If you just found this and are completely bamboozled as to how to do anything with it, check out the controls menu.\n'\
        '\n'\
        'If you don\'t think it\'s complete garbage, check out the donate menu. College is expensive.\n'\
        '\n'\
        'If you are a programmer and you like it so much you\'d like to contribute, go for it. My GitHub username is smartycope.\n'\
        'Enjoy!'

        # QMessageBox.information(None, 'About', about)
        QMessageBox.about(None, 'About', about)

    def _creditsMenu(self):
        credits = 'This magnificent program is brought to you by: \n'\
        'Copeland Carter, Eng.\n'\
        '\n'\
        'I would also like to thank Brigham Keys, for answering all my dumb questions, and my parents for, you know, raising me.\n'\
        '\n'\
        'Hi Liam!'

        QMessageBox.about(None, 'Credits', credits)

    def _licenseMenu(self):
        l = 'This software is licensed under the GPL3.0.\n'\
        'This means it is free and open-source software\n'\
        'This just means you can do whatever the heck you want with it.\n'\
        'If you really want to, you can learn more about it here: https://www.gnu.org/licenses/gpl-3.0.en.html'

        QMessageBox.about(None, 'License', l)

    def _donateMenu(self):
        donate = 'While this software is free, I am a poor college student who likes to eat.\n'\
        'Like, preferably regularly.\n'\
        'So if you liked this program and can spare change for some ramen noodles, Venmo me some money at @Copeland-Carter\n'\
        'I\'d greatly appreciate it.'

        QMessageBox.about(None, 'Donate', donate)

    def _statusMenu(self):
        status = 'If you have any ideas or problems, text or email me at smartycope@gmail.com / (208)513-0110\n'\
        '\n'\
        'What works, what does\'t, and what\'s on the todo list \n'\
        '(in no particular order):\n'\
        'What works:\n'\
        'Drawing lines (you have to start somewhere)\n'\
        'Repeating patterns\n'\
        'Offsetting rows/columns\n'\
        'Flipping rows/columns\n'\
        'Saving patterns\n'\
        'Opening patterns\n'\
        'The preferences menu\n'\
        'Length labels\n'\
        'Changing the dot color\n'\
        'Changing the focus color\n'\
        'Changing the background color\n'\
        'The color toolbar\n'\
        '\n'\
        'What should work, but doesn\'t:\n'\
        'The induvidual line colors\n'\
        'Exporting patterns to images\n'\
        'Setting the background to be an image\n'\
        'The easter egg ;)\n'\
        '\n'\
        'Features I\'m planning to add eventually:\n'\
        'Setting the background to be a pretty gradient\n'\
        'Setting the background to be a satalite view of a property\n'\
        'More cool features in that direction (like hooking up to GIS data to get property lines and accurate measurements)\n'\
        'Moving the pattern/page around\n'\
        'Scaling the pattern/page\n'\
        'Customizable key repeat/interval delay\n'\
        'Customizable controls\n'\
        'Mirroring\n'\
        'Split the vertical and horizontal drop down menus into buttons, so you can do both\n'\
        'Lots of more things that I can\'t think of at the moment, but I know I\'ve had the idea for.'

        QMessageBox.about(None, 'Status', status)


    def meme():
        url = QtCore.QUrl.fromLocalFile('/home/marvin/Downloads/Rick-Astley-Never-Gonna-Give-You-Up.mp3')
        content = QtMultimedia.QMediaContent(url)
        player = QtMultimedia.QMediaPlayer()
        player.setMedia(content)
        player.play()


        meme = uic.loadUi(join(DATA, 'meme.ui'))
        debug(meme)

        pixmap = QPixmap("/home/marvin/hello/python/GeoDoodle/Qt_Version/GeoDoodle/paulblart.png")
        scene = QGraphicsScene(meme)
        item = QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        meme.graphicsView.setScene(scene)

        meme.show()


    def exit(self):
        self.paper.exit()
        self.close()
