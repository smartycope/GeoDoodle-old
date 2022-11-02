from PIL import Image, ImageColor, ImageDraw
import sdxf
import svgwrite
import json
from Cope import todo, debug, untested, confidence, flattenList
from PyQt6.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QWidget
import Pattern
from Line import Line
from Point import Pair

from Singleton import Singleton


def getFile(save: bool):
        return QFileDialog.getSaveFileName()[0] if save else QFileDialog.getOpenFileName()[0]


def save(self):
    self.exportJSON()
    print('File Saved!')

def saveAs(self):
    todo('saveAs')
    self.save()

def open(self):
    self.importJSON()

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

def exportJSON(self):
    file = getFile(True)
    if len(file):
        with open(file, 'w') as f:
            json.dump([
                        self.lines,
                        self.pattern,
                        self.bounds,
                        [
                            Pattern.params.xOverlap,
                            Pattern.params.yOverlap,
                            Pattern.params.includeHalfsies,
                            Pattern.params.skipRows,
                            Pattern.params.skipColumns,
                            Pattern.params.skipRowAmt,
                            Pattern.params.skipColumnAmt,
                            Pattern.params.flipRows,
                            Pattern.params.flipColumns,
                            Pattern.params.flipRowOrient,
                            Pattern.params.flipColumnOrient
                        ]
                    ], f)

def importJSON(self):
    file = getFile(False)
    if len(file):
        with open(file, 'rb') as f:
            lines, pattern, bounds, params = json.load(f)
            self.bounds = [Point(b) for b in bounds]
            Pattern.params = Pattern._PatternParams(*params)
            self.pattern = Pattern.Pattern.fromJson(pattern)
            self.lines = [Line.fromJson(line) for line in lines]
    self.updatePattern()
