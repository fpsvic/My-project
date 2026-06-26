#pragma once
#include <cmath>

inline double hashN(double x, double y, double seed) {
    double v = std::sin(x * 127.1 + y * 311.7 + seed * 74.3) * 43758.5453;
    return v - std::floor(v);
}

inline double smoothN(double x, double y, double seed) {
    double v = 0, amp = 1, freq = 1, mx = 0;
    for (int o = 0; o < 6; o++) {
        v  += hashN(x * freq / 40.0, y * freq / 40.0, seed + o) * amp;
        mx += amp; amp *= 0.5; freq *= 2.0;
    }
    return v / mx;
}
