#include "game.h"
#include <iostream>

// #define RADIUS 5	    // radius of the focus circle - in settings
#define CHECK_SETTINGS_DELAY 50 // how often you should compare the settings file to see if it's changed
#define START_Y 100     // where should the text start 
#define START_X -150
#define LINE_OFFSET -25 // how much should each line be offset
#define WELCOME_TEXT_1  "Welcome to GeoDoodle! Move the mouse or use the arrow keys,"
#define WELCOME_TEXT_2  "and then click or press the space bar to make a line."
#define X_INSTRUCT      "Press x to undo or cancel a line"
#define M_INSTRUCT      ""
#define BIG_X_INSTRUCT  ""
#define SLASH_INSTRUCT  ""
#define Q_INSTRUCT      ""
#define ENTER_INSTRUCT  ""
#define ENTER_INSTRUCT_2 ""
// #define _INSTRUCT      ""
#define CREDIT_TEXT     "Created by Copeland Carter."

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

        //check to see if the settings have changed. If so, update the settings variable
        if (checkSettingsDelay > CHECK_SETTINGS_DELAY){
            nlohmann::json j = getSettings();
            if ((settings != j) or (dots.settings != j)) {
                dots.settings = j;
                settings = j;
                checkSettingsDelay++;
            }
        }

        // update the size of the window
        topLeft.first  = -getWindowWidth() / 2;
        topLeft.second =  getWindowHeight() / 2;
	    bottomRight.first  = getWindowWidth() / 2;
        bottomRight.second = -getWindowHeight() / 2;
	}
    
	// explination screen
	else{
        /* 
		Point line1(START_X, START_Y);
		Point line2(START_X, START_Y + LINE_OFFSET);
		Point line3(START_X, START_Y + LINE_OFFSET * 2);
		Point line4(START_X, START_Y + LINE_OFFSET * 3);
        Point line5(START_X, START_Y + LINE_OFFSET * 4);
        Point line6(START_X, START_Y + LINE_OFFSET * 5);
        Point line7(START_X, START_Y + LINE_OFFSET * 6);
        Point line8(START_X, START_Y + LINE_OFFSET * 7);
        Point line9(START_X, START_Y + LINE_OFFSET * 8);
        Point line10(START_X, START_Y + LINE_OFFSET * 9);
        Point line11(START_X, START_Y + LINE_OFFSET * 10);
        Point line12(START_X, START_Y + LINE_OFFSET * 11);
        Point line13(START_X, START_Y + LINE_OFFSET * 12);

		drawText(line1, WELCOME_TEXT_1);
		drawText(line2, WELCOME_TEXT_2);
		drawText(line3, X_INSTRUCT);
        drawText(line4, Q_INSTRUCT);
        drawText(line5, M_INSTRUCT);
        drawText(line6, BIG_X_INSTRUCT);
        drawText(line7, SLASH_INSTRUCT);
        drawText(line8, ENTER_INSTRUCT);
        drawText(line9, ENTER_INSTRUCT_2);
        // drawText(line10, _INSTRUCT);
		drawText(line13, CREDIT_TEXT); */
	}
}
