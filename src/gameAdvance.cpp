#include "game.h"
#include <iostream>

#define START_Y 180     // where should the text start 
#define START_X -190 

void Game::advance(){
	if (!drawMenu){
        dots.drawArray();
        dots.drawFocus(settings["focus radius"]);

        // draw all the lines - change this to use an iterator
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
        if (checkSettingsDelay > CHECK_SETTINGS_DELAY){
            nlohmann::json j = getSettings();
            
            if (settings != j) {
                setSettings(settings);
                dots.settings = settings;
            } else if (dots.settings != j){
                setSettings(dots.settings);
            }
        }

        // update the size of the window
        topLeft.first  = -getWindowWidth() / 2;
        topLeft.second =  getWindowHeight() / 2;
	    bottomRight.first  = getWindowWidth() / 2;
        bottomRight.second = -getWindowHeight() / 2;


        checkSettingsDelay++;
	}
    
	// explination screen
	else {        
        const std::string text =
        "Welcome to GeoDoodle!\n"
        "Use the mouse or the arrow keys to move, then click\n"
        "or press the space bar to start a line.\n\n"

        "x :\t undo or cancel the last line\n"
        "c :\t end a line and start a new one\n"
        "X :\t delete the lines over where the focus is\n"
        "Q :\t delete all lines\n"
        "? :\t display this help menu\n"
        "m :\t show/hide the box\n\n\n\n\n"

        "Please send any bug reports to smartycope@gmail.com\n"
        "Made by Copeland Carter";
        
        std::pair<int, int> here(START_X, START_Y);
        drawText(here, text);
	}
}
