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
 ******************************************************/
#include "game.h"
#include "uiInteract.h"
#include "uiDraw.h"
#include <iostream>

/*************************************
 * All the interesting work happens here, when
 * I get called back from OpenGL to draw a frame.
 * When I am finished drawing, then the graphics
 * engine will wait until the proper amount of
 * time has passed and put the drawing on the screen.
 **************************************/
void callBack(const Interface *pUI, void *p){
   Game *pGame = (Game *)p;

//    std::cout << "Called back\n";
   
   pGame->advance();
//    std::cout << "Advancing...\n";
   pGame->handleInput(*pUI);
//    std::cout << "Handling...\n";
   //pGame->draw(*pUI);
}

/*********************************
 * Main is pretty sparse.  Just initialize
 * the game and call the display engine.
 * That is all!
 *********************************/
int main(int argc, char ** argv){
   std::pair<int, int> topLeft(-200, 200);
   std::pair<int, int> bottomRight(200, -200);
   
   Interface ui(argc, argv, "GeoDoodle", topLeft, bottomRight);
   Game game(topLeft, bottomRight);
   ui.run(callBack, &game);
   
   return 0;
}