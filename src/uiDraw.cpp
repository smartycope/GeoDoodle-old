/***********************************************************************
 * Source File:
 *    User Interface Draw : put pixels on the screen
 * Author:
 *    Br. Helfrich
 * Summary:
 *    This is the code necessary to draw on the screen. We have a collection
 *    of procedural functions here because each draw function does not
 *    retain state. In other words, they are verbs (functions), not nouns
 *    (variables) or a mixture (objects)
 ************************************************************************/

#include <string>     // need you ask?
#include <sstream>    // convert an integer into text
#include <cassert>    // I feel the need... the need for asserts
#include <time.h>     // for clock


#ifdef __APPLE__
#include <openGL/gl.h>    // Main OpenGL library
#include <GLUT/glut.h>    // Second OpenGL library
#endif // __APPLE__

#ifdef __linux__
#include <GL/gl.h>        // Main OpenGL library
#include <GL/glut.h>      // Second OpenGL library
#endif // __linux__

#ifdef _WIN32
#include <stdio.h>
#include <stdlib.h>
#include <GL/glut.h>         // OpenGL library we copied 
#define _USE_MATH_DEFINES
#include <math.h>
#endif // _WIN32

#include "uiDraw.h"

using namespace std;

#define deg2rad(value) ((M_PI / 180) * (value))
#define ARRAY_WIDTH 10
#define BORDER_WIDTH 5

// code for changing the color (don't forget to change it back afterwards!)
// glColor3f(0, 0, 0);

/*********************************************
 * NUMBER OUTLINES
 * We are drawing the text for score and things
 * like that by hand to make it look "old school."
 * These are how we render each individual charactger.
 * Note how -1 indicates "done".  These are paired
 * coordinates where the even are the x and the odd
 * are the y and every 2 pairs represents a point
 ********************************************/
const char NUMBER_OUTLINES[10][20] =
{
  {0, 0,  7, 0,   7, 0,  7,10,   7,10,  0,10,   0,10,  0, 0,  -1,-1, -1,-1},//0
  {7, 0,  7,10,  -1,-1, -1,-1,  -1,-1, -1,-1,  -1,-1, -1,-1,  -1,-1, -1,-1},//1
  {0, 0,  7, 0,   7, 0,  7, 5,   7, 5,  0, 5,   0, 5,  0,10,   0,10,  7,10},//2
  {0, 0,  7, 0,   7, 0,  7,10,   7,10,  0,10,   4, 5,  7, 5,  -1,-1, -1,-1},//3
  {0, 0,  0, 5,   0, 5,  7, 5,   7, 0,  7,10,  -1,-1, -1,-1,  -1,-1, -1,-1},//4
  {7, 0,  0, 0,   0, 0,  0, 5,   0, 5,  7, 5,   7, 5,  7,10,   7,10,  0,10},//5
  {7, 0,  0, 0,   0, 0,  0,10,   0,10,  7,10,   7,10,  7, 5,   7, 5,  0, 5},//6
  {0, 0,  7, 0,   7, 0,  7,10,  -1,-1, -1,-1,  -1,-1, -1,-1,  -1,-1, -1,-1},//7
  {0, 0,  7, 0,   0, 5,  7, 5,   0,10,  7,10,   0, 0,  0,10,   7, 0,  7,10},//8
  {0, 0,  7, 0,   7, 0,  7,10,   0, 0,  0, 5,   0, 5,  7, 5,  -1,-1, -1,-1} //9
};

/*************************************************************************
 * DRAW TEXT
 * Draw text using a simple bitmap font
 *   INPUT  topLeft   The top left corner of the text
 *          text      The text to be displayed
 ************************************************************************/
void drawText(const std::pair<int, int> &topLeft, const std::string &text)
{
   void *pFont = GLUT_BITMAP_HELVETICA_12;  // also try _18

   // prepare to draw the text from the top-left corner
   glRasterPos2f(topLeft.first, topLeft.second);

   // loop through the text
//    for (const char *p = text; *p; p++)
   for (auto it = text.begin(); it != text.end(); it++)
      glutBitmapCharacter(pFont, *it);
}

/************************************************************************
 * DRAW POLYGON
 * Draw a POLYGON from a given location (center) of a given size (radius).
 *  INPUT   center   Center of the polygon
 *          radius   Size of the polygon
 *          points   How many points will we draw it.  Larger the number,
 *                   the more line segments we will use
 *          rotation True circles are rotation independent.  However, if you
 *                   are drawing a 3-sided polygon (triangle), this matters!
 *************************************************************************
 
void drawPolygon(const std::pair<int, int> &center, int radius, int points, int rotation) {
   // begin drawing
   glBegin(GL_LINE_LOOP);

   //loop around a circle the given number of times drawing a line from
   //one point to the next
   for (double i = 0; i < 2 * M_PI; i += (2 * M_PI) / points)
   {
      Point temp(false);
      temp.setX(center.getX() + (radius * cos(i)));
      temp.setY(center.getY() + (radius * sin(i)));
      rotate(temp, center, rotation);
      glVertex2f(temp.getX(), temp.getY());
   }

   // complete drawing
   glEnd();
}
*/

/************************************************************************
 * ROTATE
 * Rotate a given point (point) around a given origin (center) by a given
 * number of degrees (angle).
 *    INPUT  point    The point to be moved
 *           center   The center point we will rotate around
 *           rotation Rotation in degrees
 *    OUTPUT point    The new position
 *************************************************************************
 
void rotate(std::pair<int, int> &point, const std::pair<int, int> &origin, int rotation){
   // because sine and cosine are expensive, we want to call them only once
   double cosA = cos(deg2rad(rotation));
   double sinA = sin(deg2rad(rotation));

   // remember our original point
   Point tmp(false);
   tmp.setX(point.getX() - origin.getX());
   tmp.setY(point.getY() - origin.getY());

   // find the new values
   point.setX(static_cast<int> (tmp.getX() * cosA -
                                tmp.getY() * sinA) +
              origin.getX());
   point.setY(static_cast<int> (tmp.getX() * sinA +
                                tmp.getY() * cosA) +
              origin.getY());
}
*/

/************************************************************************
 * DRAW LINE
 * Draw a line on the screen from the beginning to the end.
 *   INPUT  begin     The position of the beginning of the line
 *          end       The position of the end of the line
 *************************************************************************/
void drawLine(const std::pair<int, int> &begin, const std::pair<int, int> &end,
              float red, float green, float blue) {
   // Get ready...
   glBegin(GL_LINES);
   glColor3f(red, green, blue);

   // Draw the actual line
   glVertex2f(begin.first, begin.second);
   glVertex2f(  end.first,   end.second);

   // Complete drawing
   glColor3f(1.0 /* red % */, 1.0 /* green % */, 1.0 /* blue % */);
   glEnd();
}

/******************************************************************
 * RANDOM
 * This function generates a random number.  
 *
 *    INPUT:   min, max : The number of values (min <= num <= max)
 *    OUTPUT   <return> : Return the integer
 ****************************************************************/
int random(int min, int max)
{
   assert(min < max);
   int num = (rand() % (max - min)) + min;
   assert(min <= num && num <= max);

   return num;
}

/******************************************************************
 * RANDOM
 * This function generates a random number.  
 *
 *    INPUT:   min, max : The number of values (min <= num <= max)
 *    OUTPUT   <return> : Return the double
 ****************************************************************/
double random(double min, double max)
{
   assert(min <= max);
   double num = min + ((double)rand() / (double)RAND_MAX * (max - min));
   
   assert(min <= num && num <= max);

   return num;
}


/************************************************************************
 * DRAW RECTANGLE
 * Draw a rectangle on the screen centered on a given point (center) of
 * a given size (width, height), and at a given orientation (rotation)
 *  INPUT  center    Center of the rectangle
 *         width     Horizontal size
 *         height    Vertical size
 *         rotation  Orientation
 *************************************************************************
 
void drawRect(const std::pair<int, int> &center, int width, int height, int rotation)
{
   Point tl(false); // top left
   Point tr(false); // top right 
   Point bl(false); // bottom left
   Point br(false); // bottom right

   //Top Left point
   tl.setX(center.getX() - (width  / 2));
   tl.setY(center.getY() + (height / 2));

   //Top right point
   tr.setX(center.getX() + (width  / 2));
   tr.setY(center.getY() + (height / 2));

   //Bottom left point
   bl.setX(center.getX() - (width  / 2));
   bl.setY(center.getY() - (height / 2));

   //Bottom right point
   br.setX(center.getX() + (width  / 2));
   br.setY(center.getY() - (height / 2));

   //Rotate all points the given degrees
   rotate(tl, center, rotation);
   rotate(tr, center, rotation);
   rotate(bl, center, rotation);
   rotate(br, center, rotation);

   //Finally draw the rectangle
   glBegin(GL_LINE_STRIP);
   glVertex2f(tl.getX(), tl.getY());
   glVertex2f(tr.getX(), tr.getY());
   glVertex2f(br.getX(), br.getY());
   glVertex2f(bl.getX(), bl.getY());
   glVertex2f(tl.getX(), tl.getY());
   glEnd();
}
*/

/************************************************************************
 * DRAW CIRCLE
 * Draw a circle from a given location (center) of a given size (radius).
 *  INPUT   center   Center of the circle
 *          radius   Size of the circle
 *************************************************************************/
void drawCircle(const std::pair<int, int> &center, int radius)
{
   assert(radius > 1.0);
   const double increment = 1.0 / (double)radius;

   // begin drawing
   glBegin(GL_LINE_LOOP);

   // go around the circle
   for (double radians = 0; radians < M_PI * 2.0; radians += increment)
      glVertex2f(center.first + (radius * cos(radians)),
                 center.second + (radius * sin(radians)));
   
   // complete drawing
   glEnd();   
}

/************************************************************************
 * DRAW DOT
 * Draw a single point on the screen, 2 pixels by 2 pixels
 *  INPUT point   The position of the dow
 *************************************************************************/
void drawDot(const std::pair<int, int> &point){
   // Get ready, get set...
   glBegin(GL_POINTS);

   // Go...
   glVertex2f(point.first,     point.second    );
   glVertex2f(point.first + 1, point.second    );
   glVertex2f(point.first + 1, point.second + 1);
   glVertex2f(point.first,     point.second + 1);

   // Done!  OK, that was a bit too dramatic
   glEnd();
}
