#!/usr/bin/env bash
set -e
mkdir -p out
find src -name "*.java" | xargs javac -d out
echo "Build complete. Run with:  java -cp out game.Main"
