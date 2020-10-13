from Color import Color, namedColor
from Point import Point
from Pattern import Pattern
from Geometry import *
# from Gui import RepeatGui, menu
from Gui import MenuManager, menu
from Line import Line

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame, pygame_gui, pickle, sys
from PIL import Image, ImageDraw, ImageColor
import json

DIR = os.path.dirname(__file__) + '/../'
SAVES_FOLDER = DIR + 'saves/'

class Game:
    def __init__(self, winWidth = 485, winHeight = 300, title = 'Hello World!', args=None):
        with open(DIR + 'settings.json', 'r') as file:
            self.settings = json.load(file)

        self.args = args
        # print(self.args)

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
        pygame.display.set_caption(title)
        if pygame.__version__ >= '2.0.0':
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
        pygame.key.set_repeat(self.settings['keyRepeatDelay'], self.settings['keyRepeatInterval'])

        with open(DIR + 'data/' + self.settings['iconFile'], 'r') as icon:
            pygame.display.set_icon(pygame.image.load(icon))

        # Add SCALED back in when pygame gets updated to 2.0.0
        # pygame.OPENGL should also be in here, but it doesn't work for some reason.
        windowFlags = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE# | pygame.SCALED

        # TODO phase winWidth and winHeight out in favor of size
        self.winWidth  = winWidth
        self.winHeight = winHeight
        self.size = (winWidth, winHeight)

        #* Pygame data members
        self.mainSurface = pygame.display.set_mode([winWidth, winHeight], windowFlags)
        self.clock = pygame.time.Clock()

        #* Set up the GUIs
        self.openMenu = dict(zip(menu, [False] * len(menu)))

        self.offScreenAmount = self.settings['offScreenAmount'] * self.settings['dotSpread']
        self.metaLines = []
        self.startingPoint = Point(self.size[0] / 2, self.size[1] / 2)
        self.dots = genDotArrayPoints(self.size, self.settings['offScreenAmount'], self.settings['dotSpread'])
        self.mouseLoc = Point(*pygame.mouse.get_pos())
        self.focusLoc = Point()

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
        mirroringStates = [0, 2, 4]
        currentMirrorState = 0
        lineBuffer = []
        # The menu specific data each menu needs to work properly
        contexts = dict(zip(menu, [None] * len(menu)))
        boundsCircles = []
        dataFromGui = dict(zip(menu, [None] * len(menu)))

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
                for gui in list(self.openMenu):
                    if self.openMenu[gui]:
                        menuOpen = True

                #* Save the settings file if it changed 
                #! Debugging here
                if event.type != pygame.MOUSEMOTION:
                    # This seems like a good time to check if the settings have changed.
                    if self.settings != prevSettings:
                        print('Saving Settings')
                        with open(DIR + 'settings.json', 'w') as file:
                            json.dump(self.settings, file, sort_keys=True, indent=4, separators=(",", ": "))
                        
                        scaleLines_ip(self.lines, self.startingPoint,  prevSettings['dotSpread'], self.settings['dotSpread'])
                        scaleLines_ip(self.metaLines, self.startingPoint,  prevSettings['dotSpread'], self.settings['dotSpread'])
                        # print(self.lines[0])

                        prevSettings = {**self.settings}

                    # Debugging
                    if event.type is pygame.USEREVENT:
                        # print(event)
                        pass
                    # print(event)
                    # print('contexts:', contexts)
                    # print(self.focusLoc)

                #* Exit the window
                if event.type == pygame.QUIT: # or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)
                    self.exit()

                #* Reset ignoreMouse
                if ignoreMouse and event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION, pygame.USEREVENT]:
                    ignoreMouse = False
                    pygame.mouse.set_visible(True)
                    pygame.mouse.set_pos(self.focusLoc.data())
                
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
                    
                    #* Left mouse button clicked or space is pressed
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or \
                       (event.type == pygame.KEYDOWN and event.unicode == ' '):
                        if currentLine == None:
                            # print('current line is None, and im creating a new line at', self.focusLoc)
                            currentLine = Line(Point(*self.focusLoc.data()))
                        else:
                            # print('current line is not None, and im enting the current line at', self.focusLoc)
                            currentLine.finish(Point(*self.focusLoc.data()))
                            lineBuffer.append(currentLine)
                            currentLine = None

                    #* Right mouse button clicked or c is pressed
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3) or \
                       (event.type == pygame.KEYDOWN and event.key == pygame.K_c):
                        if currentLine == None:
                            currentLine = Line(Point(*self.focusLoc.data()))
                        else:
                            currentLine.finish(Point(*self.focusLoc.data()))
                            lineBuffer.append(currentLine)
                            currentLine = Line(Point(*self.focusLoc.data()))

                    #* Middle mouse butten clicked or q is pressed
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 2) or \
                       (event.type == pygame.KEYDOWN and event.key == pygame.K_q):

                        for index, i in enumerate(self.lines):
                            if i.start == self.focusLoc or i.end == self.focusLoc:
                                del self.lines[index]

                        for index, i in enumerate(boundsCircles):
                            if i == self.focusLoc:
                                del boundsCircles[index]

                        currentLine = None

                    #* Check for keys that only work outside of a menu
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
                        if event.unicode in ['S', '\x13']: #* ctrl + s
                            SAVES_FOLDER = DIR + 'saves/'
                            if fullscreen == True:
                                pygame.display.toggle_fullscreen()

                            filename = input("What would you like this pattern to be saved as?\n") + '.gdl'

                            if not filename.lower() in ['cancel.gdl', 'q.gdl', 'quit.gdl']:
                                if filename in os.listdir(SAVES_FOLDER):
                                    if input('That file already exists. Do you want to overwrite it? (y/n)\n').lower() == 'y':
                                        pickle.dump(self.lines, open(SAVES_FOLDER + filename, "wb" ))
                                        print('File Saved!')
                                else:
                                    pickle.dump(self.lines, open(SAVES_FOLDER + filename + '.gdl', "wb" ))
                                    print('File Saved!')
                            # ? if not self.menus['save'].isOpen:
                            # ?     self.menus['save'].isOpen = True
                            #     self.menus[menu.SAVE.value].open()
                            pass
                        if event.unicode in ['O', '\x0f']: #* ctrl + o
                            # pass
                            SAVES_FOLDER = DIR + 'saves/'
                            if fullscreen == True:
                                pygame.display.toggle_fullscreen()
                            # print(os.listdir(SAVES_FOLDER))
                            opts = dict(zip(range(1, len(os.listdir(SAVES_FOLDER)) + 1), os.listdir(SAVES_FOLDER)))
                            opts[0] = 'Cancel'
                            print(opts)
                            ans = int(input(f'Which file would you like to open? (0-{len(os.listdir(SAVES_FOLDER))})\n'))
                            if ans:
                                with open(SAVES_FOLDER + os.listdir(SAVES_FOLDER)[ans - 1], 'rb') as f:
                                    self.lines = pickle.load(f)
                            # self.lines = pickle.load(open(SAVES_FOLDER + os.listdir(SAVES_FOLDER)[int(input(f'Which file would you like to open? (0-{len(os.listdir(SAVES_FOLDER)) - 1})\n'))], 'rb'))
                        if event.unicode == 'Q':
                            self.lines = []
                            boundsCircles = []
                            lineBuffer = []
                            currentLine = None
                            for m in list(contexts):
                                contexts[m] = None
                            for g in self.openMenu:
                                g = False
                                
                        if event.key == 264 or event.key == pygame.K_HOME: # numpad up
                            self.settings['dotSpread'] += 1
                            self.dots = genDotArrayPoints(self.size, self.settings['offScreenAmount'], self.settings['dotSpread'])
                        if event.key == 258 or event.key == pygame.K_END: # numpad down
                            self.settings['dotSpread'] -= 1
                            self.dots = genDotArrayPoints(self.size, self.settings['offScreenAmount'], self.settings['dotSpread'])
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
                        if event.unicode in ['E', '\x05']: #* ctrl + e
                            image = Image.new('RGB', (self.winWidth, self.winHeight), color=tuple(self.settings['backgroundColor']))
                            draw = ImageDraw.Draw(image)
                            for line in self.lines:
                                draw.line(line.start.data() + line.end.data(), fill=line.color, width=self.settings['exportLineThickness'])
                            # draw.line((0, 0) + image.size, fill=128)
                            # draw.line((0, image.size[1], image.size[0], 0), fill=128)
                            SAVES_FOLDER = DIR + 'saves/'
                            SAVE_FILE = SAVES_FOLDER + 'testImage.png'
                            os.system('touch ' + SAVE_FILE)
                            image.save(SAVE_FILE)
                        if event.key == pygame.K_UP    or event.unicode == 'w':
                            self.focusLoc.y = self.focusLoc.y - self.settings['dotSpread']
                            if currentLine != None:
                                currentLine.end = self.focusLoc
                            ignoreMouse = True
                        if event.key == pygame.K_DOWN  or event.unicode == 's':
                            self.focusLoc.y = self.focusLoc.y + self.settings['dotSpread']
                            if currentLine != None:
                                currentLine.end = self.focusLoc
                            ignoreMouse = True
                        if event.key == pygame.K_LEFT  or event.unicode == 'a':
                            self.focusLoc.x = self.focusLoc.x - self.settings['dotSpread']
                            if currentLine != None:
                                currentLine.end = self.focusLoc
                            ignoreMouse = True
                        if event.key == pygame.K_RIGHT or event.unicode == 'd':
                            self.focusLoc.x = self.focusLoc.x + self.settings['dotSpread']
                            if currentLine != None:
                                currentLine.draw(self.mainSurface)
                                currentLine.end = self.focusLoc
                            ignoreMouse = True
                        if event.unicode == 'm':
                            mirrorLineColor = (87, 11, 13)
                            currentMirrorState += 1
                            if currentMirrorState >= len(mirroringStates):
                                currentMirrorState = 0
                                self.metaLines = []
                            
                            center = Point(min(self.dots, key=lambda i:abs(i.x - (self.winWidth / 2))).x + 1, min(self.dots, key=lambda i:abs(i.y - (self.winHeight / 2))).y + 1)

                            if mirroringStates[currentMirrorState] >= 2:
                                startv = Point(center.x, -self.offScreenAmount)
                                endv   = Point(center.x, self.winHeight + self.offScreenAmount)
                                self.metaLines.append(Line(startv, endv, mirrorLineColor))
                                
                                if mirroringStates[currentMirrorState] >= 4:
                                    starth = Point(-self.offScreenAmount, center.y)
                                    endh   = Point(self.winWidth + self.offScreenAmount, center.y)
                                    self.metaLines.append(Line(starth, endh, mirrorLineColor))
                        if event.unicode == 'b':
                            boundsCircles.append(self.focusLoc)


                #* Check for keys that also work inside a menu
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if menuOpen:
                            for m in self.openMenu:
                                self.openMenu[m] = False
                        else:
                            self.exit()
                    if event.unicode == 'f':
                            # Its better to call pygame.display.set_mode() with window flags to do this instead, because this will not work on windows.
                            pygame.display.toggle_fullscreen()
                            fullscreen = not fullscreen
                    if event.unicode == 'r':
                        if not menuOpen:
                            if len(boundsCircles) > 1:
                                bounds = getLargestRect(boundsCircles)
                                lines = self.getLinesWithinRect(bounds)

                                contexts[menu.REPEAT] = Pattern(lines[0], lines[1], bounds, self.settings['dotSpread'])

                                #* Uncomment this to manually repeat the pattern with given settings
                                    # self.lines = contexts[menu.REPEAT].repeat((self.winWidth + self.settings['dotSpread'], 
                                    #                                             self.winHeight + self.settings['dotSpread']), 
                                    #                                            self.offScreenAmount,
                                    #                                            startPoint=Point(0, 0) - self.offScreenAmount,
                                    #                                            dotSpread=self.settings['dotSpread'],
                                    #                                            overlap=[0, 0],
                                    #                                            halfsies=True
                                    #                                            )
                                    # boundsCircles = []
                                
                                self.openMenu[menu.REPEAT] = not self.openMenu[menu.REPEAT]
                    if event.unicode == 'o':
                        contexts[menu.OPTION] = self.settings
                        self.openMenu[menu.OPTION] = not self.openMenu[menu.OPTION]

                if menuOpen:
                    for i in list(self.openMenu):
                        if self.openMenu[i]:
                            self.openMenu[i] = menuManager.run(event, type=i)

                #* Add mirroring
                for i in lineBuffer:
                    if i.start != i.end:
                        self.lines.append(i)
                    if mirroringStates[currentMirrorState] >= 2:
                        center = Point(min(self.dots, key=lambda i:abs(i.x - (self.winWidth / 2))).x + 1, min(self.dots, key=lambda i:abs(i.y - (self.winHeight / 2))).y + 1)

                        startx = center.x + (center.x - i.start.x)
                        endx   = center.x + (center.x - i.end.x)
                        horStart = Point(startx, i.start.y)
                        horEnd   = Point(endx,   i.end.y)
                        self.lines.append(Line(horStart, horEnd, i.color))

                        if mirroringStates[currentMirrorState] >= 4:
                            starty = center.y + (center.y - i.start.y)
                            endy   = center.y + (center.y - i.end.y)
                            vertStart = Point(i.start.x, starty)
                            vertEnd   = Point(i.end.x,   endy)
                            self.lines.append(Line(vertStart, vertEnd, i.color))

                            corStart = Point(startx, starty)
                            corEnd   = Point(endx,   endy)
                            self.lines.append(Line(corStart, corEnd, i.color))

                lineBuffer = []

            #* Add mirrored current line
            if currentLine is not None and mirroringStates[currentMirrorState] >= 2:
                curStartx = center.x + (center.x - currentLine.start.x)
                curEndx   = center.x + (center.x - currentLine.end.x)
                Line(Point(curStartx, currentLine.start.y), Point(curEndx, currentLine.end.y), currentLine.color).draw(self.mainSurface)

                if mirroringStates[currentMirrorState] >= 4:
                    curStarty = center.y + (center.y - currentLine.start.y)
                    curEndy   = center.y + (center.y - currentLine.end.y)
                    Line(Point(currentLine.start.x, curStarty), Point(currentLine.end.x, curEndy), currentLine.color).draw(self.mainSurface)

                    Line(Point(curStartx, curStarty), Point(curEndx, curEndy), currentLine.color).draw(self.mainSurface)

            if not menuOpen:
                self.drawFocus()
                if currentLine != None: currentLine.draw(self.mainSurface)

            self.drawDots()
            self.drawLines()

            if menuOpen:
                for m in list(self.openMenu):
                    if self.openMenu[m]:
                        dataFromGui = menuManager.draw(deltaTime, m, context=contexts[m])
                    else:
                        contexts[m] = None

            #* If there's a pattern, and we haven't repeated it yet
            if dataFromGui[menu.REPEAT] is not None:
                #* First close the repeat menu
                self.openMenu[menu.REPEAT] = False

                #* Find the top left most point
                startPoint = Point(min(self.dots, key=lambda i: i.x).x,
                                   min(self.dots, key=lambda i: i.y).y)

                #* Repeat the pattern and add the lines to self.lines
                self.lines = dataFromGui[menu.REPEAT].repeat((self.winWidth + self.settings['dotSpread'], 
                                                               self.winHeight + self.settings['dotSpread']),
                                                              offScreenAmount=self.offScreenAmount,
                                                              startPoint=startPoint,
                                                            #   startPoint=self.startingPoint,
                                                              dotSpread=self.settings['dotSpread']
                                                              )

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
                self.dots = genDotArrayPoints(self.size, self.settings['offScreenAmount'], self.settings['dotSpread'])
                dataFromGui[menu.OPTION] = None


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