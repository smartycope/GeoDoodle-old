#include "Point.hpp"
#include "cope.hpp"

#include <Qt/qapplication.h>
#include <Qt/qlabel.h>
#include <QtCore/QLine>
#include <QtCore/QLineF>
#include <QtCore/QPoint>
#include <QtCore/QPointF>
#include <QtCore/qline.h>
#include <QtGui/QColor>
#include <QtGui/QFont>
#include <QtGui/QPen>
#include <vector>

class Line: QLine {
    Line(start, end = None, pen; QPen = QPen(), label = None);
    void   finish(end);
    Line*  finished(end);
    Line*  copy();
    bool   isFinished();
    tern   within(rect);
    QLabel createLabel(parent, dotSpread, dotSpreadMeasure, dotSpreadUnit, backgroundColor);
    float  getDist();
    float  getLen(dotSpread, multiplier);
    Point  getLenLoc();
           operator std::string();
    bool&  operator==(a);
    Line&  operator-(Point);
    Line&  operator+(Point);
    __isub__(point);
    __iadd__(point);
    __json__(**options);
    fromJson(j);
};