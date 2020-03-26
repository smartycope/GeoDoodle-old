/***********************************************************************
 *    This is the code necessary to draw on the screen. We have a collection
 *    of procedural functions here because each draw function does not
 *    retain state. In other words, they are verbs (functions), not nouns
 *    (variables) or a mixture (objects)
 ************************************************************************/

#ifndef UI_DRAW_H
#define UI_DRAW_H

#include <string>     // To display text on the screen
#include <cmath>      // for M_PI, sin() and cos()
// using std::string;

/*************************************************************************
 * DRAW TEXT
 * Draw text using a simple bitmap font
 ************************************************************************/
void drawText(const std::pair<int, int> &topLeft, std::string);

/************************************************************************
 * ROTATE
 * Rotate a given point (point) around a given origin (center) by a given
 * number of degrees (angle).
 *************************************************************************/
// void rotate(std::pair<int, int> &point, const std::pair<int, int> &origin, int rotation = 0);

/************************************************************************
 * DRAW RECTANGLE
 * Draw a rectangle on the screen centered on a given point (center) of
 * a given size (width, height), and at a given orientation (rotation)
 * measured in degrees (0 - 360)	
 *************************************************************************/
// void drawRect(const std::pair<int, int> &center, int width, int height, int rotation);

/************************************************************************
 * DRAW CIRCLE
 * Draw a circle from a given location (center) of a given size (radius).
 *************************************************************************/
void drawCircle(const std::pair<int, int> &center, int radius);

/************************************************************************
 * DRAW POLYGON
 * Draw a polygon from a given location (center) of a given size (radius).
 *************************************************************************/
// void drawPolygon(const std::pair<int, int> & center,
//                  int radius = 20,
//                  int points = 4,
//                  int rotation = 0);

/************************************************************************
 * DRAW LINE
 * Draw a line on the screen from the beginning to the end.
 *************************************************************************/
void drawLine(const std::pair<int, int> &begin, const std::pair<int, int> &end,
             float red = 1.0, float green = 1.0, float blue = 1.0);

/************************************************************************
 * DRAW DOT
 * Draw a single point on the screen, 2 pixels by 2 pixels
 *************************************************************************/
void drawDot(const std::pair<int, int> &point);

/******************************************************************
 * RANDOM
 * This function generates a random number.  The user specifies
 * The parameters 
 *    INPUT:   min, max : The number of values (min <= num <= max)
 *    OUTPUT   <return> : Return the integer
 ****************************************************************/
int    random(int    min, int    max);
double random(double min, double max);

#endif // UI_DRAW_H