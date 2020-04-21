ExternalProject_Add(json
  DOWNLOAD_NO_PROGRESS 1
  URL https://github.com/nlohmann/json/releases/download/v3.7.3/include.zip
  PREFIX ${CMAKE_CURRENT_BINARY_DIR}/json
  CMAKE_ARGS -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_BINARY_DIR}/json
  BUILD_COMMAND "true"
  CONFIGURE_COMMAND "true"
  INSTALL_COMMAND "true"
)

include_directories(
SYSTEM "${CMAKE_BINARY_DIR}/json/src/json/include/"
)
