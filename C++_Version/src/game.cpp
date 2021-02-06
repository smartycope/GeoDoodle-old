#include "game.h"
#include <cassert>
#include <iostream>
#include <algorithm>
#include <math.h>

// std::pair<int, int> Game::bottomRight;
// std::pair<int, int> Game::topLeft;

Game::Game() : dots(Array()) {
	topLeft.first  = -getWindowWidth() / 2;
    topLeft.second =  getWindowHeight() / 2;
	bottomRight.first  = getWindowWidth() / 2;
    bottomRight.second = -getWindowHeight() / 2;

    isBigErase.push_back(-1);

    settings = getSettings();

    // settings["dot spread"] = 18; // pixCount();

    // for debugging
    first = true;
    first2 = true;

    drawMenu = false;
    menuDelay = 0;
    recenter = true;

    debugPair = {500, 500};

    // debugVar("Window width", int(settings["start width"]));
    // debugVar("Window height", int(settings["start height"]));
    // // debugVar("center dot", dots.centerDot);
    // debugVar("dot spread", int(settings["dot spread"]));
    // // debugVar("xAdjust", xAdjust);
    // // debugVar("yAdjust", yAdjust);
}

// bet you can't guess what this does!
bool Game::isOnScreen(const std::pair<int, int> &point){
	return (point.first >= topLeft.first - (int)settings["off screen amount"]
		 && point.first <= bottomRight.first + (int)settings["off screen amount"]
		 && point.second >= bottomRight.second - (int)settings["off screen amount"]
		 && point.second <= topLeft.second + (int)settings["off screen amount"]);
}

void Game::repeatLine(){
    if (pattern.back().isFinished){
        tmpLines.clear();
        if (drawMetaLines and (boundsX.size() == 4)){
            if(((pattern.back().start.first  <= metaLines.front().end.first)   and
                (pattern.back().start.first  >= metaLines.front().start.first) and
                (pattern.back().start.second <= metaLines.front().end.second)  and
                (pattern.back().start.second >= metaLines.back().start.second)) or // <--
                // 'and' for both points must be inside the area, 'or' if only one point has to be inside the area.
               ((pattern.back().end.first  <= metaLines.front().end.first)   and
                (pattern.back().end.first  >= metaLines.front().start.first) and
                (pattern.back().end.second <= metaLines.front().end.second)  and
                (pattern.back().end.second >= metaLines.back().start.second)) ) {

                isBigErase.push_back(0);

                std::vector<Line> newPattern;
                int width, height, xOffset, xEndOffset, yOffset, yEndOffset;

                // Uncomment this line if you want the lines within the area to stay
                // newPattern.push_back(pattern.back()); // add the current Line to newPattern

                // relate the start points to the top left corner, and the end points to the start points
                xOffset = pattern.back().start.first  - metaLines.front().start.first;
                yOffset = pattern.back().start.second - metaLines.front().start.second;
                xEndOffset = pattern.back().end.first  - pattern.back().start.first;
                yEndOffset = pattern.back().end.second - pattern.back().start.second;

                height = metaLines.front().start.second - metaLines.back().start.second;
                width  = metaLines.front().end.first - metaLines.front().start.first;

                eraseCount = 0;

                // iterate through the array by the offset and create new points at every junction
                for (int ys =  yOffset - (getWindowHeight() / 2) - (int)settings["offscreen amount"] - height;
                         ys <= yOffset + (getWindowHeight() / 2) + (int)settings["offscreen amount"] + height;
                         ys += height){
                    for (int xs =  xOffset - (getWindowWidth() / 2) - (int)settings["offscreen amount"] - width;
                             xs <= xOffset + (getWindowWidth() / 2) + (int)settings["offscreen amount"] + width;
                             xs += width){

                        std::pair<int, int> startPoint(xs + xAdjust + repeatedxAdjust, ys + yAdjust + repeatedyAdjust);
                        std::pair<int, int> endPoint  (xs + xAdjust + repeatedxAdjust + xEndOffset, ys + yEndOffset + yAdjust + repeatedyAdjust);
                        Line tmp2(startPoint, endPoint);
                        newPattern.push_back(tmp2);
                        ++eraseCount;
                    }
                }

                for (auto it = newPattern.begin(); it != newPattern.end(); it++){
                    pattern.push_back(*it);
                }
            } // end of if statement
            else{
                if (isBigErase.back() >= 0){
                    ++isBigErase.back();// = isBigErase.back() + 1;
                }
            }
        }
    }
    else { // if the line is unfinished
        if (drawMetaLines and (boundsX.size() == 4)){
            if( (pattern.back().start.first  <= metaLines.front().end.first)   and
                (pattern.back().start.first  >= metaLines.front().start.first) and
                (pattern.back().start.second <= metaLines.front().end.second)  and
                (pattern.back().start.second >= metaLines.back().start.second) ) {

                // isBigErase.push_back(0);

                // relate the start points to the top left corner, and the end points to the start points
                int xOffset = pattern.back().start.first  - metaLines.front().start.first;
                int yOffset = pattern.back().start.second - metaLines.front().start.second;
                // int xEndOffset = dots.getFocus().first  - pattern.back().start.first;
                // int yEndOffset = dots.getFocus().second - pattern.back().start.second;

                int height = metaLines.front().start.second - metaLines.back().start.second;
                int width  = metaLines.front().end.first - metaLines.front().start.first;

                // iterate through the array by the offset and create new points at every junction
                for (int ys =  yOffset - (getWindowHeight() / 2) - (int)settings["offscreen amount"] - height;
                         ys <= yOffset + (getWindowHeight() / 2) + (int)settings["offscreen amount"] + height;
                         ys += height){
                    for (int xs =  xOffset - (getWindowWidth() / 2) - (int)settings["offscreen amount"] - width;
                             xs <= xOffset + (getWindowWidth() / 2) + (int)settings["offscreen amount"] + width;
                             xs += width){

                        std::pair<int, int> startPoint(xs + xAdjust + repeatedxAdjust, ys + yAdjust + repeatedyAdjust);
                        Line tmp3(startPoint);
                        tmpLines.push_back(tmp3);
                    }
                }
            } // end of if statement
            else {
                if (isBigErase.back() >= 0){
                    ++isBigErase.back();
                }
            }
        }
    }
}

bool Game::write_png_file(const char* file_name, const png_bytepp data, int width, int height){
  debug("starting to write png");
  // open file
  // note: libpng tells us to make sure we open in binary mode
  FILE *fp = fopen(file_name, "wb");
  if (fp == NULL)
    std::cout << "Unable to save the pattern.\n";
    //assert(false); //("%s file cannot be opened for reading", file_name);

  // create png structure
  png_structp png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
  if (png_ptr == NULL){
    // cannot create png structure
    fprintf(stderr, "cannot create png structure\n");

    // close file
    fclose(fp);
    fp = NULL;
    return false;
  }

  // create png-info structure
  png_infop info_ptr = png_create_info_struct(png_ptr);
  if (info_ptr == NULL){
    fprintf(stderr, "cannot create png info structure\n");

    // clear png resource
    png_destroy_write_struct(&png_ptr, (png_infopp)NULL);

    // close file
    fclose(fp);
    fp = NULL;
    return false;
  }

  // we need to set jump callback to handle error when we enter into a new routing before the call to png_*()
  // defined as convenient for future if you every call this in different routine
  // note: if use, need to call in routine that return bool type indicating the result of operation
#define PNG_WRITE_SETJMP(png_ptr, info_ptr, fp) \
  /* set jmp */  \
  if (setjmp(png_jmpbuf(png_ptr)))  \
  { \
    fprintf(stderr, "error png's set jmp for write\n"); \
                                              \
    /* clear png resource */                  \
    png_destroy_write_struct(&png_ptr, &info_ptr);   \
                                                                      \
    /* close file */ \
    fclose(fp);     \
    fp = NULL;      \
    return false;    \
  }

  // call this once as all relevant operations all happen in just one routine
  PNG_WRITE_SETJMP(png_ptr, info_ptr, fp)

  // set up input code
  png_init_io(png_ptr, fp);

  // set important parts of png_info first
  png_set_IHDR(png_ptr,
      info_ptr,
      width,
      height,
      8,
      PNG_COLOR_TYPE_RGB_ALPHA,
      PNG_INTERLACE_NONE,
      PNG_COMPRESSION_TYPE_DEFAULT,
      PNG_FILTER_TYPE_DEFAULT);
  // <... add any png_set_*() function in any order if need here

  // ready to write info we've set before actual image data
  png_write_info(png_ptr, info_ptr);

  // now it's time to write actual image data
  png_write_image(png_ptr, data);

  // done writing image
  // pass NULL as we don't need to write any set data i.e. comment
  png_write_end(png_ptr, NULL);

  // clear png resource
  png_destroy_write_struct(&png_ptr, &info_ptr);

  // close file
  fclose(fp);
  fp = NULL;

  debug("png write succesful");
  return true;
}

png_bytepp Game::generateImage(std::vector<Line> lines, int width, int height, int xOffset, int yOffset, unsigned char r, unsigned char g, unsigned char b){
  debug("generating png");
  // generate RGBA pixel format
  const int rowbytes = width * 4;

  png_bytepp row_ptr = (png_bytepp)malloc(sizeof(png_bytep) * height);
  for (int y = 0; y < height; ++y){
    row_ptr[y] = (png_bytep)malloc(rowbytes);
  }

  debugVar("width", width);
  debugVar("height", height);

  // set the background to all be the same
  for (int y = 0; y < height; ++y){
    for (int x = 0; x < width; ++x){
      png_bytep p = &(row_ptr[y][x * 4]);
      p[0] = r;
      p[1] = g;
      p[2] = b;
      p[3] = 0xFF;
    }
  }

  int x, y;

  debug("well, I got here anyway.");

  for(auto itv = pattern.begin(); itv != pattern.end(); ++itv)
    drawLine(row_ptr, *itv, 0x00, 0x00, 0x00, xOffset, yOffset);

  debug("png generation succesful");
  return row_ptr;
}

float Game::fpart(float x){
	return x - floor(x);
}

float Game::rfpart(float x){
	return 1 - fpart(x);
}

void Game::plot(png_bytepp row, int x, int y, float c, unsigned char r, unsigned char g, unsigned char b){
  if(VERBOSE >= 3){ debug("plotting png byte"); }
  png_bytep p = &(row[y][x * 4]);
  p[0] = r;// * c;
  p[1] = g;// * c;
  p[2] = b;// * c;
  p[3] = c;//0xFF;
  if(VERBOSE >= 3){ debug("png byte plot sucessful"); }
}

std::pair<int, int> Game::shiftOriginCenterToCorner(std::pair<int, int> coord){
  return std::pair<int, int>(coord.first + (getWindowWidth() / 2), coord.second + (getWindowHeight() / 2));
}

std::pair<int, int> Game::shiftOriginCornerToCenter(std::pair<int, int> coord){
  return std::pair<int, int>(coord.first - (getWindowWidth() / 2), coord.second - (getWindowHeight() / 2));
}

// Xiaolin Wu's anti-aliasing algorithm
void Game::drawLine(png_bytepp row, Line line, unsigned char r, unsigned char g, unsigned char b, int xOffset, int yOffset){
  if(VERBOSE >= 3){ debug("drawing line in png"); }

  line.start = shiftOriginCenterToCorner(line.start);
  line.end = shiftOriginCenterToCorner(line.end);

  line.start.first  += xOffset;
  line.end.first    += xOffset;
  line.start.second += yOffset;
  line.end.second   += yOffset;

  debugVar("line start", line.start);
  debugVar("line end", line.end);

	float dx = line.end.first - line.start.first;
	float dy = line.end.second - line.start.second;

	if (std::fabs(dx) > std::fabs(dy)){
		if(line.end.first < line.start.first){
			std::swap(line.start.first, line.end.first);
			std::swap(line.start.second, line.end.second);
		}

		float gradient = dy / dx;
		float xend = static_cast<float>(round(line.start.first));
		float yend = line.start.second + gradient * (xend - line.start.first);
		float xgap = rfpart(line.start.first + 0.5f);

		int xpxl1 = static_cast<int>(xend);
		int ypxl1 = floor(yend);

		// Add the first endpoint
		plot(row, xpxl1, ypxl1, rfpart(yend) * xgap, r, g, b);
		plot(row, xpxl1, ypxl1 + 1, fpart(yend) * xgap, r, g, b);

		float intery = yend + gradient;

		xend = static_cast<float>(round(line.end.first));
		yend = line.end.second + gradient * (xend - line.end.first);
		xgap = fpart(line.end.first + 0.5f);

		int xpxl2 = static_cast<int>(xend);
		int ypxl2 = floor(yend);

		// Add the second endpoint
		plot(row, xpxl2, ypxl2, rfpart(yend) * xgap, r, g, b);
		plot(row, xpxl2, ypxl2 + 1, fpart(yend) * xgap, r, g, b);

		// Add all the points between the endpoints
		for(int x = xpxl1 + 1; x <= xpxl2 - 1; ++x){
			plot(row, x, floor(intery), rfpart(intery), r, g, b);
			plot(row, x, floor(intery) + 1, fpart(intery), r, g, b);
			intery += gradient;
		}
	}
	else{
		if(line.end.second < line.start.second){
			std::swap(line.start.first, line.end.first);
			std::swap(line.start.second, line.end.second);
		}

		float gradient = dx / dy;
		float yend = static_cast<float>(round(line.start.second));
		float xend = line.start.first + gradient * (yend - line.start.second);
		float ygap = rfpart(line.start.second + 0.5f);

		int ypxl1 = static_cast<int>(yend);
		int xpxl1 = floor(xend);

		// Add the first endpoint
		plot(row, xpxl1, ypxl1, rfpart(xend) * ygap, r, g, b);
		plot(row, xpxl1, ypxl1 + 1, fpart(xend) * ygap, r, g, b);

		float interx = xend + gradient;

		yend = static_cast<float>(round(line.end.second));
		xend = line.end.first + gradient * (yend - line.end.second);
		ygap = fpart(line.end.second + 0.5f);

		int ypxl2 = static_cast<int>(yend);
		int xpxl2 = floor(xend);

		// Add the second endpoint
		plot(row, xpxl2, ypxl2, rfpart(xend) * ygap, r, g, b);
		plot(row, xpxl2, ypxl2 + 1, fpart(xend) * ygap, r, g, b);

		// Add all the points between the endpoints
		for(int y = ypxl1 + 1; y <= ypxl2 - 1; ++y){
			plot(row, floor(interx), y, rfpart(interx), r, g, b);
			plot(row, floor(interx) + 1, y, fpart(interx), r, g, b);
			interx += gradient;
		}
	}
  if(VERBOSE >= 3){ debug("png line draw sucessful"); }
}