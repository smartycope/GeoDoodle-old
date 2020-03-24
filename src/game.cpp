#include "game.h"
//#include "uiDraw.h"
//#include "uiInteract.h"
//#include "line.h"
#include <cassert>
#include <iostream>
#include <algorithm>
#include <math.h>

#define OFF_SCREEN_BORDER_AMOUNT 10 // how far off screen stuff goes

std::pair<int, int> center(0, 0);
std::pair<int, int> Game::bottomRight;
std::pair<int, int> Game::topLeft;

Game::Game(const std::pair<int, int> &tl, const std::pair<int, int> &br) :
dots(Array(tl, br)) {
	topLeft = tl;
	bottomRight = br;
    isBigErase.push_back(-1);
}

Game :: ~Game(){ }

/**************************************************************************
 * GAME :: IS ON SCREEN
 * Determines if a given point is on the screen.
 **************************************************************************/
bool Game::isOnScreen(const std::pair<int, int> &point){
	return (point.first >= topLeft.first - OFF_SCREEN_BORDER_AMOUNT
		 && point.first <= bottomRight.first + OFF_SCREEN_BORDER_AMOUNT
		 && point.second >= bottomRight.second - OFF_SCREEN_BORDER_AMOUNT
		 && point.second <= topLeft.second + OFF_SCREEN_BORDER_AMOUNT);
}

bool Game::isCloseEnough(int from, int to, int tolerance){
    if( (from < (to + tolerance)) and
        (from > (to - tolerance)) )
            return true;
    else
        return false;       
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
                for (int ys = yOffset - topLeft.second - OFF_SCREEN_AMOUNT - height;
                        ys <= topLeft.second + yOffset + OFF_SCREEN_AMOUNT + height + 1;
                        ys += height){
                    for (int xs = xOffset - bottomRight.first - OFF_SCREEN_AMOUNT - width;
                                xs <= bottomRight.first + xOffset + OFF_SCREEN_AMOUNT + width + 1;
                                xs += width){                                

                        std::pair<int, int> startPoint(xs + X_ADJUST + 2, ys + Y_ADJUST + 2);
                        std::pair<int, int> endPoint(xs + xEndOffset + X_ADJUST + 2, ys + yEndOffset + Y_ADJUST + 2);
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
                for (int ys = yOffset - topLeft.second - OFF_SCREEN_AMOUNT - height;
                        ys <= topLeft.second + yOffset + OFF_SCREEN_AMOUNT + height + 1;
                        ys += height){
                    for (int xs = xOffset - bottomRight.first - OFF_SCREEN_AMOUNT - width;
                                xs <= bottomRight.first + xOffset + OFF_SCREEN_AMOUNT + width + 1;
                                xs += width){
                        std::pair<int, int> startPoint(xs + X_ADJUST + 2, ys + Y_ADJUST + 2);
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



/* 
void Game::drawBorderPoints(){
    if (not borderIndexes.empty()){
		// assert(false);
		// std::cout << "Drawing points\n";
        for(int i = 0; i <= borderIndexes.size(); i++){
            drawRect(dots.array[borderIndexes[i].first][borderIndexes[i].second], 6, 6, 45);
        }
    }
} */

// My hacked functions of Brigham's that use message pack
// template<class Stored>
/* std::string Game::serialize(Stored content) {
  std::ostringstream os(std::ios::binary);
  msgpack::pack(os, src);
  return os.str();
} */

// template<class Stored1>
/* Stored1 Game::deserialize(const std::string &str) {
  std::ostringstream os;
  Stored1 structure;

  msgpack::object_handle oh = msgpack::unpack(str.data(), str.size());

    // deserialized object is valid during the msgpack::object_handle instance is alive.
  msgpack::object deserialized = oh.get();
  deserialized.convert(structure);  

//   std::istringstream SData(data, std::ios::binary);
//   cereal::PortableBinaryInputArchive Archive(SData);
//   Archive(structure);
  return deserialized; // if this doesn't work, maybe make this return structure?
} */
/* 
// template<class T>
void Game::saveDataToFile(T data, std::string fileName) {
//   std::ofstream os(fileName);
//   msgpack::pack(os, src);
    std::ofstream fout(fileName);
    nlohmann::json jsn(data);
    std::fout << jsn;
    fout.close();
}

// template<class T1>
T1 Game::getDataFromFile(const std::string &fileName) {
  std::ifstream fin(fileName);
  nlohmann::json jsn;
  fin >> jsn;
  return jsn.get<T1>();
} */

  /* T1 structure;
  msgpack::object_handle oh = msgpack::unpack(str.data(), str.size());
  msgpack::object deserialized = oh.get();
  deserialized.convert(structure);
  return deserialized; */
// }



// message pack API example
/* int main(void)
{
    msgpack::type::tuple<int, bool, std::string> src(1, true, "example");

    // serialize the object into the buffer.
    // any classes that implements write(const char*,size_t) can be a buffer.
    std::stringstream buffer;
    msgpack::pack(buffer, src);

    // send the buffer ...
    buffer.seekg(0);

    // deserialize the buffer into msgpack::object instance.
    std::string str(buffer.str());

    msgpack::object_handle oh =
        msgpack::unpack(str.data(), str.size());

    // deserialized object is valid during the msgpack::object_handle instance is alive.
    msgpack::object deserialized = oh.get();

    // msgpack::object supports ostream.
    std::cout << deserialized << std::endl;

    // convert msgpack::object instance into the original type.
    // if the type is mismatched, it throws msgpack::type_error exception.
    msgpack::type::tuple<int, bool, std::string> dst;
    deserialized.convert(dst);

    // or create the new instance
    msgpack::type::tuple<int, bool, std::string> dst2 =
        deserialized.as<msgpack::type::tuple<int, bool, std::string> >();

    return 0;
} */



// Brigham's functions for serialization
/* template<class Stored>
std::string serialize(Stored content, int flag = 0) {
  std::ostringstream os(std::ios::binary);
  if(flag == 0) {
    cereal::PortableBinaryOutputArchive ar(os);
    ar(content);
  } else {
    cereal::JSONOutputArchive ar(os);
    ar(content);
  }
  return os.str();
}

template<class Stored>
Stored deserialize(const std::string &data, int flag = 0) {
  std::ostringstream os;
  Stored structure;
  if(flag == 0) {
    std::istringstream SData(data, std::ios::binary);
    cereal::PortableBinaryInputArchive Archive(SData);
    Archive(structure);
  } else {
    std::istringstream SData(data);
    cereal::JSONInputArchive Archive(SData);
    Archive(structure);
  }
  return structure;
}

template<class T>
void saveDataToFile(T data, std::string fileName, int flag = 0) {
  std::ofstream outputStream(fileName);
  if(flag == 0) {
    cereal::PortableBinaryOutputArchive archive(outputStream);
    archive(data);
  } else if(flag == 1) {
    cereal::JSONOutputArchive archive(outputStream);
    archive(data);
  }
}

template<class T>
T getDataFromFile(const std::string &fileName, int flag = 0) {
  T data;
  std::ifstream outputStream(fileName);
  if(flag == 0) {
    cereal::PortableBinaryInputArchive archive(outputStream);
    archive(data);
  } else if(flag == 1) {
    cereal::JSONInputArchive archive(outputStream);
    archive(data);
  }
  return data;
}
 */
