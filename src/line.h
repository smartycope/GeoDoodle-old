#include <utility>
#include <iostream>
#include "array.h"
#include "uiDraw.h"

class Line:public Array{
private:
    std::pair<std::pair<int, int>, std::pair<int, int>> indexes;

public:
    bool isFinished;

    Line(){
        indexes.first.first  = 0;
        indexes.first.second = 0;
        indexes.second.first = 0;
        indexes.second.second= 0;
        isFinished = false;
    }

    Line(std::pair<int, int> start){
        indexes.first.first  = start.first;
        indexes.first.second = start.second;
        indexes.second.first = 0;
        indexes.second.second= 0;
        isFinished = false;
    }

    Line(std::pair<int, int> start, std::pair<int, int> end){
        indexes.first.first   =  start.first;
        indexes.first.second  = start.second;
        indexes.second.first  =    end.first;
        indexes.second.second =   end.second;
        isFinished = true;
    }

    void drawMyLine(){
        drawLine(array[indexes.first.first][indexes.first.second],
                 array[indexes.second.first][indexes.second.second],
                 0.0, 0.0, 0.0);
    }

    void finish(std::pair<int, int> end){
        indexes.second = end;
        done();
    }

    bool getFinished(){
        return isFinished;
    }

    void done(){
        isFinished = true;
    }

    std::pair<std::pair<int, int>, std::pair<int, int>> getIndexes(){
        return indexes;
    }
};