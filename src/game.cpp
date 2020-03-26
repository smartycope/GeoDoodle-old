#include "game.h"
#include <cassert>
#include <iostream>
#include <algorithm>
#include <math.h>

// #define OFF_SCREEN_BORDER_AMOUNT 10 // how far off screen stuff goes

// std::pair<int, int> Game::bottomRight;
// std::pair<int, int> Game::topLeft;

Game::Game() : dots(Array()) {
	topLeft.first  = -getWindowWidth() / 2;
    topLeft.second =  getWindowHeight() / 2;
	bottomRight.first  = getWindowWidth() / 2;
    bottomRight.second = -getWindowHeight() / 2;

    isBigErase.push_back(-1);

    settings = getSettings();

    settings["dot spread"] = pixCount();
    xAdjust = int((float)settings["dot spread"] / 3.0f) + 1;
    yAdjust = int((float)settings["dot spread"] / 3.0f) + 9;

    // dots.setFocus(std::pair<int, int>(int(settings["dot spread"]), int(settings["dot spread"])));
    // dots.setFocus(std::pair<int, int>(100, 100));

    
    debugVar("dot spread", (int)settings["dot spread"]);
    debugVar("xAdjust", xAdjust);
    debugVar("yAdjust", yAdjust);
}

// bet you can't guess what this does!
bool Game::isOnScreen(const std::pair<int, int> &point){
	return (point.first >= topLeft.first - (int)settings["off screen amount"]
		 && point.first <= bottomRight.first + (int)settings["off screen amount"]
		 && point.second >= bottomRight.second - (int)settings["off screen amount"]
		 && point.second <= topLeft.second + (int)settings["off screen amount"]);
}

void Game::repeatLine(){
    if (pattern.back().isFinished){
        tmpLines.clear();
        if (drawMetaLines and (boundsX.size() == 4)){
            if(((pattern.back().start.first  <= metaLines.front().end.first)   and
                (pattern.back().start.first  >= metaLines.front().start.first) and
                (pattern.back().start.second <= metaLines.front().end.second)  and
                (pattern.back().start.second >= metaLines.back().start.second)) or // <--
                // 'and' for both points must be inside the area, 'or' if only one point has to be inside the area.
               ((pattern.back().end.first  <= metaLines.front().end.first)   and
                (pattern.back().end.first  >= metaLines.front().start.first) and
                (pattern.back().end.second <= metaLines.front().end.second)  and
                (pattern.back().end.second >= metaLines.back().start.second)) ) {

                isBigErase.push_back(0);
                
                std::vector<Line> newPattern;
                int width, height, xOffset, xEndOffset, yOffset, yEndOffset;
                
                // Uncomment this line if you want the lines within the area to stay
                // newPattern.push_back(pattern.back()); // add the current Line to newPattern

                // relate the start points to the top left corner, and the end points to the start points
                xOffset = pattern.back().start.first  - metaLines.front().start.first;
                yOffset = pattern.back().start.second - metaLines.front().start.second;
                xEndOffset = pattern.back().end.first  - pattern.back().start.first;
                yEndOffset = pattern.back().end.second - pattern.back().start.second;

                height = metaLines.front().start.second - metaLines.back().start.second;
                width  = metaLines.front().end.first - metaLines.front().start.first;

                eraseCount = 0;

                // iterate through the array by the offset and create new points at every junction
                for (int ys =  yOffset - (getWindowHeight() / 2) - (int)settings["offscreen amount"] - height;
                         ys <= yOffset + (getWindowHeight() / 2) + (int)settings["offscreen amount"] + height;
                         ys += height){
                    for (int xs =  xOffset - (getWindowWidth() / 2) - (int)settings["offscreen amount"] - width;
                             xs <= xOffset + (getWindowWidth() / 2) + (int)settings["offscreen amount"] + width;
                             xs += width){                                

                        std::pair<int, int> startPoint(xs + xAdjust + 2, ys + yAdjust + 2);
                        std::pair<int, int> endPoint(xs + xEndOffset + xAdjust + 2, ys + yEndOffset + yAdjust + 2);
                        Line tmp2(startPoint, endPoint);
                        newPattern.push_back(tmp2);
                        ++eraseCount;
                    }
                }

                for (auto it = newPattern.begin(); it != newPattern.end(); it++){
                    pattern.push_back(*it);
                }
            } // end of if statement
            else{
                if (isBigErase.back() >= 0){
                    ++isBigErase.back();// = isBigErase.back() + 1;
                }
            }        
        }
    }
    else { // if the line is unfinished
        if (drawMetaLines and (boundsX.size() == 4)){
            if( (pattern.back().start.first  <= metaLines.front().end.first)   and
                (pattern.back().start.first  >= metaLines.front().start.first) and
                (pattern.back().start.second <= metaLines.front().end.second)  and
                (pattern.back().start.second >= metaLines.back().start.second) ) {

                // isBigErase.push_back(0);

                // relate the start points to the top left corner, and the end points to the start points
                int xOffset = pattern.back().start.first  - metaLines.front().start.first;
                int yOffset = pattern.back().start.second - metaLines.front().start.second;
                // int xEndOffset = dots.getFocus().first  - pattern.back().start.first;
                // int yEndOffset = dots.getFocus().second - pattern.back().start.second;

                int height = metaLines.front().start.second - metaLines.back().start.second;
                int width  = metaLines.front().end.first - metaLines.front().start.first;

                // iterate through the array by the offset and create new points at every junction
                for (int ys =  yOffset - (getWindowHeight() / 2) - (int)settings["offscreen amount"] - height;
                         ys <= yOffset + (getWindowHeight() / 2) + (int)settings["offscreen amount"] + height;
                         ys += height){
                    for (int xs =  xOffset - (getWindowWidth() / 2) - (int)settings["offscreen amount"] - width;
                             xs <= xOffset + (getWindowWidth() / 2) + (int)settings["offscreen amount"] + width;
                             xs += width){

                        std::pair<int, int> startPoint(xs + xAdjust + repeatedxAdjust, ys + yAdjust + repeatedyAdjust);
                        Line tmp3(startPoint);
                        tmpLines.push_back(tmp3);
                    }
                }
            } // end of if statement
            else {
                if (isBigErase.back() >= 0){
                    ++isBigErase.back();
                }
            }
        }
    }
}