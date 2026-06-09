cmake_minimum_required(VERSION 3.16)
project(BladeArena CXX C)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(BUILD_GAMES OFF CACHE BOOL "" FORCE)
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)

FetchContent_Declare(
  raylib
  GIT_REPOSITORY https://github.com/raysan5/raylib.git
  GIT_TAG 5.5
)
FetchContent_MakeAvailable(raylib)

FetchContent_Declare(
  lua
  URL https://www.lua.org/ftp/lua-5.4.6.tar.gz
  DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)
FetchContent_MakeAvailable(lua)

set(LUA_CORE_SOURCES
  ${lua_SOURCE_DIR}/src/lapi.c ${lua_SOURCE_DIR}/src/lcode.c ${lua_SOURCE_DIR}/src/lctype.c
  ${lua_SOURCE_DIR}/src/ldebug.c ${lua_SOURCE_DIR}/src/ldo.c ${lua_SOURCE_DIR}/src/ldump.c
  ${lua_SOURCE_DIR}/src/lfunc.c ${lua_SOURCE_DIR}/src/lgc.c ${lua_SOURCE_DIR}/src/llex.c
  ${lua_SOURCE_DIR}/src/lmem.c ${lua_SOURCE_DIR}/src/lobject.c ${lua_SOURCE_DIR}/src/lopcodes.c
  ${lua_SOURCE_DIR}/src/lparser.c ${lua_SOURCE_DIR}/src/lstate.c ${lua_SOURCE_DIR}/src/lstring.c
  ${lua_SOURCE_DIR}/src/ltable.c ${lua_SOURCE_DIR}/src/ltm.c ${lua_SOURCE_DIR}/src/lundump.c
  ${lua_SOURCE_DIR}/src/lvm.c ${lua_SOURCE_DIR}/src/lzio.c
)
set(LUA_LIB_SOURCES
  ${lua_SOURCE_DIR}/src/lauxlib.c ${lua_SOURCE_DIR}/src/lbaselib.c ${lua_SOURCE_DIR}/src/lcorolib.c
  ${lua_SOURCE_DIR}/src/ldblib.c ${lua_SOURCE_DIR}/src/liolib.c ${lua_SOURCE_DIR}/src/lmathlib.c
  ${lua_SOURCE_DIR}/src/loadlib.c ${lua_SOURCE_DIR}/src/loslib.c ${lua_SOURCE_DIR}/src/lstrlib.c
  ${lua_SOURCE_DIR}/src/ltablib.c ${lua_SOURCE_DIR}/src/lutf8lib.c ${lua_SOURCE_DIR}/src/linit.c
)

add_library(lua_static STATIC ${LUA_CORE_SOURCES} ${LUA_LIB_SOURCES})
target_include_directories(lua_static PUBLIC ${lua_SOURCE_DIR}/src)
if(UNIX AND NOT APPLE)
  target_link_libraries(lua_static PUBLIC m dl)
endif()

add_executable(blade_arena src/main.cpp src/script_host.cpp)
target_include_directories(blade_arena PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/assets ${lua_SOURCE_DIR}/src)
target_link_libraries(blade_arena PRIVATE raylib lua_static)

if(UNIX AND NOT APPLE)
  target_link_libraries(blade_arena PRIVATE m pthread dl rt)
endif()
