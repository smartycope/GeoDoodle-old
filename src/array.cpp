#include "array.h"
#include <iostream>

void Array::drawArray(){
    for(int k = -getWindowWidth(); k <= getWindowWidth(); k += (int)settings["dot spread"]){
        for(int i = getWindowWidth(); i >= -getWindowWidth(); i -= (int)settings["dot spread"]){
            std::pair<int, int> tmp(k, i);
            drawDot(tmp);
        }
    }
}

void Array::drawFocus(int radius){
    //glColor3f(0, 0, 1);
    drawCircle(focusLoc, radius);
    //glColor3f(0, 0, 0);
}