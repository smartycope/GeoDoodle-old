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

from ColorDialog import ColorDialog
from Cope import DIR, UI, DATA, darken, debug, debugged, getTime, timeFunc, todo
from Geometry import *
from Line import Line
from Paper import Paper
from Pattern import Pattern
from Point import Pointf, Pointi

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

#* How much we're allowed to seperate patterns * their size
MAX_SPREAD_MULTIPLIER = 2




class Game(QMainWindow):
    def __init__(self):
        super(Game, self).__init__()
        uic.loadUi(join(UI, "main.ui"), self)
        # pygame.init()

        #* Set the icon
        #  with open(DIR + 'data/' + self.settings['iconFile'], 'r') as icon:
            # pygame.display.set_icon(pygame.image.load(icon))

        #* Set the name of the window

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

        self.setSizeIncrement(self.paper.dotSpread, self.paper.dotSpread)

        self.fullscreen = False
        self.bindMenuBar()
        self.toolbar = None
        self.colors = [QColor(i) for i in ('black', 'red', 'green', 'yellow', 'orange', 'blue', 'purple', 'white', 'brown', 'pink')]
        self.actions = []

        self.createToolbar()

        self.installEventFilter(self)
        # for i in self.actions:
        #     i.installEventFilter(self)


    #* Key presses aren't widget specific, so they're handled by the window
    def eventFilter(self, target, event):
        if event.type() == QEvent.KeyPress:
            self.paper.keyPressed(event)

        return super().eventFilter(target, event)


    def bindMenuBar(self):
        todo('bind mirroring')
        self.getMenuBarAction('File', 'New'         ).triggered.connect(self.paper._new)
        self.getMenuBarAction('File', 'Open...'     ).triggered.connect(self.paper.open)
        self.getMenuBarAction('File', 'Save'        ).triggered.connect(self.paper.save)
        self.getMenuBarAction('File', 'Save As...'  ).triggered.connect(self.paper.saveAs)
        self.getMenuBarAction('File', 'Export As...').triggered.connect(self.paper.export)
        self.getMenuBarAction('File', 'Quit'        ).triggered.connect(self.exit)

        self.getMenuBarAction('Edit', 'Preferences...').triggered.connect(self.preferencesMenu)
        self.getMenuBarAction('Edit', 'Undo'          ).triggered.connect(self.paper.undo)
        self.getMenuBarAction('Edit', 'Redo'          ).triggered.connect(self.paper.redo)

        self.getMenuBarAction('View', 'Toggle Fullscreen').triggered.connect(self.toggleFullscreen)
        self.getMenuBarAction('View', 'Toggle Toolbar'   ).triggered.connect(self.toggleToolbar)

        self.getMenuBarAction('Pattern', 'Repeat...'    ).triggered.connect(self.repeatMenu)
        self.getMenuBarAction('Pattern', 'Add Bounds'   ).triggered.connect(self.paper.toggleBoundsMode)
        self.getMenuBarAction('Pattern', 'Clear Pattern').triggered.connect(self.paper.clearAll)

        self.getMenuBarAction('Help', 'Controls...').triggered.connect(self.controlsMenu)
        self.getMenuBarAction('Help', 'About'      ).triggered.connect(self.aboutMenu)
        self.getMenuBarAction('Help', 'Credits'    ).triggered.connect(self.creditsMenu)
        self.getMenuBarAction('Help', 'License'    ).triggered.connect(self.licenseMenu)
        self.getMenuBarAction('Help', 'Donate'     ).triggered.connect(self.donateMenu)

        # tb.actionTriggered[QAction].connect(self.toolbtnpressed)


    def preferencesMenu(self):
        self.optionsMenu = uic.loadUi(join(UI, "preferences.ui"))
        self.optionsMenu.show()


    #* This is waaaay harder than it needs to be, but I don't know an easier way of doing it.
    def getMenuBarAction(self, menu, *path):

        parent = self.menuBar().actions()[[i.text() for i in self.menuBar().actions()].index(menu)]
        for i in path:
            parent = parent.menu().actions()[[i.text() for i in parent.menu().actions()].index(i)]
        return parent


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

        self.toolbar = self.addToolBar("")

        spacing = self.width() / 5
        # self.toolbar.setStyleSheet(f'* {{ spacing: {spacing} }}')

        def setupStyleSheet(i):
            self.toolbar.setStyleSheet(self.toolbar.styleSheet() +
                f"\nQToolButton#{i+1} {{ color:rgba{self.colors[i].getRgb()} }}"
                f"\nQToolButton#{i+1} {{ background-color:rgba{self.colors[i].getRgb()} }}"
                # f"\nQToolButton#{i+1} {{ selection-color:rgba{darken(self.colors[i].getRgb(), -30)} }}"
                # f"\nQToolButton#{i+1} {{ selection-background-color:rgba{darken(self.colors[i].getRgb(), -30)} }}"
                f"\nQToolButton#{i+1} {{ widget-animation-duration:30 }}"
            )

        def call(j):
            self.colors[j] = QColorDialog.getColor()
            setupStyleSheet(j)
            setColor(j)


        def setColor(j):
            self.paper.currentDrawColor = self.colors[j]
            for cnt, _ in enumerate(self.actions):
                setupStyleSheet(cnt)

            self.actions[j].setFocus()

        #* Configure the toolbar setup
        self.toolbar.setLayout(QHBoxLayout())
        # self.toolbar.layout().setAlignment(Qt.Alignment(Qt.AlignCenter))
        self.toolbar.layout().setSpacing(25) #(Qt.Alignment(Qt.AlignCenter))
        # debug(self.toolbar.layout().spacing(), name='spacing')
        # self.toolbar.


        #* Make simple expanding widgets to center the colors
        rSpacer = QWidget()
        lSpacer = QWidget()
        rSpacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lSpacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toolbar.addWidget(rSpacer)

        for i in range(10):
            button = QDoubleButton() #str(i+1))
            # button.setFocus()
            # self.toolbar.addAction(action)
            # button.setFocus()

            button.setObjectName(str(i+1))
            # self.toolbar.widgetForAction(action).setObjectName(str(i+1))
            # action.setObjectName(str(i+1))
            setupStyleSheet(i)

            button.setText(str(i+1))
            button.setMinimumWidth(45)
            # button.setShortcut(30+i)
            button.setShortcut(QKeySequence(str(i-1)))


            self.toolbar.addWidget(button)


            # self.toolbar.widgetForAction(action).setToolTipDuration(-1)
            # self.toolbar.widgetForAction(action).setToolTip('')


            self.actions.append(button)

            #* You SHOULD be able to do this. I have NO IDEA why you can't.
            #* Someone PLEASE explain this too me.
            # action.triggered.connect(setColor(i))
            # action.doubleClicked.connect(call(i))

        self.toolbar.addWidget(lSpacer)

        self.actions[0].setFocus()

        #* For loops, why have you forsaken me?
        self.actions[0].doubleClicked.connect(lambda: call(0))
        self.actions[1].doubleClicked.connect(lambda: call(1))
        self.actions[2].doubleClicked.connect(lambda: call(2))
        self.actions[3].doubleClicked.connect(lambda: call(3))
        self.actions[4].doubleClicked.connect(lambda: call(4))
        self.actions[5].doubleClicked.connect(lambda: call(5))
        self.actions[6].doubleClicked.connect(lambda: call(6))
        self.actions[7].doubleClicked.connect(lambda: call(7))
        self.actions[8].doubleClicked.connect(lambda: call(8))
        self.actions[9].doubleClicked.connect(lambda: call(9))

        self.actions[0].clicked.connect(lambda: setColor(0))
        self.actions[1].clicked.connect(lambda: setColor(1))
        self.actions[2].clicked.connect(lambda: setColor(2))
        self.actions[3].clicked.connect(lambda: setColor(3))
        self.actions[4].clicked.connect(lambda: setColor(4))
        self.actions[5].clicked.connect(lambda: setColor(5))
        self.actions[6].clicked.connect(lambda: setColor(6))
        self.actions[7].clicked.connect(lambda: setColor(7))
        self.actions[8].clicked.connect(lambda: setColor(8))
        self.actions[9].clicked.connect(lambda: setColor(9))

        self.toolbar.hide()


    def toggleToolbar(self, on):
        if on: #self.getMenuBarAction('View', 'Toggle Toolbar').isChecked():
            self.toolbar.show()
        else:
            self.toolbar.hide()


    def repeatMenu(self):
        class PatternMenu(QDialog):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                uic.loadUi(join(UI, "repeat.ui"), self)
                self.pattern = None
                self.xOffset.sliderMoved.connect(lambda pos: self.update(xpos=pos))
                self.yOffset.sliderMoved.connect(lambda pos: self.update(ypos=pos))
                self.okCancel.accepted.connect(self.update)
                self.restoreDefaults.clicked.connect(self.setDefaults)

            @pyqtSlot()
            def update(self, xpos=None, ypos=None):
                if xpos is None:
                    xpos = self.xOffset.value()
                if ypos is None:
                    ypos = self.yOffset.value()

                #* Update all of the pattern options in paper
                self.paper.overlap = (xpos, ypos)
                self.paper.includeHalfsies = self.includeHalfsies.isChecked()
                self.paper.rowSkip = self.rowSkip.value()
                self.paper.rowSkipAmount = self.rowSkipAmount.value()
                self.paper.columnSkip = self.columnSkip.value()
                self.paper.columnSkipAmount = self.columnSkipAmount.value()

                self.paper.update()
                self.paper.repeatPattern(self.pattern)

                return super().update()

            @pyqtSlot()
            def setDefaults(self):
                self.paper.overlap = (0, 0)
                self.paper.includeHalfsies = True
                self.paper.rowSkip = 0
                self.paper.rowSkipAmount = 0
                self.paper.columnSkip = 0
                self.paper.columnSkipAmount = 0

                self.xOffset.setSliderPosition(0)
                self.yOffset.setSliderPosition(0)

                self.includeHalfies.setChecked(True)

                self.rowSkip.setValue(0)
                self.rowSkipAmount.setValue(0)
                self.columnSkipAmount.setValue(0)
                self.columnSkip.setValue(0)


        if len(self.paper.boundsCircles) > 1:
            self.paper.bounds = getLargestRect(self.paper.boundsCircles)
            lines = self.paper.getLinesWithinRect(self.paper.bounds)
            halfLines = self.paper.getHalfLinesWithinRect(self.paper.bounds)

            # pattern = Pattern([Line(Pointi(100, 100), Pointi(20, 20), QColor('black'))], [], QRect(0, 0, 125, 125), DOTSPREAD)
            try:
                pattern = Pattern(lines, halfLines, self.paper.dotSpread)
            except UserWarning:
                return

            self.patternMenu = PatternMenu()
            self.patternMenu.pattern = pattern

            #* If you want to by default set the new color to black
            self.patternMenu.paper.currentDrawColor = QColor('black')

            patternSize = self.patternMenu.pattern.getRect(self.paper.dotSpread, self.paper.includeHalfsies).size()

            self.patternMenu.xOffset.setMinimum(-(patternSize.width() / self.paper.dotSpread) + 1)
            self.patternMenu.xOffset.setMaximum(  patternSize.width() / self.paper.dotSpread * MAX_SPREAD_MULTIPLIER)
            # self.patternMenu.xOffset.setSliderPosition(0)

            self.patternMenu.yOffset.setMinimum(-(patternSize.height() / self.paper.dotSpread) + 1)
            self.patternMenu.yOffset.setMaximum(  patternSize.height() / self.paper.dotSpread * MAX_SPREAD_MULTIPLIER)
            # self.patternMenu.yOffset.setSliderPosition(0)

            self.patternMenu.okCancel.accepted.connect(lambda: self.paper.repeatPattern(self.patternMenu.pattern))

            self.patternMenu.update()
            self.patternMenu.show()


    def controlsMenu(self):
        todo('controlsMenu')


    def aboutMenu(self):
        todo('aboutMenu')


    def creditsMenu(self):
        todo('creditsMenu')


    def licenseMenu(self):
        todo('licenseMenu')


    def donateMenu(self):
        todo('donateMenu')


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
