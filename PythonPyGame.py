import pygame, os
from collections import namedtuple

os.system('clear')

Point = namedtuple('Point', ['x', 'y'])

class Color:
    def __init__(self, r = 0, g = 0, b = 0, a = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.color = [self.r, self.g, self.b, self.a]
    
def namedColor(color):
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

class Line:
    def __init__(self, start, end = [-1, -1], data = ([])):
        self.start = start
        self.end   = end
        self.data  = data
        self.color = namedColor('black')

    def append(self, loc):
        self.data.append(loc)

    def finish(self, loc, data = list()):
        self.end = loc
        self.data = data

    def isFinished(self):
        return (self.end == [-1, -1])

    def _getData(self):
        tmpData = self.data
        tmpData.insert(0, self.start)
        if self.end != [-1, -1]:
            tmpData.append(self.end)
        return tmpData

    def draw(self, display):
        # self is a point
        if len(self.data) < 1 and self.start == self.end:
            pygame.draw.circle(display, self.color.color, self.start, 1)

        # self is a normal line
        elif len(self.data) > 0 and self.isFinished():
            pygame.draw.lines(display, self.color.color, False, self._getData())

        # self is an unfinished line that is more than 2 points
        elif len(self._getData()) > 1:
            assert(not self.isFinished())
            pygame.draw.lines(display, self.color.color, False, self._getData())

class Game:
    def __init__(self, winWidth = 485, winHeight = 300, title = 'Hello World!'):
        pygame.init()
        pygame.display.set_caption(title)
        self.gameDisplay = pygame.display.set_mode((winWidth, winHeight))
        self.clock = pygame.time.Clock()
        self.lines = list()
        self.background = namedColor('white')
        self.winWidth  = winWidth
        self.winHeight = winHeight
        self.mouseLoc  = pygame.mouse.get_pos()
        self.fps = 60

    def drawLines(self):
        for line in self.lines:
            line.draw(self.gameDisplay)

    def updateMouse(self):
        self.mouseLoc = pygame.mouse.get_pos()

    def run(self):
        self.gameDisplay.fill(self.background.color)
        run = True
        while run:
            self.updateMouse()
            # print(self.mouseLoc)
            
            for event in pygame.event.get():
                print(pygame.event.event_name(event.type))
                print(pygame.key.get_pressed())

                if(event.type == pygame.QUIT):# or (event.type == pygame.KEYDOWN and pygame.K_ESCAPE):
                    run = False

                if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                    self.lines[-1].append(self.mouseLoc)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.lines.append(Line(self.mouseLoc))

                if event.type == pygame.MOUSEBUTTONUP:
                    self.lines[-1].finish(self.mouseLoc)

                # print(event)

            self.drawLines()

            
            pygame.display.update()
            self.clock.tick(self.fps)

    def text_objects(self, text, font):
        textSurface = font.render(text, True, black)
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

game = Game()
game.run()
game.exit()