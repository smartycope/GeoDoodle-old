#include "uiDraw.h"
#include <utility>
#include <vector>
#include <math.h>

#define BORDER_WIDTH 0 // how far away from the edge do the dots go
#define DOT_SPREAD 16 // the distance between each dots - everything is easier if this is even.
#define ARRAY_SIZE 28

class Array{
protected:
    // std::pair<int, int> cursorLoc; // previously cursorIndexLoc
    std::pair<int, int> focusLoc; // previously focusLoc
    //int arraySize; // how many dots does one side of the array have in 

public:
    std::pair<int, int> topLeft;
    std::pair<int, int> bottomRight;
    int height;
    int width;
    int dotSpread;
    // std::vector<std::vector<std::pair<int, int>>> array;
    
    // defualt constructor just so line will work
     Array(){
        // arraySize = ARRAY_SIZE;
        // array.resize(arraySize);
        // for(auto it = array.begin(); it != array.end(); it++)
        // (*it).resize(arraySize);
        // generateArray();
        // tl = 0;
        // br = bottomRight;
        // focusLoc.first = (topLeft.first - bottomRight.first) / 2;
        // focusLoc.second = (topLeft.second - bottomRight.second) / 2;
        dotSpread = DOT_SPREAD;
        topLeft = {-200, 200};
        bottomRight = {200, -200};
    }

    Array(std::pair<int, int> tl, std::pair<int, int> br){
        dotSpread = DOT_SPREAD;
        tl = topLeft;
        br = bottomRight;
        width = (topLeft.first - bottomRight.first);
        height = (topLeft.second - bottomRight.second);
        focusLoc.first = width / 2;
        focusLoc.second = height / 2;
    }
    Array(std::pair<int, int> tl, std::pair<int, int> br, std::pair<int,int> focusedIndex){
        // arraySize = ARRAY_SIZE;
        // array.resize(arraySize);
        // for(auto it = array.begin(); it != array.end(); it++)
        //     (*it).resize(arraySize);
        // generateArray();
        dotSpread = DOT_SPREAD;
        tl = topLeft;
        br = bottomRight;
        width = (topLeft.first - bottomRight.first);
        height = (topLeft.second - bottomRight.second);
        focusLoc.first = width / 2;
        focusLoc.second = height / 2;
        focusLoc= focusedIndex;
    }
    
    // void generateArray();
    void drawArray();
    void drawFocus(int radius);
    
    void setFocus(std::pair<int, int> where){
        // if (where.first < 0)
        //     where.first = arraySize - 1;
        // if (where.first > arraySize - 1)
        //     where.first = 0;
        // if (where.second < 0)
        //     where.second = arraySize - 1;
        // if (where.second > arraySize - 1)
        //     where.second = 0;
        focusLoc = where;
    }
    std::pair<int, int> getFocus(){
        return focusLoc;
    }
    void setFocusX(int x){
        // if (x < 0)
        //     x = arraySize - 1;
        // if (x > arraySize - 1)
        //     x  = 0;

        focusLoc.first = x;
    }
    void setFocusY(int y){
        // if (y < 0)
        //     y = arraySize - 1;
        // if (y > arraySize - 1)
        //     y  = 0;

        focusLoc.second = y;
    }
    int getFocusX(){
        return focusLoc.first;
    }
    int getFocusY(){
        return focusLoc.second;
    }
    /*
    void updateCursorLoc(){
        // get mouse location here
    } 
    
    std::pair<int, int> getCursorIndex(){
        return cursorLoc;
    }
    std::pair<int, int> pointToIndex(Point hi){
        std::pair<int, int> tmp;
        tmp.first  = int(round(float(hi.getX()) / float(ARRAY_WIDTH)));
        tmp.second = int(round(float(hi.getY()) / float(ARRAY_WIDTH)));
        return tmp;
    } */
    // int getArraySize(){
    //     return arraySize;
    // }
    // // don't use
    // void setArraySize(const int &size){
    //     arraySize = size;
    // }

    // Point operator [] (std::pair<int, int> index){
    //     return array[index.first][index.second];
    // }
};