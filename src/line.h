#include <utility>
#include <iostream>
#include <nlohmann/json.hpp>
#include "array.h"
#include "uiDraw.h"

class Line:public Array{
public:
    // std::pair<std::pair<int, int>, std::pair<int, int>> indexes;
    std::pair<int, int> start;
    std::pair<int, int> end;
    bool isFinished;

    Line(){
        start.first = 0;
        start.second = 0;
        end.first = 0;
        end.second = 0;
        isFinished = false;
    }

    Line(std::pair<int, int> Start){
        start = Start;
        end.first = 0;
        end.second = 0;
        isFinished = false;
    }

    Line(std::pair<int, int> Start, std::pair<int, int> End){
        start = Start;
        end = End;
        isFinished = true;
    }

    void drawMyLine(){
        // if (indexes.first.first < 0)
        //     return;
        // if (indexes.first.first > arraySize - 1)
        //     return;
        // if (indexes.first.second < 0)
        //     return;
        // if (indexes.first.second > arraySize - 1)
        //     return;
        // if (indexes.second.first < 0)
        //     return;
        // if (indexes.second.first > arraySize - 1)
        //     return;
        // if (indexes.second.second < 0)
        //     return;
        // if (indexes.second.second > arraySize - 1)
        //     return;

        drawLine(start, end, 0.0, 0.0, 0.0);
    }

    void finish(std::pair<int, int> End){
        end = End;
        done();
    }

    bool getFinished(){
        return isFinished;
    }

    void done(){
        isFinished = true;
    }

    std::pair<std::pair<int, int>, std::pair<int, int>> getIndexes(){
        std::pair<std::pair<int, int>, std::pair<int, int>> indexes;
        indexes.first = start;
        indexes.second = end;
        return indexes;
    }

    void to_json(nlohmann::json& j, const Line& l) {
        j += nlohmann::json{{"startX", l.start.first},
                            {"startY", l.start.second},
                            {"endX", l.end.first},
                            {"endY", l.end.second}};
    }
};