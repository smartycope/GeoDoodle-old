/*********************************************
 *    This module will create an OpenGL window,
 *    enter the OpenGL main loop, and accept events.
 *    The main methods are:
 *    1. Constructors - Create the window
 *    2. run()        - Run the main loop
 *    3. callback     - Specified in Run, this user-provided
 *                      function will get called with every frame
 *    4. isDown()     - Is a given key pressed on this loop?
 **********************************************/

#ifndef UI_INTERFACE_H
#define UI_INTERFACE_H

#include <iostream>
#include "glutCallbacks.h"

// #define START_WIDTH  400 // in settings
// #define START_HEIGHT 400 // in settings

// #define START_WIDTH  int(getSettings()["start width" ])
// #define START_HEIGHT int(getSettings()["start height"])

#define START_WIDTH  100
#define START_HEIGHT 700

void setMouse(bool hidden);

/********************************************
 * INTERFACE
 * All the data necessary to keep our graphics
 * state in memory
 ********************************************/
class Interface{
public:
   // Default constructor useful for setting up the random variables
   // or for opening the file for output
   Interface() {
       initialize(0, 0x0000, "Window");
    };

   // Constructor if you want to set up the window with anything but the default parameters
   Interface(int argc, char ** argv, const char * title){
      initialize(argc, argv, title);
   }

   // Destructor, incase any housecleaning needs to occur
   ~Interface() { };

   // This will set the game in motion
   void run(void (*callBack)(const Interface *, void *), void *p);

   // Is it time to redraw the screen
   bool isTimeToDraw();

   // Set the next draw time based on current time and time periodpUI
   void setNextDrawTime();

   // Retrieve the next tick time... the time of the next draw.
   unsigned int getNextTick() { return nextTick; };

   // How many frames per second are we configured for?
   void setFramesPerSecond(double value);

   // Key event indicating a key has been pressed or not. The callbacks
   // should be the only onces to call this
   void keyEvent(int key, bool fDown);
   void keyEvent();
   void modKeyEvent(int key, bool fDown);
   void modKeyEvent();
   void reshapeWindow(int width, int height);

   // Current frame rate
   double frameRate() const { return timePeriod; };

   void hideCursor() const { setMouse(true);  };
   void showCursor() const { setMouse(false); };

   // Get various key events
   int  isDown()        const { return isDownPress;  };
   int  isUp()          const { return isUpPress;    };
   int  isLeft()        const { return isLeftPress;  };
   int  isRight()       const { return isRightPress; };
   bool isSpace()       const { return isSpacePress; };
   bool isC()           const { return isCPress;     };
   bool isX()           const { return isXPress;     };
   bool isMouseClicked()const { return isMouseClick; };
   bool isMouseRightClicked() const { return isMouseRightClick; };
   bool isMouseMoved()  const { return isMouseMoving;};
   bool isBigX()        const { return isBigXPress;  };
   bool isEnter()       const { return isEnterPress; };
   bool isBigQ()        const { return isBigQPress;  };
   bool isM()           const { return isMPress;     };
   bool isSlash()       const { return isSlashPress; };
   bool isQuestion()    const { return isQuestionPress; };
   bool isBigS()        const { return isBigSPress;  };
   bool isS()           const { return isSPress;     };
   bool isF5()          const { return isF5Press;    };
   bool isF9()          const { return isF9Press;    };
   bool isCtrl()        const { return isCtrlPress;  };
   bool isAlt()         const { return isAltPress;   };
   bool isShift()       const { return isShiftPress; };
   bool isZ()           const { return isZPress;     };

   /*
   bool is()           const { return isPress;    };
   */
    // add key here

   void setMouseLoc(int x, int y){
      mouseLoc.first  = x;
      mouseLoc.second = y;
   }

   std::pair<int, int> getMouseLoc() const {
    return mouseLoc;
   };


   static void *p;                   // for client
   static void (*callBack)(const Interface *, void *);


private:
   void initialize(int argc, char ** argv, const char * title);

   static bool         initialized;  // only run the constructor once!
   static double       timePeriod;   // interval between frame draws
   static unsigned int nextTick;     // time (from clock()) of our next draw

   static int  isDownPress;          // is the down arrow currently pressed?
   static int  isUpPress;            //    "   up         "
   static int  isLeftPress;          //    "   left       "
   static int  isRightPress;         //    "   right      "
   static bool isSpacePress;         //    "   space      "
   static bool isCPress;             //    "   c          "
   static bool isXPress;             //    "   x          "
   static bool isMouseClick;         // is the left mouse button currently clicked?
   static bool isMouseRightClick;    // is the right mouse button clicked?
   static bool isMouseMoving;        // is the cursor moving right now?
   static bool isBigXPress;          //    "   X          "
   static bool isEnterPress;         // is enter pressed?
   static bool isBigQPress;
   static bool isMPress;
   static bool isSlashPress;
   static bool isQuestionPress;
   static bool isBigSPress;
   static bool isSPress;
   static bool isF5Press;
   static bool isF9Press;
   static bool isCtrlPress;
   static bool isAltPress;
   static bool isShiftPress;
   static bool isZPress;

   /*
   static bool isPress;
   */
   static std::pair<int, int> mouseLoc;

   // add key here
};

#endif // UI_INTERFACE_H