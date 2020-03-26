#include "uiDraw.h"
#include <utility>
#include <vector>
#include <math.h>
#include <fstream>
#include "glutCallbacks.h"

// #define DOT_SPREAD 16 // the distance between each dots - everything is easier if this is even.

class Array{
protected:
    std::pair<int, int> focusLoc;

public:
    nlohmann::json settings;
    
     Array(){
        settings = getSettings();
        settings["dot spread"] = pixCount();
        // focusLoc.first = (int)settings["dot spread"];
        // focusLoc.second = (int)settings["dot spread"];
        // debugVar("dot spread", settings["dot spread"]);
    }

    // Array(){
    //     settings = getSettings();
    //     settings["dot spread"] = pixCount();
    // }
    
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
};