import os; os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame  import Rect, draw
from Line    import Line 
from Point   import Point
 

def getLargestRect(points):
    tmpX = sorted(points, key=lambda p: p.x)
    tmpY = sorted(points, key=lambda p: p.y)

    highest = tmpY[-1].y
    lowest  = tmpY[0].y
    left    = tmpX[-1].x
    right   = tmpX[0].x

    tmp = Rect(left, highest, right - left, lowest - highest)
    tmp.normalize()
    return tmp


def drawRect(surface, rect, color):
    draw.line(surface, color, rect.topleft,     rect.topright)
    draw.line(surface, color, rect.topright,    rect.bottomright)
    draw.line(surface, color, rect.bottomright, rect.bottomleft)
    draw.line(surface, color, rect.bottomleft,  rect.topleft)


#// TODO this works enough, but it's still off by just a little
def scalePoint(point, originPoint, startDotSpread, newDotSpread):
    if startDotSpread == newDotSpread:
        return point

    scaleX = True
    scaleY = True

    if point.x == originPoint.x:
        scaleX = False
    if point.y == originPoint.y:
        scaleY = False

    returnPoint = Point(point)

    if scaleX:
        returnPoint.x -= ((originPoint.x - returnPoint.x) / startDotSpread) * (newDotSpread - startDotSpread)
    if scaleY:
        returnPoint.y -= ((originPoint.y - returnPoint.y) / startDotSpread) * (newDotSpread - startDotSpread)

    return returnPoint


    # return point - ((originPoint - point) / startDotSpread) * (newDotSpread - startDotSpread)


def scaleLines_ip(lines, originPoint, startDotSpread, newDotSpread):
    ''' Scales the lines appropriately in place '''
    if startDotSpread == newDotSpread:
        return

    for line in lines:
        line.start = scalePoint(line.start, originPoint, startDotSpread, newDotSpread)
        line.end   = scalePoint(line.end,   originPoint, startDotSpread, newDotSpread)


def scaleLines(lines, originPoint, startDotSpread, newDotSpread):
    ''' Scales the lines appropriately, and return them '''
    returnLines = []
    if startDotSpread == newDotSpread:
        return None

    for line in lines:
        start = scalePoint(line.start, originPoint, startDotSpread, newDotSpread)
        end   = scalePoint(line.end,   originPoint, startDotSpread, newDotSpread)
        returnLines.append(Line(start, end))

    return returnLines


def genOnionLayer(dist, spread, origin, drawX=True, drawY=True):
    points = []

    for i in range(-dist, dist + 1):
        if drawY:
            points.append(origin + (Point(i, dist) * spread))
            points.append(origin + (Point(i, -dist) * spread))
        if drawX:
            points.append(origin + (Point(dist, i) * spread))
            points.append(origin + (Point(-dist, i) * spread))

    return points


def genDotArrayPoints(size, offScreenAmount, dotSpread):
    #* The top-left corner-centric way of generating dots
        # dots = []
        # for x in range(int((self.winWidth + (self.offScreenAmount)) / self.settings['dotSpread'])):
        #     for y in range(int((self.winHeight + (self.offScreenAmount)) / self.settings['dotSpread'])):
        #         dots.append(Point((x * self.settings['dotSpread'])+ startingPoint.x - self.offScreenAmount, 
        #                           (y * self.settings['dotSpread']) + startingPoint.y - self.offScreenAmount))

    #* The center-centric way of generating dots
    points = []

    xDist = int(size[0] / (dotSpread - offScreenAmount))
    yDist = int(size[1] / (dotSpread - offScreenAmount))

    values = sorted([xDist, yDist])

    for i in range(values[1]):
        points += genOnionLayer(i, dotSpread, Point(size) / 2)

    drawX = values[0] == xDist
    drawY = values[0] == yDist

    for i in range(values[0]):
        points += genOnionLayer(i, dotSpread, Point(size) / 2, drawX=drawX, drawY=drawY)

    return points
