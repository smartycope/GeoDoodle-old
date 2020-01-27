#include "array.h"

void Array::generateArray(){
    for(int k = 0; k < arraySize; ++k){
    for(int i = 0; i < arraySize; ++i){
            Point dot(-200 + BORDER_WIDTH - 2 + (k * ARRAY_WIDTH), 200 - BORDER_WIDTH - (i * ARRAY_WIDTH));
            array[k][i] = dot;
        }
    }
}

void Array::drawArray(){
    for(int k = 0; k < arraySize; ++k){
        for(int i = 0; i < arraySize; ++i){
            drawDot(array[k][i]);
        }
    }
}
/*
void Array::drawFocus(int x, int y, int radius){
    glColor3f(0, 0, 1);
    drawCircle(array[x][y], radius);
    glColor3f(0, 0, 0);
}
 */
void Array::drawFocus(int radius){
    //glColor3f(0, 0, 1);
    drawCircle(array[focusIndex.first][focusIndex.second], radius);
    //glColor3f(0, 0, 0);
}