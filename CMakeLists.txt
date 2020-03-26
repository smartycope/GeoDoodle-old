cmake_minimum_required(VERSION 2.8.11)
project(GeoDoodle)

# State directories for modules and binaries
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin)
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/CMake)
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/CMake/Dependencies)
include(ExternalProject)
include(GLUT)
include(JSON)

# setting the compiler flags
set(CMAKE_CXX_FLAGS "-std=c++1z -O3")


#Making the compiler as strict as possible
#set(CMAKE_CXX_FLAGS "-std=c++1z -fno-elide-constructors 
# -pedantic-errors -Werror -Wextra -Wall -Wpedantic -Winit-self 
# -Wmissing-declarations -Wuninitialized -Woverloaded-virtual 
# -Wold-style-cast -Wfatal-errors -O3 -static")
#add_definitions(${CMAKE_CXX_FLAGS})

#Location of source files
#file(GLOB SOURCE src/*.cpp src/*.hpp)
set(GeoDoodle_src
src/driver.cpp 
src/uiInteract.cpp
# src/point.cpp
src/game.cpp
src/uiDraw.cpp
src/array.cpp
src/line.h
src/gameAdvance.cpp
src/gameHandleInput.cpp
src/glutCallbacks.cpp
)

# Find dependencies
#find_package(SDL2 REQUIRED)
#if(NOT SDL2_FOUND)
    #include(SDL2)
#    message(FATAL_ERROR "Package SDL2 is required, but not found!")
#endif(NOT SDL2_FOUND)
#include()

find_package(OpenGL REQUIRED)

# Specify include directories
include_directories(
    ${OpenGL_INCLUDE_DIR}
    ${FREEGLUT_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}
)

# Create the binary
add_executable(${CMAKE_PROJECT_NAME} ${GeoDoodle_src})

# This line is saying "make sure you build freeglut before you build ^the project^".
# This is useful for things that depend on other things, and/or multithreading your build.
# Link the libraries
add_dependencies(${CMAKE_PROJECT_NAME} freeglut)

target_link_libraries(${CMAKE_PROJECT_NAME}
  ${FREEGLUT_LIBRARY}
  ${OPENGL_LIBRARIES}
)