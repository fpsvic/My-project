cmake_minimum_required(VERSION 3.16)
project(TopDownWorld)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(SDL2 REQUIRED)
find_package(SDL2_ttf QUIET)

# Try pkg-config if CMake find didn't work
if(NOT SDL2_ttf_FOUND)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(SDL2_TTF REQUIRED SDL2_ttf)
    set(SDL2_TTF_LIBRARIES ${SDL2_TTF_LIBRARIES})
    set(SDL2_TTF_INCLUDE_DIRS ${SDL2_TTF_INCLUDE_DIRS})
else()
    set(SDL2_TTF_LIBRARIES SDL2_ttf::SDL2_ttf)
    set(SDL2_TTF_INCLUDE_DIRS "")
endif()

add_executable(TopDownWorld
    src/main.cpp
    src/World.cpp
    src/Game.cpp
)

target_include_directories(TopDownWorld PRIVATE src ${SDL2_INCLUDE_DIRS} ${SDL2_TTF_INCLUDE_DIRS})
target_link_libraries(TopDownWorld PRIVATE ${SDL2_LIBRARIES} ${SDL2_TTF_LIBRARIES} m)
target_compile_options(TopDownWorld PRIVATE -O2 -Wall)
