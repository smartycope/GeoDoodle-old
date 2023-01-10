from PIL import Image, ImageColor, ImageDraw
import sdxf
import svgwrite
import json
from Cope import todo, debug, untested, confidence, flattenList
from PyQt6.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QWidget
from Line import Line
from Point import Point
from time import gmtime
from Singleton import Singleton as S


def getFile(self, save=True, extensions=('.gdl',)):
    # Promts the user for a filepath
    if save:
        file = QFileDialog.getSaveFileName(self,
                caption='Save Pattern',
                filter=' *'.join(('',)+extensions),
                initialFilter=' *'.join(('',)+extensions)
            )[0]
    else:
        file = QFileDialog.getOpenFileName(self,
            caption='Load Pattern',
            filter=' *'.join(('',)+extensions),
            initialFilter=' *'.join(('',)+extensions)
        )[0]

    if file != '' and file is not None:
        if not file.endswith(extensions):
            file = file + extensions[0]

    return file

def save(self):
    if self.saveFile is None:
        time = gmtime()
        self.saveFile = S.settings['files/savePath'] / f'{time.tm_mon}-{time.tm_mday}-{time.tm_year} {time.tm_hour}:{time.tm_min}:{time.tm_sec}.gdl'
    with open(self.saveFile, 'w') as f:
        f.write(self.serialize())
    print('Pattern Saved!')

def saveAs(self):
    todo('saveAs')
    self.save()

def exportPNG(self):
    image = Image.new('RGB', (self.width(), self.height()), color=tuple(self.background))
    draw = ImageDraw.Draw(image)
    for line in self.lines + self.getLinesFromPattern():
        draw.line(line.start.data() + line.end.data(),
                  fill=tuple(line.color),
                  width=S.settings.value('paper/export_line_thickness'))

    image.save(getFile(True))
    print('PNG Exported!')

def exportDXF(self):
    d=sdxf.Drawing()
    # d.append(sdxf.Text('Hello World!',point=(3,0,1)))
    for line in self.lines + self.getLinesFromPattern():
        d.append(sdxf.Line(points=[line.start.data() + (0,), line.end.data() + (0,)]))
    d.saveas(getFile(True))
    print('DXF Exported!')

def exportSVG(self):
    svg = svgwrite.Drawing('test.svg', profile='tiny')
    # svg.add(svg.text('Test', insert=(0, 0.2), fill='red'))
    for line in self.lines + self.getLinesFromPattern():
        svg.add(svg.line(line.start.data(), line.end.data(), stroke=svgwrite.rgb(10, 10, 16, '%')))
    svg.saveas(getFile(True))
    print("SVG Exported!")
