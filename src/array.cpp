#include "array.h"
#include <iostream>


void Array::drawArray(){
    std::pair<int, int> prevCenter(500, 500); // this is assuming dotSpread > 500

    for(int x = -(getWindowWidth() / 2) - DOTS_OFFSCREEN;
            x <= (getWindowWidth() / 2) + DOTS_OFFSCREEN;
            x += int(settings["dot spread"])){
        for(int y =   (getWindowHeight() / 2) + DOTS_OFFSCREEN;
                y >= -(getWindowHeight() / 2) - DOTS_OFFSCREEN;
                y -= int(settings["dot spread"])){

            drawDot(std::pair<int, int>(x, y));

            if (findCenter){
                if(abs(x) < abs(prevCenter.first)){
                    centerDot.first = x;
                    prevCenter.first = x;
                }
                if(abs(y) < abs(prevCenter.second)){
                    centerDot.second = y;
                    prevCenter.second = y;
                    // debugVar("start point", std::pair<int, int>(((getWindowWidth() / 2) + DOTS_OFFSCREEN), ((getWindowHeight() / 2) + DOTS_OFFSCREEN)));
                }
                // debugVar(centerDot);
            }
        }
    }
    findCenter = false;
}

/*
void Array::drawArray(){
    int numXDots = ceil(float(getWindowWidth()  - (DOTS_OFFSCREEN * 2)) / float(settings["dot spread"]));
    int numYDots = ceil(float(getWindowHeight() - (DOTS_OFFSCREEN * 2)) / float(settings["dot spread"]));
    std::pair<int, int> prevCenter(numXDots, numYDots);

    for(int x = numXDots; x >= -numXDots; --x){
        for(int y = numYDots; y >= -numYDots; --y){
            drawDot(std::pair<int, int>(int(settings["dot spread"]) * x, int(settings["dot spread"]) * y));
            if (findCenter)
                if(abs(x) < prevCenter.first){
                    centerDot.first = x;
                }  // (x == int(round(numXDots / 2.0f))) and (y == int(round(numXDots / 2.0f)))){
                centerDot = {x, y};
            }
        }
    }
    findCenter = false;
}
*/

void Array::drawFocus(int radius){
    //glColor3f(0, 0, 1);
    drawCircle(focusLoc, radius);
    //glColor3f(0, 0, 0);
}