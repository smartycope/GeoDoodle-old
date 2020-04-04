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

#define IS_DEBUG false

// class Interface;

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

void debug(const std::string &message, int line = -1);
void debug(int line = -1);
void debugVar(const std::string &varName, int var);
void debugVar(const std::string &varName, std::pair<int, int> var);
void debugVar(int var);