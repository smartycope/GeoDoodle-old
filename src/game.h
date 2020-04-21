#pragma once

#include "uiDraw.h"
#include "uiInteract.h"
#include <vector>
#include <utility>
#include <map>
#include "line.h"
#include "glutCallbacks.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdarg.h>
#include <png.h>
// #include "test-libpng.h"

// how often you should compare the settings file to see if it's changed
#define CHECK_SETTINGS_DELAY 100 // 100 = ~5 seconds
#define MENU_DELAY 10

class Game{
private:
	Array dots;
  nlohmann::json settings;

  int xAdjust;
  int yAdjust;
  int repeatedxAdjust = 1;
  int repeatedyAdjust = 1;

  // These are for debugging
  std::pair<int, int> debugPair;
  bool first;
  bool first2;

  bool recenter; // not for debugging
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
  unsigned int checkSettingsDelay = CHECK_SETTINGS_DELAY;
  unsigned int menuDelay  = 0;
  // this keeps track of how many lines you've added since a repeating line
  std::vector<int> isBigErase;
  // this dictates how many times you need to erase to erase a repeated line
  unsigned int eraseCount = 0;
  // this holds all the unfinished repeating lines.
  std::vector<Line> tmpLines;

  void repeatLine();

  std::pair<int, int> topLeft;
	std::pair<int, int> bottomRight;

  std::pair<int, int> shiftOriginCenterToCorner(std::pair<int, int> coord);
  std::pair<int, int> shiftOriginCornerToCenter(std::pair<int, int> coord);

  // for writing to a png image
  bool write_png_file(const char* file_name, const png_bytepp data, int width, int height);
  png_bytepp generateImage(std::vector<Line> lines, int width, int height, int xOffset, int yOffset, unsigned char r, unsigned char g, unsigned char b);
  void drawLine(png_bytepp row, Line line, unsigned char r, unsigned char g, unsigned char b, int xOffset, int yOffset);
  void plot(png_bytepp row, int x, int y, float c, unsigned char r, unsigned char g, unsigned char b);
  float rfpart(float x);
  float fpart(float x);

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