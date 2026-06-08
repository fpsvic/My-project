cmake_minimum_required(VERSION 3.16)
project(BladeArena CXX)

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

add_executable(blade_arena src/main.cpp)
target_link_libraries(blade_arena PRIVATE raylib)

if(UNIX AND NOT APPLE)
  target_link_libraries(blade_arena PRIVATE m pthread dl rt)
endif()
