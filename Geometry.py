from pygame  import Rect, draw
from Line    import Line 
from Point   import Point

from math    import ceil
 

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


# TODO this works enough, but it's still off by just a little
def scalePoint(point, startDotSpread, newDotSpread):
    if startDotSpread == newDotSpread:
        return point

    offset = newDotSpread - startDotSpread
        
    point.x = round((point.x / startDotSpread) * newDotSpread) + offset
    point.y = round((point.y / startDotSpread) * newDotSpread) + offset

    return point


def scaleLines_ip(lines, startDotSpread, newDotSpread):
    ''' Scales the lines appropriately in place '''
    if startDotSpread == newDotSpread:
        return

    for line in lines:
        line.start = scalePoint(line.start, startDotSpread, newDotSpread)
        line.end   = scalePoint(line.end,   startDotSpread, newDotSpread)


def scaleLines(lines, startDotSpread, newDotSpread):
    ''' Scales the lines appropriately, and return them '''
    returnLines = []
    if startDotSpread == newDotSpread:
        return None

    for line in lines:
        start = scalePoint(line.start, startDotSpread, newDotSpread)
        end   = scalePoint(line.end,   startDotSpread, newDotSpread)
        returnLines.append(Line(start, end))

    return returnLines
    

def repeatPattern(pattern, size, dotSpread, startPoint, offScreenAmount, overlap, halfsies):
    from Pattern import Pattern
    returnLines = []
    patternSize = pattern.getSize(dotSpread)

    #* First determine how many patterns can fit in the x and y
    xAmount = ceil((size[0] + offScreenAmount + overlap[0]) / patternSize[0])
    yAmount = ceil((size[1] + offScreenAmount + overlap[1]) / patternSize[1])

    print('xAmount:', xAmount)
    print('yAmount:', yAmount)
    print('size of the pattern:', patternSize)
    print('overlap:', overlap)

    for x in range(xAmount):
        for y in range(yAmount):
            p = Point( (x * (patternSize[0] + overlap[0]) ) - offScreenAmount + startPoint.x, 
                       (y * (patternSize[1] + overlap[1]) ) - offScreenAmount + startPoint.y )
            returnLines += pattern.getPatternAtLoc(p, halfsies=halfsies)

    print('length of return lines:', len(returnLines))
    return returnLines