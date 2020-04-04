cmake_minimum_required(VERSION 3.5)
project(GeoDoodle)

# State directories for modules and binaries
set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin)
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/CMake)
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/CMake/Dependencies)
# set(CMAKE_PREFIX_PATH ${CMAKE_SOURCE_DIR}/CMake/Qt5)
# set(CMAKE_PREFIX_PATH)
# set(CMAKE_PREFIX_PATH path/to/Qt5/lib/cmake)
set(Qt5_DIR ${CMAKE_SOURCE_DIR}/CMake)
# set(Qt5QDialog_DIR ${CMAKE_SOURCE_DIR}/CMake)

# Turn on automatic invocation of the MOC, UIC & RCC
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


include(ExternalProject)
include(GLUT)
include(JSON)

# setting the compiler flags
set(CMAKE_CXX_FLAGS "-std=c++1z -O3")


# set(CMAKE_CXX_FLAGS_COVERAGE "${CMAKE_CXX_FLAGS_RELEASE} -fprofile-arcs -ftest-coverage")

# set up a mapping so that the Release configuration for the Qt imported target is
# used in the COVERAGE CMake configuration.
# set_target_properties(Qt5::Core PROPERTIES MAP_IMPORTED_CONFIG_COVERAGE "RELEASE")


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
    # src/qml.qrc
    )

# Find dependencies
#find_package(SDL2 REQUIRED)
#if(NOT SDL2_FOUND)
    #include(SDL2)
#    message(FATAL_ERROR "Package SDL2 is required, but not found!")
#endif(NOT SDL2_FOUND)
#include()

find_package(OpenGL REQUIRED)

find_package(Qt5 REQUIRED
    Core
    Gui
    Widgets
    Quick
    # QDialog
)

find_package(Qt5 REQUIRED COMPONENTS Widgets)

# Specify include directories
include_directories(
    ${OpenGL_INCLUDE_DIR}
    ${FREEGLUT_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}
)

# Create the binary
add_executable(${CMAKE_PROJECT_NAME} ${GeoDoodle_src})

# if(ANDROID)
#     add_library(GeoDoodle SHARED qml.qrc)
# else()
#     add_executable(GeoDoodle qml.qrc)
# endif()

# This line is saying "make sure you build freeglut before you build ^the project^".
# This is useful for things that depend on other things, and/or multithreading your build.
# Link the libraries
add_dependencies(${CMAKE_PROJECT_NAME} freeglut)

# target_compile_definitions(GeoDoodle PRIVATE $<$<OR:$<CONFIG:Debug>,$<CONFIG:RelWithDebInfo>>:QT_QML_DEBUG>)

# target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE Qt5::Core Qt5::Quick)
target_link_libraries(GeoDoodle Qt5::Widgets)

target_link_libraries(${CMAKE_PROJECT_NAME}
  ${FREEGLUT_LIBRARY}
  ${OPENGL_LIBRARIES}
  Qt5::Core 
  Qt5::Quick
)