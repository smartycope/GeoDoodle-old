/***********************************************************************
 * Source File:
 *     UI INTERACT
 * Author:
 *     Copeland Carter
 * Description:
 *     Implement the interfaces specified in uiInterface.h.  This handles
 *     all the interfaces and events necessary to work with OpenGL.  Your
 *     program will interface with this thorough the callback function
 *     pointer towards the bottom of the file.
 *     -To add another key, ctrl+f for "add key here" in here, the 
 *     header file, and game.cpp
 ************************************************************************/

#include <string>     // need you ask?
#include <sstream>    // convert an integer into text
#include <cassert>    // I feel the need... the need for asserts
#include <time.h>     // for clock
#include <cstdlib>    // for rand()
#include <iostream>

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

#include "uiInteract.h"

// using namespace std;

#define MOUSE_MOVES 193 // litterally just any random number you think isn't being used by GLUT already
#define BACKGROUND_COLOR 1, 1, 1, 0

/***************************************************************
 * INTERFACE : KEY EVENT
 * Either set the up or down event for a given key
 *   INPUT   key     which key is pressed
 *           fDown   down or brown
 ****************************************************************/
void Interface::keyEvent(int key, bool fDown){
   switch(key){
        case GLUT_KEY_DOWN:
            isDownPress = fDown;
            break;
      case GLUT_KEY_UP:
         isUpPress = fDown;
         break;
      case GLUT_KEY_RIGHT:
         isRightPress = fDown;
         break;
      case GLUT_KEY_LEFT:
         isLeftPress = fDown;
         break;
      case GLUT_KEY_HOME:
      case ' ':
         isSpacePress = fDown;
         break;
      case GLUT_KEY_F5:
         isF5Press = fDown;
         break;
      case 'c':
         isCPress = fDown;
         break;
      case 'x':
         isXPress = fDown;
         break;
      case GLUT_LEFT_BUTTON:
         isMouseClick = fDown;
         break;
      case GLUT_RIGHT_BUTTON:
         isMouseRightClick = fDown;
         break;
      case MOUSE_MOVES:
         isMouseMoving = fDown;
         break;
      case 'X':
         isBigXPress = fDown;
         break;
      case 13:
         isEnterPress = fDown;
         break;
      case 'Q':
         isBigQPress = fDown;
         break;
      case 'm':
         isMPress = fDown;
         break;
      case '/':
         isSlashPress = fDown;
         break;
      case '?':
         isQuestionPress = fDown;
         break;
      case 's':
         isSPress = fDown;
         break;
      case 'S':
         isBigSPress = fDown;
         break;
      case GLUT_KEY_F9:
         isF9Press = fDown;
         break;
        case 'z':
        case 'Z':
            isZPress = fDown;
            break;

      /*
        case '':
            isPress = fDown;
            break;
      */
      // add key here
   }
}

void Interface::modKeyEvent(int key, bool fDown){
   switch(key){
       case GLUT_ACTIVE_CTRL:
            isCtrlPress = fDown;
            // std::cout << "Control has been pressed\n";
            break;
        case GLUT_ACTIVE_ALT:
            isAltPress = fDown;
            // std::cout << "Alt has been pressed\n";
            break;
        case GLUT_ACTIVE_SHIFT:
            isShiftPress = fDown;
            // std::cout << "Shift has been pressed\n";
            break;
   }
}

void Interface::modKeyEvent(){
    isAltPress = false;
    isCtrlPress = false;
    isShiftPress = false;
}

/***************************************************************
 * INTERFACE : KEY EVENT
 * Either set the up or down event for a given key
 *   INPUT   key     which key is pressed
 *           fDown   down or brown
 ****************************************************************/
void Interface::keyEvent(){
   if (isDownPress)
      isDownPress++;    
   if (isUpPress)
      isUpPress++;
   if (isLeftPress)
      isLeftPress++;
   if (isRightPress)
      isRightPress++;
   isSpacePress = false;
   isCPress     = false;
   isXPress     = false;
   isMouseClick = false;
   isMouseRightClick = false;
   isMouseMoving  = false;
   isBigXPress  = false;
   isEnterPress = false;
   isBigQPress  = false;
   isMPress     = false;
   isSlashPress = false;
   isQuestionPress = false;
   isSPress    = false;
   isBigSPress = false;
   isF5Press   = false;
   isF9Press   = false;
//    isCtrlPress = false;
//    isAltPress = false;
//    isShiftPress = false;
   isZPress = false;

   /*
   isPress = false;
   */
   // add key here
}

/************************************************************************
 * INTEFACE : IS TIME TO DRAW
 * Have we waited long enough to draw swap the background buffer with
 * the foreground buffer?
 *************************************************************************/
bool Interface::isTimeToDraw(){
   return ((unsigned int)clock() >= nextTick);
}

/************************************************************************
 * INTERFACE : SET NEXT DRAW TIME
 * What time should we draw the buffer again?  This is a function of
 * the current time and the frames per second.
 *************************************************************************/
void Interface::setNextDrawTime(){
   nextTick = clock() + static_cast<int> (timePeriod * CLOCKS_PER_SEC);
}

/************************************************************************
 * INTERFACE : SET FRAMES PER SECOND
 * The frames per second dictates the speed of the game.  The more frames
 * per second, the quicker the game will appear to the user.  We will default
 * to 30 frames/second but the client can set this at will.
 *    INPUT  value        The number of frames per second.  30 is default
 *************************************************************************/
void Interface::setFramesPerSecond(double value){
    timePeriod = (1 / value);
}

/***************************************************
 * STATICS
 * All the static member variables need to be initializedwhite
 * Somewhere globally.  This is a good spot
 **************************************************/
int          Interface::isDownPress  = 0;
int          Interface::isUpPress    = 0;
int          Interface::isLeftPress  = 0;
int          Interface::isRightPress = 0;
bool         Interface::isSpacePress = false;
bool         Interface::isCPress     = false;
bool         Interface::isXPress     = false;
bool         Interface::isMouseClick = false;
bool         Interface::isMouseRightClick = false;
std::pair<int, int> Interface::mouseLoc; // (/* getSettings()["dot spread"] */ -1, /* getSettings()["dot spread"] */ -8);
bool         Interface::isMouseMoving = false;
bool         Interface::isBigXPress  = false;
bool         Interface::isEnterPress = false;
bool         Interface::isBigQPress  = false;
bool         Interface::isMPress     = false;
bool         Interface::isSlashPress = false;
bool         Interface::isQuestionPress = false;
bool         Interface::isSPress      = false;
bool         Interface::isBigSPress   = false;
bool         Interface::isF5Press     = false;
bool         Interface::isF9Press     = false;
bool         Interface::isCtrlPress   = false;
bool         Interface::isAltPress    = false;
bool         Interface::isShiftPress  = false;
bool         Interface::isZPress      = false;

/*
bool         Interface::isPress      = false;
*/
// add key here

bool         Interface::initialized  = false;
double       Interface::timePeriod   = 1.0 / 30; // default to 30 frames/second
unsigned int Interface::nextTick     = 0;        // redraw now please
void *       Interface::p            = NULL;
void (*Interface::callBack)(const Interface *, void *) = NULL;

/************************************************************************
 * INTEFACE : INITIALIZE
 * Initialize our drawing window.  This will set the size and position,
 * get ready for drawing, set up the colors, and everything else ready to
 * draw the window.  All these are part of initializing Open GL.
 *  INPUT    argc:       Count of command-line arguments from main
 *           argv:       The actual command-line parameters
 *           title:      The text for the titlebar of the window
 *************************************************************************/
void Interface::initialize(int argc, char ** argv, const char * title){
   if (initialized)
      return;
   
   // set up the random number generator
   srand((unsigned int)time(NULL));

   // create the window
   glutInit(&argc, argv);
   std::pair<int, int> point;
//    glutInitWindowSize(   // size of the window
//       (bottomRight.first - topLeft.first),
//       (topLeft.second - bottomRight.second));
            
   glutInitWindowPosition(100, 100);                // initial position
   glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);  // double buffering
   glutCreateWindow(title);              // text on titlebar
   glutIgnoreKeyRepeat(false); // previously true
   
   // set up the drawing style: B/W and 2D
   glClearColor(BACKGROUND_COLOR);          // set the background color
//    gluOrtho2D(topLeft.first, bottomRight.first,
            //   bottomRight.second, topLeft.second); // 2D environment
    gluOrtho2D(-START_WIDTH / 2, START_WIDTH / 2, -START_HEIGHT / 2, START_HEIGHT / 2);

    glutReshapeWindow(START_WIDTH, START_HEIGHT);

    // register the callbacks so OpenGL knows how to call us
    glutDisplayFunc(   drawCallback    );
    glutIdleFunc(      drawCallback    );
    glutKeyboardFunc(  keyboardCallback);
    glutSpecialFunc(   keyDownCallback );
    glutSpecialUpFunc( keyUpCallback   );
    glutMouseFunc(     mouseCallback   );
    glutPassiveMotionFunc( mouseMotionCallback );

    initialized = true;
    return;
}

/************************************************************************
 * INTERFACE : RUN
 *            Start the main graphics loop and play the game
 * INPUT callBack:   Callback function.  Every time we are beginning
 *                   to draw a new frame, we first callback to the client
 *                   to see if he wants to do anything, such as move
 *                   the game pieces or respond to input
 *       p:          Void point to whatever the caller wants.  You
 *                   will need to cast this back to your own data
 *                   type before using it.
 *************************************************************************/
void Interface::run(void (*callBack)(const Interface *, void *), void *p) {
   // setup the callbacks
   this->p = p;
   this->callBack = callBack;
   
   glutMainLoop();

   return;
}