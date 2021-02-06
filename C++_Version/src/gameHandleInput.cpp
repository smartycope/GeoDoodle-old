#include "game.h"
#include <cassert>
#include <iostream>
#include <algorithm>
#include <math.h>
#include <string>
#include <nlohmann/json.hpp>
#include <fstream>
#include <QFileDialog>

// #define NK_IMPLEMENTATION
// #include "nuklear.h"

#define HOW_TO_ROUND round // how to round the mouse to the nearest dot. options are round, floor, ceil, or trunc.
#define PNG_BACKGROUND_COLOR 255, 255, 255
#define PNG_WIDTH 500
#define PNG_HEIGHT 500


void Game::handleInput(const Interface& ui){
    if (ignoreMouse) {
        ui.hideCursor();
    }
    else{
        ui.showCursor();
    }

  // Left Key
	if (ui.isLeft()){
        // Left arrow code
		allowLeft++;
		if (allowLeft > (int)settings["key repeat speed"] or allowLeft == 1) {
            int shift;

            if (ui.isShift()) {
                shift = int((float)settings["dot spread"] / 2.0f);
                notOnDotSide = not notOnDotSide;
            }
            else if (notOnDotSide) {
                shift = int((float)settings["dot spread"] / 2.0f);
                notOnDotSide = false;
            }
            else {
                shift = (int)settings["dot spread"];
            }

			dots.setFocusX(dots.getFocusX() - shift);
		}
		ignoreMouse = true;
	}

  // not left key
	if (not bool(ui.isLeft())){
		// up arrow released code
		allowLeft = 0;
	}

  // right key
	if (ui.isRight()){
        // right arrow code
		allowRight++;// tmp.first = int(round(float(ui.getMouseLoc().first) / float(settings["dot spread"])) * float(settings["dot spread"])) + xAdjust;
		if (allowRight > (int)settings["key repeat speed"] or allowRight == 1){
            int shift;

            if (ui.isShift()) {
                shift = int((float)settings["dot spread"] / 2.0f);
                notOnDotSide = not notOnDotSide;
            }
            else if (notOnDotSide) {
                shift = int((float)settings["dot spread"] / 2.0f);
                notOnDotSide = false;
            }
            else {
                shift = (int)settings["dot spread"];
            }
			dots.setFocusX(dots.getFocusX() + shift);
		}
		ignoreMouse = true;
	}

  // not right key
	if (not bool(ui.isRight())){
		// up arrow released code
		allowRight = 0;
	}

  // up key
	if (ui.isUp()){
		// up arrow code
		allowUp++;
		if (allowUp > (int)settings["key repeat speed"] or allowUp == 1){
            int shift;

            if (ui.isShift()) {
                shift = int((float)settings["dot spread"] / 2.0f);
                notOnDotUp = not notOnDotUp;
            }
            else if (notOnDotUp) {
                shift = int((float)settings["dot spread"] / 2.0f);
                notOnDotUp = false;
            }
            else {
                shift = (int)settings["dot spread"];
            }
			dots.setFocusY(dots.getFocusY() + shift);
		}
		ignoreMouse = true;
	}

  // not up key
	if (not bool(ui.isUp())){
		// up arrow released code
		allowUp = 0;
	}

  // down key
	if (ui.isDown()){
		// down arrow code
		allowDown++;
		if (allowDown > (int)settings["key repeat speed"] or allowDown == 1){
            int shift;

            if (ui.isShift()) {
                shift = int((float)settings["dot spread"] / 2.0f);
                notOnDotUp = not notOnDotUp;
            }
            else if (notOnDotUp) {
                shift = int((float)settings["dot spread"] / 2.0f);
                notOnDotUp = false;
            }
            else {
                shift = (int)settings["dot spread"];
            }
			dots.setFocusY(dots.getFocusY() - shift);
		}
		ignoreMouse = true;
	}

  // not down key
	if (not bool(ui.isDown())){
		// up arrow released code
		allowDown = 0;
	}

  // end the current line or start a new one
	if (ui.isSpace()) {
		// spacebar code
         // are you still holding an unfinished line?
		if (pattern.empty() ? true : pattern.back().getFinished()){
			Line l(dots.getFocus());
			pattern.push_back(l);
            repeatLine();
		}
		else{
			pattern.back().finish(dots.getFocus());
            repeatLine();
        }
	}

  // end the current line and start a new one
	if (ui.isC()){
		// c code (not to be confused with C code)
        if (pattern.empty() ? true : pattern.back().getFinished()){
			Line s(dots.getFocus());
			pattern.push_back(s);
            repeatLine();
		}
		else{
			pattern.back().finish(dots.getFocus());
            repeatLine();repeatLine();
			Line d(dots.getFocus());
			pattern.push_back(d);
            repeatLine();
		}
	}

  // undo the last line or cancel the current line
	if ((ui.isX() or (ui.isCtrl() and ui.isZ())) and not pattern.empty()){
        if (not isBigErase.back() and drawMetaLines) {
            if(pattern.back().isFinished){
                for(int i = eraseCount; i; --i){
                    pattern.pop_back();
                }
                isBigErase.pop_back();
            }
        }
        else {
            if (isBigErase.size()){
                --isBigErase.back();
            }
        }
        pattern.pop_back();
        // std::cout << "isX() says: " << isBigErase.back() << std::endl;
	}

  // save the current pattern as a .png image
  if (ui.isS()){// and ui.isShift()){
    debug("You pressed ctrl+s");
    QFileDialog dialog;
    dialog.setFileMode(QFileDialog::AnyFile);
    auto file = dialog.getSaveFileName(nullptr, "Save Pattern", "/home/Robert/GeoDoodle/images", "PNG Image Files (*.png)");
    std::string fileName = file.toStdString();

    // iterate throught the pattern and find the outlying points in each direction
    int leftmost, rightmost, highest, lowest;
    int prevLeftmost, prevRightmost, prevHighest, prevLowest;

    // leftmost
    for(auto it = pattern.begin(); it != pattern.end(); ++it){
      if((*it).start.first < prevLeftmost){
        leftmost = (*it).start.first;
        prevLeftmost = (*it).start.first;
      }
      if((*it).end.first < prevLeftmost){
        leftmost = (*it).end.first;
        prevLeftmost = (*it).end.first;
      }
    }

    // rightmost
    for(auto it = pattern.begin(); it != pattern.end(); ++it){
      if((*it).start.first > prevRightmost){
        rightmost = (*it).start.first;
        prevRightmost = (*it).start.first;
      }
      if((*it).end.first > prevRightmost){
        rightmost = (*it).end.first;
        prevRightmost = (*it).end.first;
      }
    }

    // lowest
    for(auto it = pattern.begin(); it != pattern.end(); ++it){
      if((*it).start.second < prevLowest){
        lowest = (*it).start.second;
        prevLowest = (*it).start.second;
      }
      if((*it).end.second < prevLowest){
        lowest = (*it).end.second;
        prevLowest = (*it).end.second;
      }
    }

    // highest
    for(auto it = pattern.begin(); it != pattern.end(); ++it){
      if((*it).start.second > prevHighest){
        highest = (*it).start.second;
        prevHighest = (*it).start.second;
      }
      if((*it).end.second > prevHighest){
        highest = (*it).end.second;
        prevHighest = (*it).end.second;
      }
    }

    int width  = rightmost - leftmost;
    int height = highest - lowest;

    debugVar("rightmost", rightmost);
    debugVar("leftmost", leftmost);
    debugVar("highest", highest);
    debugVar("lowest", lowest);

    int xOffset = -((getWindowWidth()  / 2) + width);
    int yOffset = -((getWindowHeight() / 2) + height);

    debugVar("xOffset", xOffset);
    debugVar("yOffset", yOffset);

    if(not write_png_file(fileName.c_str(), generateImage(pattern, width, height, xOffset, yOffset, PNG_BACKGROUND_COLOR), width, height))
      std::cout << "Unable to save image for some reason.\n";
    else
      std::cout << "Succesfully wrote image!\n";

    // for reference
    // bool write_png_file(const char* file_name, const png_bytepp data, int width, int height);
    // png_bytepp generateImage(std::vector<Line> lines, int width, int height, unsigned char r, unsigned char g, unsigned char b);
  }

  // end the current line or start a new one
	if(ui.isMouseClicked()){
		// move the focus to the right place
		// don't make another line if you don't want it to
		if(rightLastClicked and pattern.back().getFinished())
			pattern.pop_back();
		rightLastClicked = false;

		//  cursor(ui.getMouseLoc().first, ui.getMouseLoc().second);
		// dots.setFocus(dots.pointToIndex(cursor));
        // dots.setFocus(ui.getMouseLoc());

		if (pattern.empty() ? true : pattern.back().getFinished()){
			Line p(dots.getFocus());
			pattern.push_back(p);
            repeatLine();
		}
		else{
			pattern.back().finish(dots.getFocus());
            repeatLine();
		}
        if (IS_DEBUG and (VERBOSE >= 3)) { std::cout << ui.getMouseLoc().first << ", " << ui.getMouseLoc().second << std::endl; }
        // debug();
	}

  // end the current line and start a new one
	if(ui.isMouseRightClicked()){
		rightLastClicked = true;
		// Point cursor(ui.getMouseLoc().first, ui.getMouseLoc().second);
		// dots.setFocus(dots.pointToIndex(cursor));

		if (pattern.empty() ? true : pattern.back().getFinished()){
			Line s(dots.getFocus());
			pattern.push_back(s);
            repeatLine();
		}
		else{
			pattern.back().finish(dots.getFocus());
            repeatLine();
			Line d(dots.getFocus());
			pattern.push_back(d);
            repeatLine();
		}
	}

  // if the mouse is being moved
	if(not ignoreMouse){
        std::pair<int, int> tmp; //(ui.getMouseLoc());

        // debugVar("true mouse location", ui.getMouseLoc());

        tmp.first  = int(HOW_TO_ROUND( float(ui.getMouseLoc().first)  / float(settings["dot spread"]) ) * float(settings["dot spread"])) + xAdjust;
        tmp.second = int(HOW_TO_ROUND( float(ui.getMouseLoc().second) / float(settings["dot spread"]) ) * float(settings["dot spread"])) + yAdjust;

        // debugVar("rounded mouse location", tmp);

		dots.setFocus(tmp);
	}

  // if the mouse is being moved
	if(ui.isMouseMoved()){
		ignoreMouse = false;
	}

  // erase the lines where connecting to where the focus is
	if(ui.isBigX()){
    // for (auto it = pattern.begin(); it != pattern.end(); it++){
    // check every line
    for (int i = 0; i < pattern.size(); i++){
        // find the focus
        if(((pattern[i].start.first  == dots.getFocus().first) and
            (pattern[i].start.second == dots.getFocus().second)) or
            ((pattern[i].end.first    == dots.getFocus().first) and
            (pattern[i].end.second   == dots.getFocus().second))) {

            // if the focus is within the metaLines area...
            // (commented out, because it should always be true if drawMetaLines is)
            if( (/* metaLines.size() and  */drawMetaLines /* and (numEnterPressed == 4) */) and
            ((dots.getFocus().first  <= metaLines.front().end.first)   and
              (dots.getFocus().first  >= metaLines.front().start.first) and
              (dots.getFocus().second <= metaLines.front().end.second)  and
              (dots.getFocus().second >= metaLines.back().start.second)) ){
                // pattern.erase(pattern.begin() + i);

                //        \|/ I don't think this is nessicary, but just in case.
                int xOffset1 = dots.getFocus().first  - metaLines.front().start.first;
                int yOffset1 = dots.getFocus().second - metaLines.front().start.second;

                int height1 = metaLines.front().start.second - metaLines.back().start.second;
                int width1  = metaLines.front().end.first - metaLines.front().start.first;

                // get every point in the repeated pattern
                for (int ys = yOffset1 - topLeft.second - (int)settings["offscreen amount"] - height1;
                        ys <= topLeft.second + yOffset1 + (int)settings["offscreen amount"] + height1 + 1;
                        ys += height1){

                    for (int xs = xOffset1 - bottomRight.first - (int)settings["offscreen amount"] - width1;
                                xs <= bottomRight.first + xOffset1 + (int)settings["offscreen amount"] + width1 + 1;
                                xs += width1){

                        // reiterate through every point and compare against xs and ys
                        for (int k = 0; k < pattern.size(); k++){
                            if((isCloseEnough(pattern[k].start.first,  xs + xAdjust + repeatedxAdjust, (int)settings["dot spread"]) and
                                isCloseEnough(pattern[k].start.second, ys + yAdjust + repeatedyAdjust, (int)settings["dot spread"])) or
                                (isCloseEnough(pattern[k].end.first,    xs + xAdjust + repeatedxAdjust, (int)settings["dot spread"]) and
                                isCloseEnough(pattern[k].end.second,   ys + yAdjust + repeatedyAdjust, (int)settings["dot spread"])) ) {

                                pattern.erase(pattern.begin() + k);
                            }
                        }
                    }
                }
            }

            // otherwise, just check if the mouse is on it.
            if (((pattern[i].start.first  == dots.getFocus().first) and
                 (pattern[i].start.second == dots.getFocus().second)) or
                ((pattern[i].end.first    == dots.getFocus().first) and
                 (pattern[i].end.second   == dots.getFocus().second))) {
            // if ((pattern[i].start == dots.getFocus()) or (pattern[i].end == dots.getFocus())){
            pattern.erase(pattern.begin() + i);
        }
      }
    }
  }

  // erase all the lines
  if(ui.isBigQ()){
      pattern.clear();
      metaLines.clear();
      drawMetaLines = false;
  }

  // toggle the meta box
  if (ui.isM()){
      drawMetaLines = not drawMetaLines;
  }

  // draw the menu
  if (ui.isSlash() or ui.isQuestion()){
    drawMenu = true;
    menuDelay = 0;
    // if(menuDelay <= MENU_DELAY * 3)
    //   ++menuDelay;
  } else{
    if(menuDelay >= MENU_DELAY){
      drawMenu = false;
      menuDelay = 0;
    }else
      ++menuDelay;
  }

  // save the pattern as a .json file
  if (ui.isF5()){
      QFileDialog dialog;
      dialog.setFileMode(QFileDialog::AnyFile);
      auto file = dialog.getSaveFileName(nullptr, "Save Pattern", "/home/Robert/GeoDoodle/saves", "GeoDoodle Pattern Files (*.gdl)"); //, "*.gdl");
      std::string fileName = file.toStdString();

      std::ofstream fout(fileName);
      if (fout.fail()) {
          std::cout << "Unable to open " << fileName << "\n";
      } else {

          nlohmann::json jsn;
          // jsn["dot spread"] = int(settings["dot spread"]);
          // jsn["dot spread"] = settings.get<int>("dot spread");
          jsn += nlohmann::json{{"dotspread", int(settings["dot spread"])}};
          // debug("dot spread settings", settings["dot spread"]);
          // std::cout << "dot spread settings = " << settings["dot spread"] << std::endl;
          // jsn.push_back("dot spread", settings["dot spread"]);
          for (auto it = pattern.begin(); it != pattern.end(); it++){
              (*it).to_json(jsn, (*it));
          }
          // jsn = pattern;
          fout << jsn.dump(3);
          fout.close();
          std::cout << "Done!\n";
      }
  }

  // load a .json pattern
  if (ui.isF9()){
      auto file = QFileDialog::getOpenFileName(0, "Open Pattern", "/home/Robert/Geodoodle/", "GeoDoodle Pattern Files (*.gdl)");
      std::string fileName = file.toStdString();

      std::ifstream fin(fileName);
      if (fin.fail()) {
          std::cout << "Unable to open " << fileName << "\n";
      } else {

          pattern.clear();

          nlohmann::json jsn;

          try{
              fin >> jsn;
              debug();
              nlohmann::json::iterator it = jsn.begin();

              std::cout << *it << std::endl;

              settings["dot spread"] = (*it)["dotspread"];

              for (++it; it != jsn.end(); ++it){
                  Line l;
                  (*it).at("startX").get_to(l.start.first);
                  (*it).at("startY").get_to(l.start.second);
                  (*it).at("endX").get_to(l.end.first);
                  (*it).at("endY").get_to(l.end.second);
                  l.isFinished = true;

                  pattern.push_back(l);
              }
              std::cout << "Done reading!\n";
              std::cout << "There are " << pattern.size() << " lines being drawn right now.\n";

          } catch (nlohmann::detail::type_error){
              std::cout << "Unable to read file: Incorrect file format.\n";
          }
          fin.close();
      }
  }

  // specify one outlying point of the pattern to repeat
  if(ui.isEnter()){
    metaLines.clear();

    if (not numEnterPressed){
      moon:
      boundsX.clear();
      boundsY.clear();
      corners.clear();
    }

    ++numEnterPressed;

    if (numEnterPressed < 4){
      boundsX.push_back(dots.getFocus().first);
      boundsY.push_back(dots.getFocus().second);
    }
    else if (numEnterPressed == 4){
      numEnterPressed = 0;

    boundsX.push_back(dots.getFocus().first);
    boundsY.push_back(dots.getFocus().second);

    // sort by x value
    std::sort(boundsX.begin(), boundsX.end());

    if (boundsX.front() == boundsX.back()){
      goto moon; // equivelent to a break
    }

    // set the leftmost to the smallest x, and the rightmost to the largest x
    corners["top left"].first     = boundsX.front();
    corners["bottom left"].first  = boundsX.front();

    corners["top right"].first    = boundsX.back();
    corners["bottom right"].first = boundsX.back();

    // sort by y value
    std::sort(boundsY.begin(), boundsY.end());

    if (boundsY.front() == boundsY.back()){
        goto moon; // equivelent to a break
    }

    // set the topmost to the largest y, and the bottommost to the smallest y
    corners["bottom left"].second  = boundsY.front();
    corners["bottom right"].second = boundsY.front();

    corners["top left"].second     = boundsY.back();
    corners["top right"].second    = boundsY.back();

    // now replicate the lines within that area everywhere

    std::vector<Line> newPattern;
    int width, height, xOffset, xEndOffset, yOffset, yEndOffset;
    // std::pair<int, int> topLeft1(-200, -200);
    std::pair<int, int> topLeft1(-getWindowWidth(), getWindowHeight());
    bool first = true;
    std::pair<int, int> start;

    if (not pattern.back().isFinished){
      pattern.pop_back();
    }

    // first find everything not inside the area we just defined
    for (; pattern.size(); pattern.pop_back()){
      drawMetaLines = true;

    // if the line is inside the area...
      if(((pattern.back().start.first  <= corners["top right"   ].first ) and
          (pattern.back().start.first  >= corners["top left"    ].first ) and
          (pattern.back().start.second <= corners["top right"   ].second) and
          (pattern.back().start.second >= corners["bottom right"].second))or // <--
          // 'and' for both points must be inside the area, 'or' if only one point has to be inside the area.
         ((pattern.back().end.first  <= corners["top right"   ].first ) and
          (pattern.back().end.first  >= corners["top left"    ].first ) and
          (pattern.back().end.second <= corners["top right"   ].second) and
          (pattern.back().end.second >= corners["bottom right"].second)) ) {

        // Uncomment this line if you want the lines within the area to stay
        // if (VERBOSE >= 3) { newPattern.push_back(pattern.back());} // add the current Line to newPattern

        // relate the start points to the top left corner, and the end points to the start points
        xOffset = pattern.back().start.first  - corners["top left"].first;
        yOffset = pattern.back().start.second - corners["top left"].second;
        xEndOffset = pattern.back().end.first  - pattern.back().start.first;
        yEndOffset = pattern.back().end.second - pattern.back().start.second;

        height = corners["top left"].second - corners["bottom left"].second;
        width  = corners["top right"].first - corners["top left"].first;

        // optimization note: add a bool that makes it so it only evluates topLeft1 once
        std::pair<int, int> optTopLeft(dots.centerDot.first - (width / 2), dots.centerDot.second + (height / 2));
        debugPair = optTopLeft;

        int prevXs = 500, prevYs = 500; // again, assuming dotspread < 500

        for(int xs = -(getWindowWidth() / 2) - DOTS_OFFSCREEN + xOffset;
                xs <= (getWindowWidth() / 2) + DOTS_OFFSCREEN + xOffset;
                xs += width){

          if ((abs(prevXs) - optTopLeft.first) > (abs(xs) - optTopLeft.first)){
              topLeft1.first = xs + repeatedxAdjust - xOffset;
              prevXs = xs;
          }

          for(int ys =   (getWindowHeight() / 2) + DOTS_OFFSCREEN + yOffset;
                  ys >= -(getWindowHeight() / 2) - DOTS_OFFSCREEN + yOffset;
                  ys -= height){

            std::pair<int, int> startPoint(xs + repeatedxAdjust, ys + repeatedyAdjust);
            std::pair<int, int> endPoint(xs + repeatedxAdjust + xEndOffset, ys + repeatedyAdjust + yEndOffset);

            Line tmp2(startPoint, endPoint);
            newPattern.push_back(tmp2);

            if ((abs(prevYs) - optTopLeft.second) > (abs(ys) - optTopLeft.second)){
              topLeft1.second = ys + repeatedyAdjust - yOffset;
              prevYs = ys;
            }
                // debugVar("Top left currently", topLeft1);
          } // end of ys loop
        } // end of xs loop
        debugVar("where topleft should be:", optTopLeft);
      } // end of if statement
    } // end of for loop

    // draw the box in the middle of the screen


    debugVar("height", height);
    debugVar("width", width);
    debugVar("top left corner of the box", topLeft1);

    // define the corners
    std::pair<int, int> topRight, bottomLeft, bottomRight1;

    topRight.first = topLeft1.first + width;
    topRight.second = topLeft1.second;
    bottomLeft.first = topLeft1.first;
    bottomLeft.second = topLeft1.second - height;
    bottomRight1.first = topLeft1.first + width;
    bottomRight1.second = topLeft1.second - height;

    // create lines from the corners
    Line right (topRight, bottomRight1);
    Line left  (bottomLeft, topLeft1);
    Line top   (topLeft1, topRight);
    Line bottom(bottomRight1, bottomLeft);

    // add them to be drawn
    metaLines.push_back(top);
    metaLines.push_back(right);
    metaLines.push_back(bottom);
    metaLines.push_back(left);

    // copy newPattern into pattern, so it can be drawn
    for (auto it = newPattern.begin(); it != newPattern.end(); it++){
        pattern.push_back(*it);
    }
  } // end of bounds if statement
  else
    assert(false); // There are more than 4 points in the boundsX vector.
	} // end of isEnter()
}
