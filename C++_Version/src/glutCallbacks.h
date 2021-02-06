/*
 Everything defined here is required to be in a global scope
 openGL to see it. That's why it's here and not in a class somewhere.
 */
#pragma once

#include "uiInteract.h"
#include <fstream>
#include <iostream>
#include <string>
#include <nlohmann/json.hpp>
#include <debug.h>

#define DOTS_OFFSCREEN (int(settings["offscreen amount"]) * int(settings["dot spread"]))

void sleep(unsigned long msSleep);
void drawCallback();
void keyDownCallback(int key, int x, int y);
void keyUpCallback(int key, int x, int y);
void keyboardCallback(unsigned char key, int x, int y);
void mouseCallback(int button, int state, int x, int y);
void mouseMotionCallback(int x, int y);
void setMouse(bool hidden);
int  pixCount(bool metric = false);
int  getWindowWidth();
int  getWindowHeight();
bool isCloseEnough(int from, int to, int tolerance);
nlohmann::json getSettings();
void setSettings(nlohmann::json settings);
