#include "game.h"
//#include "uiDraw.h"
//#include "uiInteract.h"
//#include "line.h"
#include <cassert>
#include <iostream>
#include <algorithm>

using namespace std;

#define OFF_SCREEN_BORDER_AMOUNT 10 // how far off screen stuff goes
#define RADIUS 5			  		// radius of the focus circle
#define KEY_REPEAT_DELAY 9     		// 
#define TEXT_DISPLAY_DELAY 10 		// how long the welcome text stays on the screen 100+
#define WELCOME_TEXT_1 "Welcome to GeoDoodle! Move the mouse or use the arrow keys,"
#define WELCOME_TEXT_2 "and then click or press the space bar to make a line."
#define WELCOME_TEXT_3 "Press x to undo or cancel a line, and c or right click to"
#define WELCOME_TEXT_4 "automaticaly start a new line. Created by Copeland Carter."

/* 
*	Unitl I find some way to explain in game what which keys do what...
* 	Arrow keys controls the focus (the circle)
*	Space starts and finishes a line
*	c finishes a line and then starts a new one
*	x cancels the current line
 */

/***************************************
 * GAME CONSTRUCTOR
 ***************************************/
Point center(0, 0);
Point Game::bottomRight;
Point Game::topLeft;

Game::Game(const Point &tl, const Point &br) :
dots(Array()) {
	topLeft = tl;
	bottomRight = br;
}

/****************************************
 * GAME DESTRUCTOR
 ****************************************/
Game :: ~Game(){ }

void Game::advance(){
	if (timedFade >= TEXT_DISPLAY_DELAY){
		dots.drawArray();
		dots.drawFocus(RADIUS);

		//for (auto it = pattern.begin(); it != pattern.end(); it++){
		//	it.drawMyLine();
		//}
		
		// draw all the lines
		for (int i = 0; i < pattern.size(); i++){
			if(pattern[i].getFinished()){
			pattern[i].drawMyLine();
			}
		}

		// draw the line in progress
		if (pattern.empty() ? false : not pattern.back().getFinished()){
			Line tmp(pattern.back().getIndexes().first, dots.getFocus());
			tmp.drawMyLine();
		}
	}
	// starting screen
	else{
		//Point center(0,0);
		//drawRect(center, 150, 100, 0);

		Point line1(-180, 50);
		Point line2(-148, 25);
		Point line3(-155, 0);
		Point line4(-163, -25);

		drawText(line1, WELCOME_TEXT_1);
		drawText(line2, WELCOME_TEXT_2);
		drawText(line3, WELCOME_TEXT_3);
		drawText(line4, WELCOME_TEXT_4);
		
		timedFade++;
	}

	if(not metaLines.empty())
		for(int i = 0; i <= metaLines.size(); i++)
			metaLines[i].drawMyLine();

	drawBorderPoints();
}

/**************************************************************************
 * GAME :: IS ON SCREEN
 * Determines if a given point is on the screen.
 **************************************************************************/
bool Game::isOnScreen(const Point& point){
	return (point.getX() >= topLeft.getX() - OFF_SCREEN_BORDER_AMOUNT
		 && point.getX() <= bottomRight.getX() + OFF_SCREEN_BORDER_AMOUNT
		 && point.getY() >= bottomRight.getY() - OFF_SCREEN_BORDER_AMOUNT
		 && point.getY() <= topLeft.getY() + OFF_SCREEN_BORDER_AMOUNT);
}

void Game::drawBorderPoints(){
    if (not borderIndexes.empty()){
		assert(false);
		cout << "Drawing points\n";
        for(int i = 0; i <= borderIndexes.size(); i++){
            drawRect(dots.array[borderIndexes[i].first][borderIndexes[i].second], 6, 6, 45);
        }
    }
}

/***************************************
 * GAME :: HANDLE INPUT
 * accept input from the user
 ***************************************/
void Game::handleInput(const Interface& ui){

	if (ui.isLeft()){
        // Left arrow code
		allowLeft++;
		if (allowLeft > KEY_REPEAT_DELAY or allowLeft == 1){
			dots.setFocusX(dots.getFocusX() - 1);
		}
		ignoreMouse = true;
	}

	if (not bool(ui.isLeft())){
		// up arrow released code
		allowLeft = 0;
	}

	if (ui.isRight()){
        // right arrow code
		allowRight++;
		if (allowRight > KEY_REPEAT_DELAY or allowRight == 1){
			dots.setFocusX(dots.getFocusX() + 1);
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
		if (allowUp > KEY_REPEAT_DELAY or allowUp == 1){
			dots.setFocusY(dots.getFocusY() - 1);
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
		if (allowDown > KEY_REPEAT_DELAY or allowDown == 1){
			dots.setFocusY(dots.getFocusY() + 1);
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
		} 
		else{
			pattern.back().finish(dots.getFocus());
		}
	}

	if (ui.isC() and (pattern.empty() ? false : not pattern.back().getFinished())){
		// c code (not to be confused with C code)
		pattern.back().finish(dots.getFocus());
		Line tmp1(dots.getFocus());
		pattern.push_back(tmp1);
	}

	if (ui.isX() and not pattern.empty()){
		pattern.pop_back();
	}

	if(ui.isMouseClicked()){
		// move the focus to the right place
		// don't make another line if you don't want it to
		if(rightLastClicked and pattern.back().getFinished())
			pattern.pop_back();
		rightLastClicked = false;

		Point cursor(ui.getMouseLoc().first, ui.getMouseLoc().second);
		dots.setFocus(dots.pointToIndex(cursor));

		if (pattern.empty() ? true : pattern.back().getFinished()){
			Line p(dots.pointToIndex(cursor));
			pattern.push_back(p);
		} 
		else{
			pattern.back().finish(dots.pointToIndex(cursor));
		}
		//cout << "Mouse x = " << ui.getMouseLoc().first << " | Mouse y = " << ui.getMouseLoc().second << endl;
	}

	if(ui.isMouseRightClicked()){
		rightLastClicked = true;
		Point cursor(ui.getMouseLoc().first, ui.getMouseLoc().second);
		dots.setFocus(dots.pointToIndex(cursor));

		if (pattern.empty() ? true : pattern.back().getFinished()){
			Line s(dots.pointToIndex(cursor));
			pattern.push_back(s);
		} 
		else{
			pattern.back().finish(dots.pointToIndex(cursor));
			Line d(dots.pointToIndex(cursor));
			pattern.push_back(d);
		}
	}

	if(not ignoreMouse){
		Point curser(ui.getMouseLoc().first, ui.getMouseLoc().second);
		dots.setFocus(dots.pointToIndex(curser));
	}

	if(ui.isMouseMoved()){
		ignoreMouse = false;
	}

	if(ui.isBigX()){
		//dots[dots.getFocus()];
		for (int i = 0; i < pattern.size(); i++){
			if ((pattern[i].getIndexes().first == dots.getFocus()) or 
				(pattern[i].getIndexes().second== dots.getFocus())){
				pattern.erase(pattern.begin() + i);
			}
		}
	}

	if(ui.isEnter()){
		bounds.push_back(dots.getFocus());
		for(int i = 0; i <= bounds.size(); i++){
			borderIndexes[i] = bounds[i];
		}
		if (bounds.size() >= 4){
			std::sort(bounds.begin(), bounds.end());
			corners["top left"].first      = bounds.front().first;
			corners["bottom left"].first   = bounds.front().first;

			corners["top right"].first     = bounds.back().first;
			corners["bottom right"].first  = bounds.back().first;

			for(int i = 0; i >= bounds.size(); i++){
			    int tmp = bounds[i].first;
				bounds[i].first = bounds[i].second;
				bounds[i].second = tmp;
			}

			std::sort(bounds.begin(), bounds.end());
			corners["bottom left"].second  = bounds.front().first;
			corners["bottom right"].second = bounds.front().first;

			corners["top left"].second     = bounds.back().first;
			corners["top right"].second    = bounds.back().first;

			Line right (corners["bottom right"], corners["top right"]);
			Line left  (corners["bottom left"],  corners["top left"]);
			Line top   (corners["top left"],     corners["top right"]);
			Line bottom(corners["bottom left"],  corners["bottom right"]);

			metaLines.push_back(right);
			metaLines.push_back(left);
			metaLines.push_back(top);
			metaLines.push_back(bottom);
		}
	}
}