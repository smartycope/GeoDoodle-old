from menu import menu
from Point import Point
from Pattern import Pattern
from Geometry import *
# from Gui import RepeatGui, menu
from Gui import MenuManager, menu
from Line import Line

from tkinter import filedialog
from tkinter import *

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame, pygame_gui, pickle, sys
from PIL import Image, ImageDraw, ImageColor
import json

import os; DIR = os.path.dirname(os.path.dirname(__file__)); DIR += '\\main\\' if os.name == 'nt' else '/'
SAVES_FOLDER = DIR + 'saves'
DOT_SPREAD_LIMIT = 12
MIRROR_LINE_COLOR = (87, 11, 13)

class Game:
    def __init__(self, size = [None, None], title = 'Hello World!', args=None):
        with open(DIR + 'settings.jsonc', 'r') as file:
            self.settings = json.load(file)

        # with open(DIR + 'colors.jsonc', 'r') as file:
        #     self.settings['toolbarColors'] = json.load(file)

        self.currentDrawColor = self.settings['toolbarColors'][0]

        self.args = args

        #* If there's a specified file in the command line arguments, open it and put it in lines
        if self.args is not None and self.args.open is not None:
            try:
                print('Opening pattern')
                with open(self.args.open, 'rb') as f:
                    self.lines = pickle.load(f)
            except FileNotFoundError:
                print('Can\'t open file.')
                exit(0)
        else:
            self.lines = []


        #* Initialize Pygame
        pygame.init()

        tmp = pygame.display.Info()
        self.screenSize = (tmp.current_w, tmp.current_h)

        with open(DIR + 'data/' + self.settings['iconFile'], 'r') as icon:
            pygame.display.set_icon(pygame.image.load(icon))

        pygame.key.set_repeat(self.settings['keyRepeatDelay'], self.settings['keyRepeatInterval'])
        pygame.display.set_caption(title)

        self.fullscreenWindowFlags = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.FULLSCREEN | pygame.NOFRAME
        self.windowedWindowFlags   = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE

        if pygame.__version__ >= '2.0.0':
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
            pygame.display.set_allow_screensaver(True)
            self.windowedWindowFlags = self.windowedWindowFlags | pygame.SCALED

        # Add SCALED back in when pygame gets updated to 2.0.0
        # pygame.OPENGL should also be in here, but it doesn't work for some reason.

        self.windowedSize = size
        if size[0] is None:
            self.windowedSize[0] = round(self.screenSize[0] / 1.5)
        if size[1] is None:
            self.windowedSize[1] = round(self.screenSize[1] / 1.5)

        #* Pygame data members
        if args.fullscreen:
            self.mainSurface = pygame.display.set_mode(self.screenSize, self.fullscreenWindowFlags)
        else:
            self.mainSurface = pygame.display.set_mode(self.windowedSize, self.windowedWindowFlags)
        
        self.clock = pygame.time.Clock()

        #* Set up the GUIs
        self.openMenu = dict(zip(menu, [False] * len(menu)))

        self.offScreenAmount = self.settings['offScreenAmount'] * self.settings['dotSpread']
        self.metaLines = []
        self.startingPoint = Point(self.getSize()[0] / 2, self.getSize()[1] / 2)
        self.dots = genDotArrayPoints(self.getSize(), self.settings['offScreenAmount'], self.settings['dotSpread'])
        self.mouseLoc = Point(*pygame.mouse.get_pos())
        self.focusLoc = Point()

        vidInfo = pygame.display.Info()

        if self.args.verbose:
            print('Backend video driver being used:', pygame.display.get_driver())
            print('The display is', 'not' if not vidInfo.hw else '', 'hardware accelerated')
            print('The display has', vidInfo.video_mem, 'MB of video memory')
            print('The current width and height of the window are:', (vidInfo.current_w, vidInfo.current_h))
            print('The width and height of the display is:', self.screenSize)

    def getSize(self):
        #* This won't work until pygame 2.0.0
        # return pygame.display.get_window_size()
        tmp = pygame.display.Info()
        return [tmp.current_w, tmp.current_h]

    def drawLines(self):
        for line in self.lines:
            line.draw(self.mainSurface)
        for line in self.metaLines:
            line.draw(self.mainSurface)

    def drawDots(self):
        for i in self.dots:
            pygame.draw.rect(self.mainSurface, self.settings['dotColor'], pygame.Rect(i.data(), [self.settings['dotSize'], self.settings['dotSize']]))

    def drawFocus(self):
        pygame.draw.circle(self.mainSurface, self.settings['focusColor'], self.focusLoc.data(), self.settings['focusRadius'], 1)

    def updateMouse(self):
        self.mouseLoc = Point(*pygame.mouse.get_pos())

    def updateFocus(self):
        self.focusLoc = Point(min(self.dots, key=lambda i:abs(i.x - self.mouseLoc.x)).x + 1, min(self.dots, key=lambda i:abs(i.y - self.mouseLoc.y)).y + 1)

    def resetSettings(self, prevSettings):
        pygame.key.set_repeat(self.settings['keyRepeatDelay'], self.settings['keyRepeatInterval'])
        scaleLines_ip(self.lines, self.startingPoint,  prevSettings['dotSpread'], self.settings['dotSpread'])
        scaleLines_ip(self.metaLines, self.startingPoint,  prevSettings['dotSpread'], self.settings['dotSpread'])

    def getLinesWithinRect(self, bounds):
        ''' bounds is a pygame.Rect '''

        patternLines = []
        halfLines = []
        patternLineIndecies = []
        halfLineIndecies = []

        #* Because the collidePoint function returns True if a line is touching 
        #*  the left or top, but not the bottom or right, we have to inflate the
        #*  rectangle and then move it so it's positioned correctly
        incBounds = bounds.inflate(self.settings['dotSpread'], self.settings['dotSpread'])
        incBounds.move_ip(self.settings['dotSpread'] / 2, self.settings['dotSpread'] / 2)

        #* Get all the lines that are in the incBounds, and the halfway in lines seperately
        for index, l in enumerate(self.lines):
            if incBounds.collidepoint(l.start.data()) and incBounds.collidepoint(l.end.data()):
                patternLines.append(l)
                patternLineIndecies.append(index)
            elif incBounds.collidepoint(l.start.data()) or incBounds.collidepoint(l.end.data()):
                halfLines.append(l)
                halfLineIndecies.append(index)

        return [patternLines, halfLines, patternLineIndecies, halfLineIndecies]

    def run(self):
        run = True
        currentLine = None
        dragging = 0
        specificErase = None
        ignoreMouse = False
        fullscreen = False
        menuOpen = False
        prevSettings = {**self.settings}
        menuManager = MenuManager(self.mainSurface)
        mirroringStates = [0, 1, 2, 4] # 1 is horizontal line only
        currentMirrorState = 0
        lineBuffer = []
        # The menu specific data each menu needs to work properly
        contexts = dict(zip(menu, [None] * len(menu)))
        boundsCircles = []
        dataFromGui = dict(zip(menu, [None] * len(menu)))
        mouseOverToolbar = False

        while run:
            deltaTime = self.clock.tick(self.settings['FPS']) / 1000.0

            if not ignoreMouse:
                self.updateMouse()
                self.updateFocus()
            else:
                pygame.mouse.set_visible(False)

            #* Draw the bounds
            for i in boundsCircles:
                pygame.draw.circle(self.mainSurface, self.settings['boundsCircleColor'], i.data(), self.settings['focusRadius'], 1)
                if len(boundsCircles) > 1:
                    bounds = getLargestRect(boundsCircles)                    
                    drawRect(self.mainSurface, bounds, self.settings['boundsLineColor'])

            for event in pygame.event.get():

                #* Check if any menus are open
                menuOpen = False
                tmp = list(self.openMenu)
                tmp.remove(menu.TOOLBAR)
                for gui in tmp:
                    if self.openMenu[gui]:
                        menuOpen = True

                #* Save the settings file if it changed
                #! Debugging here
                if event.type != pygame.MOUSEMOTION:
                    # This seems like a good time to check if the settings have changed.
                    if self.settings != prevSettings:
                        if self.settings['dotSpread'] < DOT_SPREAD_LIMIT:
                            self.settings['dotSpread'] = DOT_SPREAD_LIMIT

                        print('Saving Settings')
                        with open(DIR + 'settings.jsonc', 'w') as file:
                            json.dump(self.settings, file, sort_keys=True, indent=4, separators=(",", ": "))
                        
                        self.resetSettings(prevSettings)
                        # print(self.lines[0])

                        prevSettings = {**self.settings}

                    # Debugging
                    if event.type is pygame.USEREVENT:
                        # print(event)
                        pass
                    # print(event)

                #* Exit the window
                if event.type == pygame.QUIT: # or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)
                    self.exit()

                #* Reset ignoreMouse
                if ignoreMouse and event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION, pygame.USEREVENT]:
                    ignoreMouse = False
                    pygame.mouse.set_visible(True)
                    pygame.mouse.set_pos(self.focusLoc.data())
                
                #* Check to see if the mouse is over the toolbar buttons
                if event.type == pygame.USEREVENT:

                    if menuManager.toolbar is not None:
                        if event.user_type == pygame_gui.UI_BUTTON_ON_HOVERED and \
                           event.ui_element in menuManager.toolbar.buttons:

                            mouseOverToolbar = True

                        if (event.user_type == pygame_gui.UI_BUTTON_ON_UNHOVERED and \
                            event.ui_element in menuManager.toolbar.buttons) or \
                            event.user_type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:

                            mouseOverToolbar = False
                    else:
                        mouseOverToolbar = False

                if not menuOpen:

                    #* Mouse moves
                    if event.type == pygame.MOUSEMOTION:
                        if currentLine != None:
                            currentLine.end = self.focusLoc
                            if event.buttons[0]:
                                dragging += 1

                    #* If the left mouse button is released after being dragged
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging > self.settings['dragDelay']:
                        dragging = 0
                        currentLine.finish(self.focusLoc)
                        lineBuffer.append(currentLine)
                        currentLine = None
                    
                    if not mouseOverToolbar:
                        #* Left mouse button clicked or space is pressed
                        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or \
                           (event.type == pygame.KEYDOWN and event.unicode == ' '):
                            if currentLine == None:
                                # print('current line is None, and im creating a new line at', self.focusLoc)
                                currentLine = Line(Point(self.focusLoc), color=self.currentDrawColor)
                            else:
                                # print('current line is not None, and im enting the current line at', self.focusLoc)
                                currentLine.finish(Point(self.focusLoc))
                                lineBuffer.append(currentLine)
                                currentLine = None

                        #* Right mouse button clicked or c is pressed
                        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3) or \
                           (event.type == pygame.KEYDOWN and event.key == pygame.K_c):
                            if currentLine == None:
                                currentLine = Line(Point(self.focusLoc), color=self.currentDrawColor)
                            else:
                                currentLine.finish(Point(self.focusLoc))
                                lineBuffer.append(currentLine)
                                currentLine = Line(Point(self.focusLoc), color=self.currentDrawColor)

                        #* Middle mouse button clicked or q is pressed
                        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 2) or \
                           (event.type == pygame.KEYDOWN and event.key == pygame.K_q):

                            #* This should not be nessicarry, I have no idea why the 3 lines don't work by themselves.
                            linesStillAtFocus = True
                            while linesStillAtFocus:
                                linesStillAtFocus = False

                                for i in self.lines:
                                    if i.start == self.focusLoc or i.end == self.focusLoc:
                                        self.lines.remove(i)

                                for i in self.lines:
                                    if i.start == self.focusLoc or i.end == self.focusLoc:
                                        linesStillAtFocus = True

                            for i in boundsCircles:
                                if i == self.focusLoc:
                                    boundsCircles.remove(i)

                            currentLine = None

                    #* Open a file if it's dropped into the main area
                    if event.type == pygame.DROPFILE and event.file[-4:0] == '.gdl':
                        with open(event.file, 'r') as f:
                            self.lines = pickle.load(f)

                    #* If you scroll up
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
                        pass

                    #* If you scroll down
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
                        pass

                    #* If you scroll up and press shift
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        # I don't feel like adding a seperate currentDrawColorIndex member variable.
                        self.currentDrawColor = self.settings['toolbarColors'][self.settings['toolbarColors'].index(self.currentDrawColor) + 1]
                        if currentLine is not None: currentLine.color = self.currentDrawColor

                    #* If you scroll down and press shift
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.currentDrawColor = self.settings['toolbarColors'][self.settings['toolbarColors'].index(self.currentDrawColor) - 1]
                        if currentLine is not None: currentLine.color = self.currentDrawColor

                    #* Check for keys that only work outside of a menu
                    #? Keys here
                    if event.type == pygame.KEYDOWN:
                        if event.unicode == 'u' or event.unicode == '\x1a': # ctrl + z
                            if currentLine == None and len(self.lines) > 0:
                                del self.lines[-1]
                                if mirroringStates[currentMirrorState] >= 2 and len(self.lines) > 0:
                                    self.lines.pop()
                                    if mirroringStates[currentMirrorState] >= 4 and len(self.lines) > 0:
                                        self.lines.pop()
                                        if len(self.lines) > 1:
                                            self.lines.pop()
                            elif currentLine != None:
                                currentLine = None
                        if event.unicode == 'Q':
                            self.lines = []
                            boundsCircles = []
                            lineBuffer = []
                            currentLine = None
                            tmp = list(contexts)
                            tmp.remove(menu.TOOLBAR)
                            for m in tmp:
                                contexts[m] = None
                            for g in self.openMenu:
                                g = False
                        if event.key == 264 or event.key == pygame.K_HOME: # numpad up
                            self.settings['dotSpread'] += 1
                            self.dots = genDotArrayPoints(self.getSize(), self.settings['offScreenAmount'], self.settings['dotSpread'])
                        if event.key == 258 or event.key == pygame.K_END: # numpad down
                            self.settings['dotSpread'] -= 1
                            self.dots = genDotArrayPoints(self.getSize(), self.settings['offScreenAmount'], self.settings['dotSpread'])
                        if event.unicode == 'e':
                            # If there's nothing there, don't do anything
                            if self.focusLoc in [i.end for i in self.lines] + [i.start for i in self.lines]:
                                if specificErase == None:
                                    specificErase = self.focusLoc
                                else:
                                    assert(type(specificErase) == Point)
                                    for index, i in enumerate(self.lines):
                                        if (i.start == self.focusLoc and i.end == specificErase) or \
                                        (i.start == specificErase and i.end == self.focusLoc):
                                            del self.lines[index]
                                    specificErase = None
                            else:
                                specificErase = None
                        if event.key == pygame.K_UP    or event.unicode == 'w':
                            self.focusLoc.y -= self.settings['dotSpread']
                            if currentLine != None:
                                currentLine.end = self.focusLoc
                            ignoreMouse = True
                        if event.key == pygame.K_DOWN  or event.unicode == 's':
                            self.focusLoc.y += self.settings['dotSpread']
                            if currentLine != None:
                                currentLine.end = self.focusLoc
                            ignoreMouse = True
                        if event.key == pygame.K_LEFT  or event.unicode == 'a':
                            self.focusLoc.x -= self.settings['dotSpread']
                            if currentLine != None:
                                currentLine.end = self.focusLoc
                            ignoreMouse = True
                        if event.key == pygame.K_RIGHT or event.unicode == 'd':
                            self.focusLoc.x += self.settings['dotSpread']
                            if currentLine != None:
                                currentLine.draw(self.mainSurface)
                                currentLine.end = self.focusLoc
                            ignoreMouse = True
                        if event.unicode == 'm':
                            self.metaLines = []

                            currentMirrorState += 1
                            if currentMirrorState >= len(mirroringStates):
                                currentMirrorState = 0

                            # print(mirroringStates[currentMirrorState])
                                
                            if mirroringStates[currentMirrorState] in [1, 4]:
                                starth = Point(-self.offScreenAmount, self.startingPoint.y)
                                endh   = Point(self.getSize()[0] + self.offScreenAmount, self.startingPoint.y)
                                self.metaLines.append(Line(starth, endh, MIRROR_LINE_COLOR))

                            if mirroringStates[currentMirrorState] >= 2:
                                startv = Point(self.startingPoint.x, -self.offScreenAmount)
                                endv   = Point(self.startingPoint.x, self.getSize()[1] + self.offScreenAmount)
                                self.metaLines.append(Line(startv, endv, MIRROR_LINE_COLOR))
                        if event.unicode == 'b':
                            boundsCircles.append(Point(self.focusLoc))
                        if event.unicode.isnumeric():
                            self.currentDrawColor = self.settings['toolbarColors'][int(event.unicode) - 1]
                        if event.unicode == 'f':
                            # pygame.display.toggle_fullscreen()

                            if not fullscreen:
                                self.mainSurface = pygame.display.set_mode(self.screenSize, self.fullscreenWindowFlags)
                                self.startingPoint = Point(self.screenSize) / 2
                                self.dots = genDotArrayPoints(self.screenSize, self.settings['offScreenAmount'], self.settings['dotSpread'])
                            else:
                                self.mainSurface = pygame.display.set_mode(self.windowedSize, self.windowedWindowFlags)
                                self.startingPoint = Point(self.windowedSize) / 2
                                self.dots = genDotArrayPoints(self.windowedSize, self.settings['offScreenAmount'], self.settings['dotSpread'])

                            fullscreen = not fullscreen
                        if event.unicode in ['S', '\x13'] or (event.key == 115 and event.mod == 64): #* ctrl + s
                            if fullscreen:
                                self.mainSurface = pygame.display.set_mode(self.windowedSize, self.windowedWindowFlags)
                                self.startingPoint = Point(self.windowedSize) / 2
                                self.dots = genDotArrayPoints(self.windowedSize, self.settings['offScreenAmount'], self.settings['dotSpread'])
                                self.mainSurface.fill(self.settings['backgroundColor'])
                                self.drawDots()
                                self.drawLines()
                                pygame.display.flip()
                                pygame.display.update()

                            root = Tk()
                            filename = filedialog.asksaveasfilename(initialdir=self.settings['savesLoc'], 
                                                                    title="Save File",
                                                                    filetypes=(("GeoDoodle Saves","*.gdl"),),
                                                                    parent=root)

                            if '.' not in filename:
                                filename += '.gdl'

                            if len(filename) > 4:
                                with open(filename, 'wb') as f:
                                    pickle.dump(self.lines, f)
                                print('File Saved!')
                            root.destroy()
                        if event.unicode in ['O', '\x0f'] or (event.key == 111 and event.mod == 64): #* ctrl + o
                            if fullscreen:
                                self.mainSurface = pygame.display.set_mode(self.windowedSize, self.windowedWindowFlags)
                                self.startingPoint = Point(self.windowedSize) / 2
                                self.dots = genDotArrayPoints(self.windowedSize, self.settings['offScreenAmount'], self.settings['dotSpread'])
                                self.mainSurface.fill(self.settings['backgroundColor'])
                                self.drawDots()
                                self.drawLines()
                                pygame.display.flip()
                                pygame.display.update()

                            root = Tk()
                            filename = filedialog.askopenfilename(initialdir=self.settings['savesLoc'],
                                                                  title="Open File",
                                                                  filetypes=(("GeoDoodle Saves","*.gdl"),
                                                                             ('Any File',       '*.*') ),
                                                                  parent = root)
                            # print(filename)
                            if '.' not in filename:
                                filename += '.gdl'

                            if len(filename) > 4:
                                with open(filename, 'rb') as f:
                                    self.lines = pickle.load(f)
                            root.destroy()
                        if event.unicode in ['E', '\x05'] or (event.key == 101 and event.mod == 64): #* ctrl + e
                            if fullscreen:
                                self.mainSurface = pygame.display.set_mode(self.windowedSize, self.windowedWindowFlags)
                                self.startingPoint = Point(self.windowedSize) / 2
                                self.dots = genDotArrayPoints(self.windowedSize, self.settings['offScreenAmount'], self.settings['dotSpread'])
                                self.mainSurface.fill(self.settings['backgroundColor'])
                                self.drawDots()
                                self.drawLines()
                                pygame.display.flip()
                                pygame.display.update()

                            image = Image.new('RGB', self.getSize(), color=tuple(self.settings['backgroundColor']))
                            draw = ImageDraw.Draw(image)
                            for line in self.lines:
                                draw.line(line.start.data() + line.end.data(), fill=tuple(line.color), width=self.settings['exportLineThickness'])
                            # draw.line((0, 0) + image.size, fill=128)
                            # draw.line((0, image.size[1], image.size[0], 0), fill=128)
                            root = Tk()

                            filename = filedialog.asksaveasfilename(initialdir=self.settings['imageSavesLoc'],
                                                                    title="Export File",
                                                                    filetypes=(("PNG Image", '*.png'),
                                                                            ('JPEG Image', '*.jpg'),
                                                                            ('JPEG Image', '*.jpeg'),
                                                                            ('Any File', '*.*')),
                                                                    parent=root)
                            
                            if '.' not in filename:
                                filename += '.gdl'
                                
                            if len(filename) > 4:
                                image.save(filename)
                            print('File Saved!')
                            root.destroy()

                #* Check for keys that also work inside a menu
                #? Keys here
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if menuOpen:
                            for m in self.openMenu:
                                self.openMenu[m] = False
                        else:
                            self.exit()
                    if event.unicode == 'r':
                        if not menuOpen:
                            if len(boundsCircles) > 1:
                                bounds = getLargestRect(boundsCircles)
                                lines = self.getLinesWithinRect(bounds)

                                contexts[menu.REPEAT] = Pattern(lines[0], lines[1], bounds, self.settings['dotSpread'])

                                # self.lines += contexts[menu.REPEAT].getPatternAtLoc(Point(50, 50), scale=self.settings['dotSpread'])

                                #* Uncomment this to manually repeat the pattern with given settings
                                # self.lines = contexts[menu.REPEAT].repeat((self.screenSize[0] + self.settings['dotSpread'], 
                                #                                            self.screenSize[1] + self.settings['dotSpread']),
                                #                                            offScreenAmount=self.offScreenAmount,
                                #                                            startPoint=self.startingPoint % self.settings['dotSpread'],
                                #                                            dotSpread=self.settings['dotSpread'],
                                #                                            overlap=[0, 0],
                                #                                            halfsies=True
                                #                                            )

                                # boundsCircles = []
                                
                                self.openMenu[menu.REPEAT] = not self.openMenu[menu.REPEAT]
                    if event.unicode == 'o':
                        contexts[menu.OPTION] = self.settings
                        self.openMenu[menu.OPTION] = not self.openMenu[menu.OPTION]
                    if event.unicode == 't':
                        contexts[menu.TOOLBAR] = self.settings['toolbarColors'] + [self.settings['toolbarColors'].index(self.currentDrawColor)]
                        self.openMenu[menu.TOOLBAR] = not self.openMenu[menu.TOOLBAR]
                    

                if menuOpen or self.openMenu[menu.TOOLBAR]:
                    for i in list(self.openMenu):
                        if self.openMenu[i]:
                            if i == menu.TOOLBAR:
                                menuManager.handleInput(event, type=i)
                            else:
                                self.openMenu[i] = menuManager.handleInput(event, type=i)

                #* Add mirroring
                for i in lineBuffer:
                    #* Check if there's already a line there (so it doesn't get bolder (because of anti-aliasing))
                    dontDraw = False
                    for k in self.lines:
                        if i == k or (i.start == k.end and i.end == k.start):
                            dontDraw = True

                    #* Check if the start and end are the same (no line would be drawn)
                    if i.start != i.end and not dontDraw:
                        self.lines.append(i)

                    if mirroringStates[currentMirrorState] in [1, 4]:
                        starty = self.startingPoint.y + (self.startingPoint.y - i.start.y) + 2
                        endy   = self.startingPoint.y + (self.startingPoint.y - i.end.y) + 2
                        vertStart = Point(i.start.x, starty)
                        vertEnd   = Point(i.end.x,   endy)
                        self.lines.append(Line(vertStart, vertEnd, i.color))


                    if mirroringStates[currentMirrorState] >= 2:
                        # self.startingPoint = Point(min(self.dots, key=lambda i:abs(i.x - (self.getSize()[0] / 2))).x + 1, min(self.dots, key=lambda i:abs(i.y - (self.getSize()[1] / 2))).y + 1)

                        startx = self.startingPoint.x + (self.startingPoint.x - i.start.x) + 2
                        endx   = self.startingPoint.x + (self.startingPoint.x - i.end.x) + 2
                        horStart = Point(startx, i.start.y)
                        horEnd   = Point(endx,   i.end.y)
                        self.lines.append(Line(horStart, horEnd, i.color))

                        if mirroringStates[currentMirrorState] >= 4:
                            corStart = Point(startx, starty)
                            corEnd   = Point(endx,   endy)
                            self.lines.append(Line(corStart, corEnd, i.color))

                lineBuffer = []

            #* Add mirrored current line
            if currentLine is not None and mirroringStates[currentMirrorState] in [1, 4]:
                curStarty = self.startingPoint.y + (self.startingPoint.y - currentLine.start.y) + 2
                curEndy   = self.startingPoint.y + (self.startingPoint.y - currentLine.end.y) + 2
                Line(Point(currentLine.start.x, curStarty), Point(currentLine.end.x, curEndy), currentLine.color).draw(self.mainSurface)

            if currentLine is not None and mirroringStates[currentMirrorState] >= 2:
                curStartx = self.startingPoint.x + (self.startingPoint.x - currentLine.start.x) + 2
                curEndx   = self.startingPoint.x + (self.startingPoint.x - currentLine.end.x) + 2
                Line(Point(curStartx, currentLine.start.y), Point(curEndx, currentLine.end.y), currentLine.color).draw(self.mainSurface)

                if currentLine is not None and mirroringStates[currentMirrorState] >= 4:
                    Line(Point(curStartx, curStarty), Point(curEndx, curEndy), currentLine.color).draw(self.mainSurface)

            #* Draw the focus and the current line
            if not menuOpen:
                self.drawFocus()
                if currentLine != None: currentLine.draw(self.mainSurface)

            self.drawDots()
            self.drawLines()

            if menuOpen or self.openMenu[menu.TOOLBAR]:
                for m in list(self.openMenu):
                    if self.openMenu[m]:
                        dataFromGui = menuManager.draw(deltaTime, m, context=contexts[m])
                    else:
                        contexts[m] = None

            #* We don't want to have to wait till we call draw again to kill the current not-supposed-to-be-open window
            for m in menu:
                if not self.openMenu[m]:
                    menuManager.killWindow(m)

            #* If there's a pattern, and we haven't repeated it yet
            if dataFromGui[menu.REPEAT] is not None:
                #* First close the repeat menu
                self.openMenu[menu.REPEAT] = False

                #* Find the top left most point
                # startPoint = Point(min(self.dots, key=lambda i: i.x).x,
                                #    min(self.dots, key=lambda i: i.y).y)

                #* Repeat the pattern and add the lines to self.lines
                self.lines = dataFromGui[menu.REPEAT].repeat((self.screenSize[0] + self.settings['dotSpread'], 
                                                              self.screenSize[1] + self.settings['dotSpread']), 
                                                              offScreenAmount=self.offScreenAmount,
                                                              startPoint=self.startingPoint % self.settings['dotSpread'],
                                                              dotSpread=self.settings['dotSpread'])

                #* Get rid of the lines inside the box
                # bounds = getLargestRect(boundsCircles)
                # for l in self.getLinesWithinRect(bounds)[2]:
                #     del self.lines[l]
                
                # if dataFromGui[menu.REPEAT].halfsies:
                #     for l in self.getLinesWithinRect(bounds)[3]:
                #         del self.lines[l]

                #* Get rid of the bounds box and circles, we don't need them anymore
                boundsCircles = []

                #* We only want to run this once
                dataFromGui[menu.REPEAT] = None

            #* If we've recived data from the options menu, and we haven't done anything with it yet
            if dataFromGui[menu.OPTION] is not None:
                self.openMenu[menu.OPTION] = False
                self.settings = dataFromGui[menu.OPTION]
                self.dots = genDotArrayPoints(self.getSize(), self.settings['offScreenAmount'], self.settings['dotSpread'])
                dataFromGui[menu.OPTION] = None

            #* If we've just recived color and selection data from the toolbar
            if dataFromGui[menu.TOOLBAR] is not None:
                self.settings['toolbarColors'] = dataFromGui[menu.TOOLBAR][:-1]
                # print(self.settings['toolbarColors'])
                self.currentDrawColor = self.settings['toolbarColors'][dataFromGui[menu.TOOLBAR][-1]]
                contexts[menu.TOOLBAR] = dataFromGui[menu.TOOLBAR]
                dataFromGui[menu.TOOLBAR] = None

            # if dataFromGui[menu.SAVE] is not None:
            #     self.openMenu[menu.SAVE] = False
            #     with open(dataFromGui[menu.Save], 'wb') as f:
            #         pickle.dump(self.lines, f)
            #     print('File Saved!')
            #     dataFromGui[menu.SAVE] = None

            pygame.display.flip()
            pygame.display.update()
            self.mainSurface.fill(self.settings['backgroundColor'])

    def exit(self):
        pygame.quit()
        quit()


'''
    def text_objects(self, text, font):
        textSurface = font.render(text, True, namedColor('black').color)
        return textSurface, textSurface.get_rect()

    def message_display(self, text):
        largeText = pygame.font.Font('freesansbold.ttf', 115)
        TextSurf, TextRect = self.text_objects(text, largeText)
        TextRect.center = ((display_width / 2),(display_height / 2))
        self.mainSurface.blit(TextSurf, TextRect)

        pygame.display.update()
        # time.sleep(2)
        self.run()
'''