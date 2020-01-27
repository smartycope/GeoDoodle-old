#include "uiDraw.h"
#include <utility>
#include <vector>
#include <math.h>

#define BORDER_WIDTH 0 // how far away from the edge do the dots go
#define ARRAY_WIDTH 15 // the distance between each dots

class Array{
private:
    std::pair<int, int> cursorIndexLoc;
    std::pair<int, int> focusIndex;
    int arraySize; // how many dots does one side of the array have in it

public:
    Point array[40][40];
    //std::vector<Point, Point> array;
    //array.resize(40);

    Array(){
        arraySize = 40;
        generateArray();
        focusIndex.first = arraySize / 2;
        focusIndex.second = arraySize / 2;
    }
    Array(std::pair<int,int> focusedIndex){
        arraySize = 40;
        generateArray();
        focusIndex.first = arraySize / 2;
        focusIndex.second = arraySize / 2;
        focusIndex = focusedIndex;
    }
    
    void generateArray();
    void drawArray();
    void drawFocus(int radius);
    
    void setFocus(std::pair<int, int> where){
        focusIndex = where;
    }
    std::pair<int, int> getFocus(){
        return focusIndex;
    }
    void setFocusX(int x){
        focusIndex.first = x;
    }
    void setFocusY(int y){
        focusIndex.second = y;
    }
    int getFocusX(){
        return focusIndex.first;
    }
    int getFocusY(){
        return focusIndex.second;
    }
    void updateCursorLoc(){
        // get mouse location here
    }
    std::pair<int, int> getCursorIndex(){
        return cursorIndexLoc;
    }
    std::pair<int, int> pointToIndex(Point hi){
        std::pair<int, int> tmp;
        tmp.first  = int(round(float(hi.getX()) / float(ARRAY_WIDTH)));
        tmp.second = int(round(float(hi.getY()) / float(ARRAY_WIDTH)));
        return tmp;
    }
    int getArraySize(){
        return arraySize;
    }

    Point operator [] (std::pair<int, int> index){
        return array[index.first][index.second];
    }
};