#ifdef __APPLE__
#include <openGL/gl.h> // Main OpenGL library
#include <GLUT/glut.h> // Second OpenGL library
#endif // __APPLE__

#ifdef __linux__
#include <GL/gl.h>     // Main OpenGL library
#include <GL/glut.h>   // Second OpenGL library
#endif // __linux__

#ifdef _WIN32
#include <stdio.h>
#include <stdlib.h>
#include <GL/glut.h>   // OpenGL library we copied
#include <ctime>       // for ::Sleep();
#include <windows.h>

#define _USE_MATH_DEFINES
#include <math.h>
#endif // _WIN32

#include <cassert>

#include "glutCallbacks.h"

#define MOUSE_MOVES 193 // litterally just any random number you think isn't being used by GLUT already

/*********************************************************************
 * SLEEP
 * Pause for a while.  We want to put the program to sleep until it
 * is time to draw again.  Note that this requires us to tell the OS
 * that we are idle.  the nanosleep function performs this task for us
 *   INPUT: msSleep: sleep time in milliseconds
 *********************************************************************/
void sleep(unsigned long msSleep) {
   // Windows handles sleep one way
#ifdef _WIN32
   ::Sleep(msSleep + 35);

   // Unix-based operating systems (OS-X, Linux) do it another
#else // LINUX, XCODE
   timespec req = {};
   time_t sec = (int)(msSleep / 1000);
   msSleep -= (sec * 1000);

   req.tv_sec = sec;
   req.tv_nsec = msSleep * 1000000L;

   while (nanosleep(&req, &req) == -1)
      ;
#endif // LINUX, XCODE
   return;
}

/************************************************************************
 * DRAW CALLBACK
 * This is the main callback from OpenGL. It gets called constantly by
 * the graphics engine to refresh and draw the window.  Here we will
 * clear the background buffer, draw on it, and send it to the forefront
 * when the appropriate time period has passsed.
 *
 * Note: This and all other callbacks can't be member functions, they must
 * have global scope for OpenGL to see them.
 *************************************************************************/
void drawCallback(){
   // even though this is a local variable, all the members are static
   Interface ui;
   // Prepare the background buffer for drawing
   glClear(GL_COLOR_BUFFER_BIT); //clear the screen
   glColor3f(0,0,0);

   //calls the client's display function
   assert(ui.callBack != NULL);
   ui.callBack(&ui, ui.p);

   //loop until the timer runs out
   if (!ui.isTimeToDraw())
      sleep((unsigned long)((ui.getNextTick() - clock()) / 1000));

   // from this point, set the next draw time
   ui.setNextDrawTime();
   // bring forth the background buffer
   glutSwapBuffers();
   // clear the space at the end
   ui.keyEvent();
   ui.modKeyEvent();
}

/************************************************************************
 * KEY DOWN CALLBACK
 * When a key on the keyboard has been pressed, we need to pass that
 * on to the client.  Currently, we are only registering the arrow keys
 *   INPUT   key:   the key we pressed according to the GLUT_KEY_ prefix
 *           x y:   the position in the window, which we ignore
 *************************************************************************/
void keyDownCallback(int key, int x, int y){
   // Even though this is a local variable, all the members are static
   // so we are actually getting the same version as in the constructor.
   Interface ui;
   ui.keyEvent(key, true);
   ui.modKeyEvent(glutGetModifiers(), true);
}

/************************************************************************
 * KEY UP CALLBACK
 * When the user has released the key, we need to reset the pressed flag
 *   INPUT   key:   the key we pressed according to the GLUT_KEY_ prefix
 *           x y:   the position in the window, which we ignore
 *************************************************************************/
void keyUpCallback(int key, int x, int y){
   // Even though this is a local variable, all the members are static
   // so we are actually getting the same version as in the constructor.
   Interface ui;
   ui.keyEvent(key, false /*fDown*/);
   ui.modKeyEvent(glutGetModifiers(), false);
}

/***************************************************************
 * KEYBOARD CALLBACK
 * Generic callback to a regular ascii keyboard event, such as
 * the space bar or the letter 'q'
 ***************************************************************/
void keyboardCallback(unsigned char key, int x, int y){
   // Even though this is a local variable, all the members are static
   // so we are actually getting the same version as in the constructor.
   Interface ui;
   ui.keyEvent(key, true /*fDown*/);
   ui.modKeyEvent(glutGetModifiers(), true);
}

void mouseCallback(int button, int state, int x, int y){
    // debug("mouseCallback Called!");
   if(state == GLUT_DOWN){
        Interface ui;
        ui.keyEvent(button, true);
      // the 200 is because this reads from the top left corner, but uiDraw.cpp writes from the center (i.e. where (0, 0) is)
        ui.setMouseLoc(x - getWindowWidth() / 2, -(y - getWindowHeight() / 2));
        // ui.setMouseLoc(x, -y);
   }
}

void mouseMotionCallback(int x, int y){
   Interface ui;
   ui.keyEvent(MOUSE_MOVES, true);
   // the 200 is because this reads from the top left corner, but uiDraw.cpp writes from the center (i.e. where (0, 0) is)
   ui.setMouseLoc(x - getWindowWidth() / 2, -(y - getWindowHeight() / 2));
    // ui.setMouseLoc(x, -y);
}

void setMouse(bool hidden){
    glutSetCursor((hidden ? 0x0065 : 0x0000));
}

// returns how many pixles are in a quarter inch, flag to get the number in 1 mm instead. Returns 0 if unavailable.
int pixCount(bool metric){
    // std::cout << "screen width: " <<  GLUT_SCREEN_WIDTH << ", "
    //           << "glut screen width: " << glutGet(GLUT_SCREEN_WIDTH) << ", "
    //           << "glut screen width mm: " << glutGet(GLUT_SCREEN_WIDTH_MM) << std::endl;
    // return 0;
    assert(int(float(glutGet(GLUT_SCREEN_WIDTH_MM))  / float(glutGet(GLUT_SCREEN_WIDTH))) ==
           int(float(glutGet(GLUT_SCREEN_HEIGHT_MM)) / float(glutGet(GLUT_SCREEN_HEIGHT))));
    if(metric){
        return int(round(float(glutGet(GLUT_SCREEN_WIDTH_MM)) / float(glutGet(GLUT_SCREEN_WIDTH))));
    }
    else{
        return int(round(float(glutGet(GLUT_SCREEN_WIDTH)) / float(glutGet(GLUT_SCREEN_WIDTH_MM)) * 6.35f));
    }
}

int getWindowWidth(){
    return glutGet(GLUT_WINDOW_WIDTH);
}

int getWindowHeight(){
    return glutGet(GLUT_WINDOW_HEIGHT);
}

// this doesn't have anything to do with glut, but I want it to have a global scope anyway, because it's useful.
bool isCloseEnough(int from, int to, int tolerance){
    if( (from < (to + tolerance)) and
        (from > (to - tolerance)) )
            return true;
    else
        return false;
}

nlohmann::json getSettings(){
    std::ifstream fin("../settings.json");
    nlohmann::json j;
    fin >> j;
    return j;
}

void setSettings(nlohmann::json setting){
    std::ofstream fout("../settings.json");
    fout << setting.dump(4);
}
