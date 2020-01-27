/*********************************************************************
 * File: game.h
 * Description: The base of the program
 *********************************************************************/

#pragma once

#include "uiDraw.h"
#include "uiInteract.h"
#include "point.h"
#include <vector>
#include <utility>
#include <map>
//#include "array.h"
#include "line.h"

/*****************************************
 * GAME
 * The main game class containing all the states
 *****************************************/
class Game{
private:
	Array dots;
	unsigned int timedFade = 0;
	unsigned int allowUp   = 1;
	unsigned int allowDown = 1;
	unsigned int allowLeft = 1;
	unsigned int allowRight= 1;
	bool rightLastClicked  = false;
	bool ignoreMouse   	   = false;	

public:
	/*********************************************
	 * Constructor
	 * Initializes the game
	 *********************************************/
	Game(const Point &tl, const Point &br);
	~Game();

	/*********************************************
	 * Function: handleInput
	 * Description: Takes actions according to whatever
	 *  keys the user has pressed.
	 *********************************************/
	void handleInput(const Interface& ui);

	/*********************************************
	 * Function: advance
	 * Description: Move everything forward one
	 *  step in time.
	 *********************************************/
	void advance();

	/*********************************************
	 * Function: draw
	 * Description: draws everything for the game.
	 *********************************************/
	//void draw(const Interface& ui);
	
	static bool isOnScreen(const Point& point);
	void drawBorderPoints();
	
	static Point topLeft;
	static Point bottomRight;

	std::vector<Line> pattern;
	std::vector<std::pair<int, int>> bounds;
	std::map<std::string, std::pair<int, int>> corners;
	std::vector<Line> metaLines;
    std::vector<std::pair<int, int>> borderIndexes;
};