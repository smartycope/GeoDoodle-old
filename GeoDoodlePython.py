import pygame, os, pickle
from collections import namedtuple

os.system('clear')

dir = os.path.dirname(__file__) + '/'
savesFolder = dir + 'GeoDoodle Saves/'

# Point = namedtuple('Point', ['x', 'y'])

FOCUS_RADIUS = 6
DRAG_DELAY   = 5

class Point:
    def __init__(self, x = -1, y = -1):
        self.x = int(x)
        self.y = int(y)

    def __eq__(self, a):
        return self.x == a.x and self.y == a.y

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
        # return self.end.data() != [-1, -1]
        return self.end != None

    def draw(self, display):
        pygame.draw.aaline(display, self.color.color, self.start.data(), self.end.data())

class Game:
    def __init__(self, winWidth = 485, winHeight = 300, title = 'Hello World!'):
        pygame.init()
        pygame.display.set_caption(title)
        # pygame.display.set_icon(Surface)
        #* Add SCALED back in when pygame gets updated to 2.0.0
        # pygame.OPENGL should also be in here, but it doesn't work for some reason.
        windowFlags = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE # | pygame.FULLSCREEN # | pygame.SCALED
        self.gameDisplay = pygame.display.set_mode([winWidth, winHeight], windowFlags)
        self.clock = pygame.time.Clock()
        self.lines = list()
        self.background = namedColor('paper')
        self.winWidth   = winWidth
        self.winHeight  = winHeight
        self.mouseLoc   = Point(*pygame.mouse.get_pos())
        self.focusLoc   = Point()
        self.focusColor = namedColor('blue')
        self.fps = 60
        self.dotSpread = 17
        self.offScreenAmount = 10
        self.dotColor  = namedColor('black')
        self.dotSize = 2
        self.dots = self.genDotArrayPoints(Point(self.dotSpread / 2, self.dotSpread / 2))

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
        while run:
            pygame.display.flip()
            self.gameDisplay.fill(self.background.color)

            self.updateMouse()
            self.updateFocus()
            
            for event in pygame.event.get():

                if event.type != pygame.MOUSEMOTION:
                    print(event)

                #* Exit the window
                if(event.type == pygame.QUIT):
                    self.exit()
                
                #* Mouse moves
                if event.type == pygame.MOUSEMOTION:
                    if currentLine != None:
                        currentLine.end = self.focusLoc
                        if event.buttons[0]:
                            dragging += 1

                #* If the left mouse button is released after being dragged
                if event.type == pygame.MOUSEBUTTONUP and dragging > DRAG_DELAY:
                    dragging = 0
                    currentLine.finish(self.focusLoc)
                    self.lines.append(currentLine)
                    currentLine = None
                
                #* Left mouse button clicked
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if currentLine == None:
                        currentLine = Line(self.focusLoc)
                    else:
                        currentLine.finish(self.focusLoc)
                        self.lines.append(currentLine)
                        currentLine = None

                #* Right mouse button clicked or c is pressed
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3) or (event.type == pygame.KEYDOWN and event.key == pygame.K_c):
                    if currentLine == None:
                        currentLine = Line(self.focusLoc)
                    else:
                        currentLine.finish(self.focusLoc)
                        self.lines.append(currentLine)
                        currentLine = Line(self.focusLoc)

                #* Middle mouse butten clicked or q is pressed
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 2) or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                    for index, i in enumerate(self.lines):
                        if i.start == self.focusLoc or i.end == self.focusLoc:
                            del self.lines[index]

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE: #* Esc
                        self.exit()

                    if event.unicode == 'f':
                        # Its better to call pygame.display.set_mode() with window flags to do this instead, because this will not work on windows.
                        pygame.display.toggle_fullscreen()

                    if event.unicode == 'u' or event.unicode == '\x1a': # ctrl + z
                        if currentLine == None and len(self.lines) > 0:
                            del self.lines[-1]
                        elif currentLine != None:
                            currentLine = None

                    if event.unicode == 's':
                        pickle.dump(self.lines, open(savesFolder + input("What would you like this pattern to be saved as?\n") + '.gdl', "wb" ))
                        print('File Saved!')

                    if event.unicode == 'o':
                        print(dict(enumerate(os.listdir(savesFolder))))
                        self.lines = pickle.load(open(savesFolder + os.listdir(savesFolder)[int(input(f'Which file would you like to open? (0-{len(os.listdir(savesFolder)) - 1})\n'))], 'rb'))

                    if event.unicode == 'Q':
                        self.lines = []
                        currentLine = None

                    if event.key == 264: # numpad up
                        self.dotSpread += 1
                        self.dots = self.genDotArrayPoints(Point(self.dotSpread / 2, self.dotSpread / 2))
                    
                    if event.key == 258: # numpad down
                        self.dotSpread -= 1
                        self.dots = self.genDotArrayPoints(Point(self.dotSpread / 2, self.dotSpread / 2))



                        

                    # add key here

                # print(event)

            self.drawFocus()
            self.drawLines()
            if currentLine != None:
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

game = Game(1920, 1080, 'GeoDoodle')
game.run()
game.exit()