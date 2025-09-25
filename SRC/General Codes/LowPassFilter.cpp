#include "LowPassFilter.h"
#include <math.h>

LowPassFilter::LowPassFilter(float cutoffFreq, float sampleRate) {
    setAlpha(cutoffFreq, sampleRate);
    prevOutput = 0.0f;
    initialized = false;
}

void LowPassFilter::setAlpha(float cutoffFreq, float sampleRate) {
    float dt = 1.0f / sampleRate;
    float RC = 1.0f / (2.0f * 3.14159f * cutoffFreq);
    alpha = dt / (RC + dt);
}

float LowPassFilter::update(float input) {
    if (!initialized) {
        prevOutput = input;
        initialized = true;
    } else {
        prevOutput += alpha * (input - prevOutput);
    }
    return prevOutput;
}

void LowPassFilter::setInitial(float value) {
    prevOutput = value;
    initialized = false;
}

void LowPassFilter::clear() {
    initialized = false;
}
