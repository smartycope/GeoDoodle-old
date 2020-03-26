#include "game.h"
#include <cassert>
#include <iostream>
#include <algorithm>
#include <math.h>
#include <string>
#include <nlohmann/json.hpp>
#include <fstream>

/* 
*	Unitl I find some way in game to explain which keys do what...
* 	Arrow keys controls the focus (the circle)
*	Space finishes a line and then starts a new one
*	c starts and finishes a line
*	x cancels the current line/undo's the last line
*   X deletes all the lines your focus is on
*   Enter defines one corner of the area you want to repeat. Press it 4 times around your pattern to make it expand
*   Q clears all lines
*   m toggles meta lines
*   / and ? both display the menu of which buttons do what
*   f5 serializes and saves the pattern
*   f9 deserializes and prints the pattern
*/

void Game::handleInput(const Interface& ui){
    if (ignoreMouse) {
        ui.hideCursor();
    }
    else{
        ui.showCursor();
    }
    
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

	if (not bool(ui.isLeft())){
		// up arrow released code
		allowLeft = 0;
	}

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

	if (not bool(ui.isRight())){
		// up arrow released code
		allowRight = 0;
	}
	
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

	if (not bool(ui.isUp())){
		// up arrow released code
		allowUp = 0;
	}

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

	if (not bool(ui.isDown())){
		// up arrow released code
		allowDown = 0;
	}

	// Check for "Spacebar"
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
        if (IS_DEBUG) { std::cout << dots.getFocusX() << ", " << dots.getFocusY() << std::endl; };
        // debug();
	}

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

	if(not ignoreMouse){
		// Point curser(ui.getMouseLoc().first, ui.getMouseLoc().second);
        std::pair<int, int> tmp;//(ui.getMouseLoc());

        tmp.first  = int(floor( float(ui.getMouseLoc().first)  / float(settings["dot spread"]) ) * float(settings["dot spread"])) + xAdjust;
        tmp.second = int(floor( float(ui.getMouseLoc().second) / float(settings["dot spread"]) ) * float(settings["dot spread"])) + yAdjust;

        // tmp.first  = int(round( float(ui.getMouseLoc().first)  / float(settings["dot spread"]) ) * float(settings["dot spread"])) + xAdjust;
        // tmp.second = int(round( float(ui.getMouseLoc().second) / float(settings["dot spread"]) ) * float(settings["dot spread"])) + yAdjust;

		dots.setFocus(tmp);
	}

	if(ui.isMouseMoved()){
		ignoreMouse = false;
	}


    // if ((((*it).start.first  == dots.getFocus().first) and 
    //      ((*it).start.second == dots.getFocus().second)) or
    //     (((*it).end.first    == dots.getFocus().first) and
    //      ((*it).end.second   == dots.getFocus().second))) {

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
                                if((isCloseEnough(pattern[k].start.first, xs + xAdjust + 2, (int)settings["dot spread"]) and
                                    isCloseEnough(pattern[k].start.second, ys + xAdjust + 2, (int)settings["dot spread"])) or
                                   (isCloseEnough(pattern[k].end.first, xs + xAdjust + 2, (int)settings["dot spread"]) and
                                    isCloseEnough(pattern[k].end.second, ys + xAdjust + 2, (int)settings["dot spread"])) ) {
                                    
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

    if(ui.isBigQ()){
        pattern.clear();
        metaLines.clear();
        drawMetaLines = false;
    }

    if (ui.isM()){
        drawMetaLines = not drawMetaLines;
    }

    if (ui.isSlash() or ui.isQuestion()){
        drawMenu = true;
    }

    if (not ui.isSlash() and not ui.isQuestion()){
        drawMenu = false;
    }

    if (ui.isF5()){
        std::string fileName;
        std::string fileName2;
        std::cout << "\nPlease enter a file name here: ";
        std::getline(std::cin, fileName);
        // std::cin  >> fileName;
        // if(fileName.find('.')){
        //     fileName = "../saves/" + fileName;
        // }
        // else{
        //     fileName = "../saves/" + fileName + ".gdl";
        // }
        fileName2 = fileName;
        fileName = "../saves/" + fileName + ".gdl";
        std::ofstream fout(fileName);

        nlohmann::json jsn;
        for (auto it = pattern.begin(); it != pattern.end(); it++){
            (*it).to_json(jsn, (*it));
        }
        // jsn = pattern;
        fout << jsn.dump(3);
        fout.close();
        std::cout << "Done! Look for \'" << fileName2 << ".gdl\' in the saves folder.\n";
        std::cout << '(' << fileName << ")\n";
    }

    if (ui.isF9()){
        pattern.clear();
        std::string fileName;
        std::string fileName2;
        std::cout << "\nPlease enter a file name to open: ";
        std::getline(std::cin, fileName);
        // if(fileName.find('.')){
        //     fileName = "../saves/" + fileName;
        // }
        // else{
        //     fileName = "../saves/" + fileName + ".gdl";
        // }
        fileName2 = fileName;
        fileName = "../saves/" + fileName + ".gdl";
        std::ifstream fin(fileName);
        if (fin.fail()) { std::cout << "Unable to open " << fileName2 << ".gdl\n"; }

        nlohmann::json jsn;
        fin >> jsn;
        int debug = 0;

        for (nlohmann::json::iterator it = jsn.begin(); it != jsn.end(); ++it){
            Line l;
            (*it).at("startX").get_to(l.start.first);
            (*it).at("startY").get_to(l.start.second);
            (*it).at("endX").get_to(l.end.first);
            (*it).at("endY").get_to(l.end.second);
            l.isFinished = true;

            pattern.push_back(l);
        }
        fin.close();
        std::cout << "Done reading!\n";
        std::cout << "There are " << pattern.size() << " lines being drawn right now.\n";
    }

	if(ui.isEnter()){
        metaLines.clear();

        if (not numEnterPressed){
            moon:
            boundsX.clear();
            boundsY.clear();
            corners.clear();
        }

        ++numEnterPressed;

		// if (boundsX.size() < 3){
        if (numEnterPressed < 4){
			boundsX.push_back(dots.getFocus().first);
			boundsY.push_back(dots.getFocus().second);
		}
		// else if (boundsX.size() == 4){
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
            std::pair<int, int> topLeft1(-200, -200);
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
                    // newPattern.push_back(pattern.back()); // add the current Line to newPattern

                    // relate the start points to the top left corner, and the end points to the start points
                    xOffset = pattern.back().start.first  - corners["top left"].first;
                    yOffset = pattern.back().start.second - corners["top left"].second;
                    xEndOffset = pattern.back().end.first  - pattern.back().start.first;
                    yEndOffset = pattern.back().end.second - pattern.back().start.second;

                    height = corners["top left"].second - corners["bottom left"].second;
                    width  = corners["top right"].first - corners["top left"].first;

                    // std::cout << ++debug << "\nxOffset = " << xOffset << "\nyOffset = " << yOffset 
                            //   << "\nxEndOffset = " << xEndOffset << "\nyEndOffset = " << yEndOffset << std::endl << std::endl;

                    // iterate through the array by the offset and create new points at every junction
                    for (int ys =  yOffset - (getWindowHeight() / 2) - (int)settings["offscreen amount"] - height;
                             ys <= yOffset + (getWindowHeight() / 2) + (int)settings["offscreen amount"] + height;
                             ys += height){
                        if(ys < abs(topLeft1.second))
                            topLeft1.second = ys + yAdjust + repeatedyAdjust;
                        for (int xs =  xOffset - (getWindowWidth() / 2) - (int)settings["offscreen amount"] - width;
                                 xs <= xOffset + (getWindowWidth() / 2) + (int)settings["offscreen amount"] + width;
                                 xs += width){

                            std::pair<int, int> startPoint(xs + xAdjust + repeatedxAdjust, ys + yAdjust + repeatedyAdjust);
                            std::pair<int, int> endPoint(xs + xEndOffset + xAdjust + repeatedxAdjust, ys + yEndOffset + yAdjust + repeatedyAdjust);
                            Line tmp2(startPoint, endPoint);
                            newPattern.push_back(tmp2);

                            if(xs < abs(topLeft1.first))
                                topLeft1.first = xs + xAdjust + repeatedxAdjust - xOffset;
                        }
                    }
                } // end of if statement
		    } // end of for loop

            // draw the box in the middle of the screen

            // topLeft1.first = (round((float)getWindowWidth() / (float)width) * (float)width) / 2;
            // topLeft1.first = (round((float)getWindowHeight() / (float)height) * (float)height) / 2;
            debugVar("height", height);
            debugVar("width", width);

            // for (int ys = -(getWindowHeight() / 2) - (int)settings["offscreen amount"] - height;
            //          ys <= (getWindowHeight() / 2) + (int)settings["offscreen amount"] + height;
            //          ys += height) {
            //     for (int xs = -(getWindowWidth() / 2) - (int)settings["offscreen amount"] - width;
            //              xs <= (getWindowWidth() / 2) + (int)settings["offscreen amount"] + width;
            //              xs += width) {

            //         // if(isCloseEnough(xs, xAdjust, topLeft1.first))
            //         //     topLeft1.first = xs;
            //         // if(isCloseEnough(ys, yAdjust, topLeft1.second))
            //         //     topLeft1.second = ys;
            //         if(abs(xs) > topLeft1.first)
            //             topLeft1.first = xs;
            //         if(abs(ys) > topLeft1.second)
            //             topLeft1.second = ys;
            //     }
            // }




            // start.first  = (int)settings["offscreen amount"] + width + getWindowWidth();
            // start.first = abs((getWindowWidth() / 2) - (int)settings["offscreen amount"] - width) + abs((getWindowWidth() / 2) + (int)settings["offscreen amount"] + height);
            // int fullWidth  = (((int)settings["offscreen amount"] + width)  * 2) + getWindowWidth();
            // int fullHeight = (((int)settings["offscreen amount"] + height) * 2) + getWindowHeight();
            // start.second = abs((getWindowHeight() / 2) - (int)settings["offscreen amount"] - height) + abs((getWindowHeight() / 2) + (int)settings["offscreen amount"] + height);
            

            // std::cout << "start = " << start.first << ", " << start.second << std::endl;
            // topLeft1.first = (((start.first / 2) / width) * width) - (start.first / 2);
            // topLeft1.second = (((start.second / 2) / height) * height) - (start.second / 2);
            // topLeft1.first  = int(round(((float)fullWidth / 2.0f) / (float)width)  * (float)width) - (fullWidth / 2);// - (start.first / 2);
            // topLeft1.second = int(round(((float)fullHeight/ 2.0f) / (float)height) * (float)height) - (fullHeight / 2);// - (start.second / 2);
            // topLeft1.first  = int(floor(float(width)  / float(settings["dot spread"])) * float(settings["dot spread"])) + xAdjust;
            // topLeft1.second = int(floor(float(height) / float(settings["dot spread"])) * float(settings["dot spread"])) + yAdjust;
            debugVar("top left corner of the box", topLeft1);

            // define the corners
            std::pair<int, int> topRight, bottomLeft, bottomRight1;

            // std::cout << "The topLeft corner of the box is: " << topLeft1.first << ", " << topLeft1.second << std::endl;
            // std::cout << "Height = " << height << " | Width = " << width << std::endl;
            topRight.first  = topLeft1.first + width;
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