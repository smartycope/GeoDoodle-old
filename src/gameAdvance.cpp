#include "game.h"
#include <iostream>

#define START_X -190 // where should the text start
#define START_Y 180
#define I_FEEL_LIKE_IT false

void Game::advance(){
	if (!drawMenu){

    dots.drawArray();
    dots.drawFocus(settings["focus radius"]);

    // draw all the lines - change this to use an iterator?
    for (int i = 0; i < pattern.size(); i++){
      if(pattern[i].isFinished){
        pattern[i].drawMyLine();
      }
    }

    // draw the line in progress
    if (pattern.empty() ? false : not pattern.back().isFinished){
      Line tmp(pattern.back().start, dots.getFocus());
      tmp.drawMyLine();
    }

    // draw meta lines - change this to use an iterator too
    if(not metaLines.empty() and drawMetaLines){
      for(int i = 0; i < metaLines.size(); i++){
        metaLines[i].drawMyLine();
      }
    }

    // draw all the lines in progress if we're repeating
    if (drawMetaLines and (boundsX.size() == 4)){
      for(auto it = tmpLines.begin(); it != tmpLines.end(); ++it){
        int xEndOffset = dots.getFocus().first  - pattern.back().start.first;
        int yEndOffset = dots.getFocus().second - pattern.back().start.second;

        std::pair<int, int> endPoint(xEndOffset + (*it).start.first, yEndOffset + (*it).start.second);
        (*it).finish(endPoint);
        (*it).drawMyLine();
      }
    }

    //check to see if the settings have changed after a delay. If so, update the settings variable
    if (checkSettingsDelay >= CHECK_SETTINGS_DELAY){
      // debug();
      checkSettingsDelay = 0;
      nlohmann::json j = getSettings();

      if (settings != j) {
        setSettings(settings);
        dots.settings = settings;
      } else if (dots.settings != j){
        setSettings(dots.settings);
      }
    }

    // update the size of the window
    topLeft.first  = -getWindowWidth()  / 2;
    topLeft.second =  getWindowHeight() / 2;
    bottomRight.first  = getWindowWidth() / 2;
    bottomRight.second = -getWindowHeight() / 2;

    xAdjust = dots.centerDot.first + 1;
    yAdjust = dots.centerDot.second + 1;

     // called once at the beginning of the program, then again if needed (i.e. when the window resizes)
    if (recenter){
      dots.findCenter = true;
      recenter = false;
    }

    checkSettingsDelay++;

    if(IS_DEBUG and I_FEEL_LIKE_IT and (VERBOSE >= 2)){
      // constant
      // debug();
      if((debugPair.first != 500) and (debugPair.second != 500)) { drawCircle(debugPair, 6); }

      // blinking
      if(checkSettingsDelay >= CHECK_SETTINGS_DELAY / 2){
        // drawCircle(std::pair<int, int>(0, 0), 6);
      }

      // periodic
      if(checkSettingsDelay == CHECK_SETTINGS_DELAY - 2){
        // dots.findCenter = true;
      }

      // once, at the begining of the program
      if(first and (VERBOSE >= 3) ){
        debugVar("xAdjust", xAdjust);
        debugVar("yAdjust", yAdjust);
        debugVar("Center", dots.centerDot);
        debugVar("Dot Spread", int(settings["dot spread"]));
        debugVar("Window width", int(settings["start width"]));
        debugVar("Window height", int(settings["start height"]));
        debugVar("bind point", std::pair<int, int>(((getWindowWidth() / 2) + DOTS_OFFSCREEN), ((getWindowHeight() / 2) + DOTS_OFFSCREEN)));
        debug();
        first = false;
      }

      // once, a ways into the program
      if(first2 and (checkSettingsDelay == CHECK_SETTINGS_DELAY - 5) and (VERBOSE >= 3)){
        debugVar("xAdjust", xAdjust);
        debugVar("yAdjust", yAdjust);
        debugVar("Center", dots.centerDot);
        debugVar("Dot Spread", int(settings["dot spread"]));
        debugVar("Window width", int(settings["start width"]));
        debugVar("Window height", int(settings["start height"]));
        debugVar("bind point", std::pair<int, int>(((getWindowWidth() / 2) + DOTS_OFFSCREEN), ((getWindowHeight() / 2) + DOTS_OFFSCREEN)));
        first2 = false;
      }
    }
  }
	// explination screen
  else {
    const std::string text =
    "Welcome to GeoDoodle!\n"
    "Use the mouse or the arrow keys to move, then click\n"
    "or press the space bar to start a line.\n\n"

    "x :\t Undo or cancel the last line\n"
    "c :\t End a line and start a new one\n"
    "X :\t Delete the lines over where the focus is\n"
    "Q :\t Delete all lines\n"
    "? :\t Display this help menu\n"
    "m :\t Show/hide the box\n"
    "S :\t Save pattern as a .png image\n"
    "F5:\t Save pattern as a json file (reloadable)\n"
    "F9:\t Load a saved json pattern\n\n\n\n\n\n\n\n"


    "Please send any bug reports to smartycope@gmail.com\n"
    "Made by Copeland Carter";

    drawText(std::pair<int, int>(START_X, START_Y), text);
	}
}
