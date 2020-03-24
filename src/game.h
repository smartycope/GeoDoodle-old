#pragma once

#include "uiDraw.h"
#include "uiInteract.h"
#include <vector>
#include <utility>
#include <map>
// #include <msgpack.hpp>
// #include "array.h"
#include "line.h"

#define KEY_REPEAT_DELAY 9
#define OFF_SCREEN_AMOUNT 10
// These are to make the lines line up with the dots better. Honestly not sure why they're nessicary.
#define X_ADJUST -7 // 15 = -4
#define Y_ADJUST 3 // 15 = 1

#define DEBUG false

class Game{
private:
	Array dots;

	// unsigned int timedFade = 0;
	unsigned int allowUp    = 1;
	unsigned int allowDown  = 1;
	unsigned int allowLeft  = 1;
	unsigned int allowRight = 1;
	bool rightLastClicked   = false;
	bool ignoreMouse   	    = false;
    short numEnterPressed   = 0;
    bool drawMetaLines      = true;
    bool drawMenu           = false;
    bool notOnDotUp         = false;
    bool notOnDotSide       = false;
    bool lineCatch          = false;
    // bool lastRepeatedCount  = false; // this is how many lines it has been since you added a 
    std::vector<int> isBigErase;
    unsigned int eraseCount = 0;
    std::vector<Line> tmpLines;

    void repeatLine();

    bool isCloseEnough(int from, int to, int tolerance);

public:
	Game(const std::pair<int, int> &tl, const std::pair<int, int> &br);
	~Game();

	/*********************************************
	 * Handles all of the mouse movements and keystrokes
	 *********************************************/
	void handleInput(const Interface& ui);

	/*********************************************
	 * The main loop of the program
	 *********************************************/
	void advance();
	
	static bool isOnScreen(const std::pair<int, int> &point);
	void drawBorderPoints();
	
	static std::pair<int, int> topLeft;
	static std::pair<int, int> bottomRight;

	std::vector<Line> pattern;
	std::vector<int> boundsX;
	std::vector<int> boundsY;
	std::map<std::string, std::pair<int, int>> corners;
	std::vector<Line> metaLines;
    std::vector<std::pair<int, int>> borderIndexes;
};