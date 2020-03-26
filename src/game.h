#pragma once

#include "uiDraw.h"
#include "uiInteract.h"
#include <vector>
#include <utility>
#include <map>
#include "line.h"
#include "glutCallbacks.h"

// #define KEY_REPEAT_DELAY 9 // in settings
// #define OFF_SCREEN_AMOUNT 10 // in settings
// These are to make the lines line up with the dots better. Honestly not sure why they're nessicary.
// #define X_ADJUST 0 // 16 = -7 // 15 = -4
// #define Y_ADJUST 0 // 16 = 3  // 15 = 1

// #define DEBUG true

class Game{
private:
	Array dots;
    nlohmann::json settings;

    int xAdjust;
    int yAdjust;
    int repeatedxAdjust = 2;
    int repeatedyAdjust = 2;

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
    unsigned int checkSettingsDelay = 0;
    // this keeps track of how many lines you've added since a repeating line
    std::vector<int> isBigErase;
    // this dictates how many times you need to erase to erase a repeated line
    unsigned int eraseCount = 0;
    // this holds all the unfinished repeating lines.
    std::vector<Line> tmpLines;

    void repeatLine();

    std::pair<int, int> topLeft;
	std::pair<int, int> bottomRight;

public:
	Game();
    ~Game(){ };
    // guess what these do.
	void handleInput(const Interface& ui);
	void advance();
	
	bool isOnScreen(const std::pair<int, int> &point); // consider moving this to glutCallbacks.cpp
	
	// static std::pair<int, int> topLeft;
	// static std::pair<int, int> bottomRight;

	std::vector<Line> pattern;
	std::vector<int> boundsX;
	std::vector<int> boundsY;
	std::map<std::string, std::pair<int, int>> corners;
	std::vector<Line> metaLines;
    std::vector<std::pair<int, int>> borderIndexes;
};