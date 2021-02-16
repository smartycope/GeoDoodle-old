# from os import environ; environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# from pygame  import Rect
from Line    import Line
from Point import CoordPoint, TLPoint, GLPoint, InfPoint, Sizei, Sizef, Pointi, Pointf
from Cope    import isBetween, collidePoint, debug, debugged
from PyQt5.QtCore import QRect, QRectF



def getLargestRect(points) -> QRectF:
    highest = min(points, key=lambda p: p.y).y # - finagle
    lowest  = max(points, key=lambda p: p.y).y # + finagle
    left    = min(points, key=lambda p: p.x).x # - finagle
    right   = max(points, key=lambda p: p.x).x # + finagle

    return QRectF(left, highest, right - left, lowest - highest).normalized()


def drawRect(surface, rect, color):
    draw.line(surface, color, rect.topleft,     rect.topright)
    draw.line(surface, color, rect.topright,    rect.bottomright)
    draw.line(surface, color, rect.bottomright, rect.bottomleft)
    draw.line(surface, color, rect.bottomleft,  rect.topleft)


def scalePoint(point, originPoint, startDotSpread, newDotSpread):
    if startDotSpread == newDotSpread:
        return point

    scaleX = True
    scaleY = True

    if point.x == originPoint.x:
        scaleX = False
    if point.y == originPoint.y:
        scaleY = False

    returnPoint = point.copy()

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
        returnLines.append(Line(start, end, line.color))

    return returnLines


def genOnionLayer(dist, spread, origin, drawX=True, drawY=True):
    points = []

    for i in range(-dist, dist + 1):
        if drawY:
            points.append(origin + (Pointi(i, dist) * spread))
            points.append(origin + (Pointi(i, -dist) * spread))
        if drawX:
            points.append(origin + (Pointi(dist, i) * spread))
            points.append(origin + (Pointi(-dist, i) * spread))

    return points


def genDotArrayPoints(size, offScreenAmount, dotSpread, startPoint=Pointi(0, 0)):
    # debug(dotSpread, size, offScreenAmount, startPoint, color=-1)
    #* The top-left corner-centric way of generating dots
    # dots = []
    # for x in range(startPoint.x, size[0] + offScreenAmount, dotSpread):
    #     for y in range(startPoint.y, size[1] + offScreenAmount, dotSpread):
    #         dots.append(Pointi(x, y))
    # return dots

    #* The center-centric way of generating dots
    points = []

    xDist = int(size[0] / (dotSpread - offScreenAmount))
    yDist = int(size[1] / (dotSpread - offScreenAmount))

    values = sorted([xDist, yDist])

    for i in range(values[1]):
        points += genOnionLayer(i, dotSpread, Sizef(size) / 2)

    drawX = values[0] == xDist
    drawY = values[0] == yDist

    for i in range(values[0]):
        points += genOnionLayer(i, dotSpread, Sizef(size) / 2, drawX=drawX, drawY=drawY)

    #* These 2 lines are because the algorithm is broken somehow, and I'm too lazy to fix it. Its a O(1) cost, anyway
    points[:] = [i for i in points if collidePoint(Pointi(0, 0), size, i)]
    return tuple(set(points))
