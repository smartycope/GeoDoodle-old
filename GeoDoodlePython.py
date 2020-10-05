import pygame, os, pickle
from collections import namedtuple

#* THINGS TO ADD
# fix the q/middle click bug
# add repeating

# Fix this bug:
# Traceback (most recent call last):
#   File "/home/skipper/hello/Python/GeoDoodle/GeoDoodlePython.py", line 263, in <module>
#     game = Game(1366, 768, 'GeoDoodle')
#   File "/home/skipper/hello/Python/GeoDoodle/GeoDoodlePython.py", line 157, in run
#     dragging = 0
# AttributeError: 'NoneType' object has no attribute 'finish'

# add fancy repeating (with a menu)
# add save overwrite checking
# maybe add a failsafe in case it's fullscreen and everythings stopped
# make shift home/end jump more
# add icon
# add mirroring (2x, 4, 6x, 8x...)
# have lines scale with dotSpread
# export to image
# add settings menu gui
# add half spacing with arrow keys
# add mouse hiding
# add an algorithm that randomly generates patterns
# c + arrow keys is broken
# add a redo function, and have it include erasing an entire pattern
# add the ability to, when you push a button, end a line along another line, and have the focus reflect that
# add colors (attached to keys? make a toolbar?)
# s is attached to save AND down
# add sharing?

os.system('clear')

dir = os.path.dirname(__file__) + '/'
savesFolder = dir + 'GeoDoodle Saves/'

# Point = namedtuple('Point', ['x', 'y'])

FOCUS_RADIUS = 6
DRAG_DELAY   = 12
FPS          = 30
KEY_REPEAT_DELAY    = 200
KEY_REPEAT_INTERVAL = 20

class Point:
    def __init__(self, x = -1, y = -1):
        self.x = int(x)
        self.y = int(y)
    def __eq__(self, a):
        try:
            return self.x == a.x and self.y == a.y
        except:
            return False
    def __str__(self):
        return f'({self.x}, {self.y})'

    def data(self):
        return [self.x, self.y]

class Color:
    def __init__(self, r = 0, g = 0, b = 0, a = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.color = [self.r, self.g, self.b, self.a]
    
def namedColor(color):
    color = color.lower()
    if color == 'red':
        return Color(255, 0, 0)
    if color == 'blue':
        return Color(0, 0, 255)
    if color == 'green':
        return Color(0, 255, 0)
    if color == 'white':
        return Color(255, 255, 255)
    if color == 'black':
        return Color()
    if color == 'paper':
        return Color(200, 160, 100)

class Line:
    def __init__(self, start, end = None):
        self.start = start
        if end == None:
            self.end = start
        else:
            self.end = end
        self.color = namedColor('black')

    def finish(self, loc):
        self.end = loc

    def isFinished(self):
        return self.end != None

    def draw(self, display):
        pygame.draw.aaline(display, self.color.color, self.start.data(), self.end.data())

class Game:
    def __init__(self, winWidth = 485, winHeight = 300, title = 'Hello World!'):
        pygame.init()
        pygame.display.set_caption(title)
        pygame.key.set_repeat(KEY_REPEAT_DELAY, KEY_REPEAT_INTERVAL)
        # pygame.display.set_icon(Surface)
        #* Add SCALED back in when pygame gets updated to 2.0.0
        # pygame.OPENGL should also be in here, but it doesn't work for some reason.
        windowFlags = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE# | pygame.SCALED
        self.gameDisplay = pygame.display.set_mode([winWidth, winHeight], windowFlags)
        self.clock = pygame.time.Clock()
        self.lines = list()
        self.background = namedColor('paper')
        self.winWidth   = winWidth
        self.winHeight  = winHeight
        self.mouseLoc   = Point(*pygame.mouse.get_pos())
        self.focusLoc   = Point()
        self.focusColor = namedColor('blue')
        self.fps = FPS
        self.dotSpread = 25
        self.offScreenAmount = 10
        self.dotColor  = namedColor('black')
        self.dotSize = 2
        self.dots = self.genDotArrayPoints(Point(self.dotSpread / 2, self.dotSpread / 2))
        self.fullscreen = False

    def drawLines(self):
        for line in self.lines:
            line.draw(self.gameDisplay)

    def genDotArrayPoints(self, startingPoint = Point(0, 0)):
        dots = []
        for x in range(int((self.winWidth + (self.offScreenAmount * 2)) / self.dotSpread)):
            for y in range(int((self.winHeight + (self.offScreenAmount * 2)) / self.dotSpread)):
                dots.append(Point((x * self.dotSpread)+ startingPoint.x - self.offScreenAmount, (y * self.dotSpread) + startingPoint.y - self.offScreenAmount))
        return dots

    def drawDots(self):
        for i in self.dots:
            pygame.draw.rect(self.gameDisplay, self.dotColor.color, pygame.Rect(i.data(), [self.dotSize, self.dotSize]))

    def drawFocus(self):
        pygame.draw.circle(self.gameDisplay, self.focusColor.color, self.focusLoc.data(), FOCUS_RADIUS, 1)

    def updateMouse(self):
        self.mouseLoc = Point(*pygame.mouse.get_pos())

    def updateFocus(self):
        self.focusLoc = Point(min(self.dots, key=lambda i:abs(i.x - self.mouseLoc.x)).x + 1, min(self.dots, key=lambda i:abs(i.y - self.mouseLoc.y)).y + 1)

    def run(self):
        run = True
        currentLine = None
        dragging = 0
        specificErase = None
        ignoreMouse = False

        while run:
            pygame.display.flip()
            self.gameDisplay.fill(self.background.color)

            if not ignoreMouse:
                self.updateMouse()
                self.updateFocus()
            
            for event in pygame.event.get():

                if event.type != pygame.MOUSEMOTION:
                    pass
                    # print(len(self.lines))
                    # print(currentLine)
                    # print(event)

                #* Exit the window
                if(event.type == pygame.QUIT):
                    self.exit()
                
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                    ignoreMouse = False

                #* Mouse moves
                if event.type == pygame.MOUSEMOTION:
                    if currentLine != None:
                        currentLine.end = self.focusLoc
                        if event.buttons[0]:
                            dragging += 1

                #* If the left mouse button is released after being dragged
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging > DRAG_DELAY:
                    dragging = 0
                    currentLine.finish(self.focusLoc)
                    self.lines.append(currentLine)
                    currentLine = None
                
                #* Left mouse button clicked or space is pressed
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or \
                   (event.type == pygame.KEYDOWN and event.unicode == ' '):
                    if currentLine == None:
                        print('current line is None, and im creating a new line at', self.focusLoc)
                        currentLine = Line(Point(*self.focusLoc.data()))
                    else:
                        print('current line is not None, and im enting the current line at', self.focusLoc)
                        currentLine.finish(Point(*self.focusLoc.data()))
                        self.lines.append(currentLine)
                        currentLine = None

                #* Right mouse button clicked or c is pressed
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3) or \
                   (event.type == pygame.KEYDOWN and event.key == pygame.K_c):
                    if currentLine == None:
                        currentLine = Line(self.focusLoc)
                    else:
                        currentLine.finish(self.focusLoc)
                        self.lines.append(currentLine)
                        currentLine = Line(self.focusLoc)

                #* Middle mouse butten clicked or q is pressed
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 2) or \
                   (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                    for index, i in enumerate(self.lines):
                        if i.start == self.focusLoc or i.end == self.focusLoc:
                            del self.lines[index]
                    currentLine = None

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE: #* Esc
                        self.exit()

                    if event.unicode == 'f':
                        # Its better to call pygame.display.set_mode() with window flags to do this instead, because this will not work on windows.
                        pygame.display.toggle_fullscreen()
                        self.fullscreen = not self.fullscreen

                    if event.unicode == 'u' or event.unicode == '\x1a': # ctrl + z
                        if currentLine == None and len(self.lines) > 0:
                            del self.lines[-1]
                        elif currentLine != None:
                            currentLine = None

                    if event.unicode == 's':
                        if self.fullscreen == True:
                            pygame.display.toggle_fullscreen()
                        pickle.dump(self.lines, open(savesFolder + input("What would you like this pattern to be saved as?\n") + '.gdl', "wb" ))
                        print('File Saved!')

                    if event.unicode == 'o':
                        if self.fullscreen == True:
                            pygame.display.toggle_fullscreen()
                        print(dict(enumerate(os.listdir(savesFolder))))
                        self.lines = pickle.load(open(savesFolder + os.listdir(savesFolder)[int(input(f'Which file would you like to open? (0-{len(os.listdir(savesFolder)) - 1})\n'))], 'rb'))

                    if event.unicode == 'Q':
                        self.lines = []
                        currentLine = None

                    if event.key == 264 or event.key == pygame.K_HOME: # numpad up
                        self.dotSpread += 1
                        self.dots = self.genDotArrayPoints(Point(self.dotSpread / 2, self.dotSpread / 2))
                    
                    if event.key == 258 or event.key == pygame.K_END: # numpad down
                        self.dotSpread -= 1
                        self.dots = self.genDotArrayPoints(Point(self.dotSpread / 2, self.dotSpread / 2))

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

                    if event.key == pygame.K_UP or event.unicode == 'w':
                        self.focusLoc.y = self.focusLoc.y - self.dotSpread
                        if currentLine != None:
                            currentLine.end = self.focusLoc
                        ignoreMouse = True

                    if event.key == pygame.K_DOWN or event.unicode == 's':
                        self.focusLoc.y = self.focusLoc.y + self.dotSpread
                        if currentLine != None:
                            currentLine.end = self.focusLoc
                        ignoreMouse = True

                    if event.key == pygame.K_LEFT or event.unicode == 'a':
                        self.focusLoc.x = self.focusLoc.x - self.dotSpread
                        if currentLine != None:
                            currentLine.end = self.focusLoc
                        ignoreMouse = True

                    if event.key == pygame.K_RIGHT or event.unicode == 'd':
                        self.focusLoc.x = self.focusLoc.x + self.dotSpread
                        if currentLine != None:
                            currentLine.draw(self.gameDisplay)
                            currentLine.end = self.focusLoc
                        ignoreMouse = True

                    # add key here

                # print(event)

            self.drawFocus()
            self.drawLines()
            if currentLine != None:
                # print('running')
                currentLine.draw(self.gameDisplay)
            self.drawDots()

            
            pygame.display.update()
            self.clock.tick(self.fps)

    def text_objects(self, text, font):
        textSurface = font.render(text, True, namedColor('black').color)
        return textSurface, textSurface.get_rect()

    def message_display(self, text):
        largeText = pygame.font.Font('freesansbold.ttf', 115)
        TextSurf, TextRect = self.text_objects(text, largeText)
        TextRect.center = ((display_width / 2),(display_height / 2))
        self.gameDisplay.blit(TextSurf, TextRect)

        pygame.display.update()
        # time.sleep(2)
        self.run()

    def exit(self):
        pygame.quit()
        quit()

game = Game(1366, 768, 'GeoDoodle')
# game = Game(400, 368, 'GeoDoodle')
game.run()
game.exit()