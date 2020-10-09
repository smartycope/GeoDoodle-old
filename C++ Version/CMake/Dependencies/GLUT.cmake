ExternalProject_Add(freeglut
  DOWNLOAD_NO_PROGRESS 1
  URL https://github.com/dcnieho/FreeGLUT/archive/FG_3_2_1.tar.gz
  PREFIX ${CMAKE_CURRENT_BINARY_DIR}/freeglut
  CMAKE_ARGS -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_BINARY_DIR}/freeglut -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE} -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER} -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER} -DBUILD_SHARED_LIBS=OFF -DFREEGLUT_BUILD_STATIC_LIBS=ON
)

if(WIN32)
    set(FREEGLUT_LIBRARY 
#   "${CMAKE_BINARY_DIR}/freeglut/src/freeglut-build/lib/libfreeglut_static.a"
    "${CMAKE_BINARY_DIR}/freeglut/src/freeglut-build/lib/libfreeglut.dll.a"
    )
else()
    set(FREEGLUT_INCLUDE_DIR "${CMAKE_BINARY_DIR}/freeglut/include")
    # set(FREEGLUT_LIBRARY "${CMAKE_BINARY_DIR}/freeglut/lib/libfreeglut.so")
    set(FREEGLUT_LIBRARY "${CMAKE_BINARY_DIR}/freeglut/src/freeglut-build/lib/libglut.so")
endif()

include_directories(
SYSTEM "${CMAKE_BINARY_DIR}/freeglut/include"
SYSTEM "${CMAKE_BINARY_DIR}/freeglut/src/freeglut/include"
)

set(GAME_DEPENDENCY_LIBRARIES
    ${GAME_DEPENDENCY_LIBRARIES}
    ${FREEGLUT_LIBRARY}
    )
