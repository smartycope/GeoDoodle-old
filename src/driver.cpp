/*****************************************************
 * File: Driver.cpp
 * Author: Copeland Carter
 *
 * This is main.
 * 
 * Suggested features:
 * fix the "d" key bug
 * add a button that shows all the keys and what they do
:) hide the mouse when you press the arrow keys
:) add a button that hides/gets rid of the metalines
:) switch the 'c' key and the space key - didn't like it, switched back
:) expand and center the dots array so it goes off screen better
 * consider moving the enter key to some other key
:) add smaller dots within the dots so repeating can actually work
 * fix it so when a line runs out of the original area, it cuts it
 *   off where is ends, but still draws it.
 * add zooming in and out
 * add a camera you can move around
:) add saving (i.e. serialization and deserialization)
 * add saving to a pdf
 * make the repeater area smarter (i.e. make the area 
 *   more closely follow the lines, not just in a square)
 * allow screen resizing
 * add mirroring
:) add instant repeating inside of the metabox (toggles with m)
 * add the ability to change how much space is between the dots
 ******************************************************/
#include "game.h"
#include "uiInteract.h"
#include "uiDraw.h"
#include <iostream>
#include "glutCallbacks.h"

/*************************************
 * All the interesting work happens here, when
 * I get called back from OpenGL to draw a frame.
 * When I am finished drawing, then the graphics
 * engine will wait until the proper amount of
 * time has passed and put the drawing on the screen.
 **************************************/
void callBack(const Interface *pUI, void *p){
   Game *pGame = (Game *)p;
   
   pGame->advance();
   pGame->handleInput(*pUI);
}

/*********************************
 * Main is pretty sparse.  Just initialize
 * the game and call the display engine.
 * That is all!
 *********************************/
int main(int argc, char ** argv){
   std::pair<int, int> topLeft(-200, 200);
   std::pair<int, int> bottomRight(200, -200);

   // default settings
//    nlohmann::json j;
//    j.emplace("dot spread", 16);
//    j.emplace("start height", 400);
//    j.emplace("start width", 400);
//    j.emplace("is c repeat", true);
//    j.emplace("number of enters", 4);
//    j.emplace("key repeat speed", 9);
//    j.emplace("offscreen amount", 10);
//    j.emplace("focus radius", 5);
//    setSettings(j);
//    j.emplace("", );

   
   Interface ui(argc, argv, "GeoDoodle");
   Game game;
   ui.run(callBack, &game);
   
   return 0;
}