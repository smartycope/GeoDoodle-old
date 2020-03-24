#include "array.h"
#include <iostream>

/* 
void Array::generateArray(){
    for(int k = 0; k < arraySize; ++k){
        for(int i = 0; i < arraySize; ++i){
            Point dot(-200 + BORDER_WIDTH - 2 + (k * ARRAY_WIDTH), 200 - BORDER_WIDTH - (i * ARRAY_WIDTH));
            array[k][i] = dot;
        }
    }
}
 */
void Array::drawArray(){
    /* for(int k = topLeft.first; k <= bottomRight.first; k += dotSpread){
        for(int i = topLeft.second; i >= bottomRight.second; i -= dotSpread){
            std::pair<int, int> tmp(k, i);
            drawDot(tmp);
            std::cout << "Drawing dot at " << k << ", " << i << std::endl;
        }
    } */
    for(int k = -200; k <= 200; k += dotSpread){
        for(int i = 210; i >= -210; i -= dotSpread){
            std::pair<int, int> tmp(k, i);
            drawDot(tmp);
            // std::cout << "Drawing dot at " << k << ", " << i << std::endl;
        }
    }
}

void Array::drawFocus(int radius){
    //glColor3f(0, 0, 1);
    drawCircle(focusLoc, radius);
    //glColor3f(0, 0, 0);
}