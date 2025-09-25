#include <Arduino.h>
#include "PID.h"

PID::PID(float kp, float ki, float kd) {
    setTunings(kp, ki, kd);
    _integral = 0;
    _enabled = false;
    _outputMin = -24;//maxSteeringAngle
    _outputMax = 24;
    _lastOutput = 0;
    _lastPError = 0;
}

void PID::setTunings(float kp, float ki, float kd) {
    _kp = kp;
    _ki = ki;
    _kd = kd;
}

void PID::setOutputLimits(float min, float max) {
    _outputMin = min;
    _outputMax = max;
}

void PID::enable() {
    _enabled = true;
}

void PID::disable() {
    _enabled = false;
    _integral = 0;
}

void PID::reset() {
    _integral = 0;
    _lastPError = 0;
}

bool PID::isEnabled() {
    return _enabled;
}

float PID::compute(float setpoint, float input) {
    unsigned long now = micros();

    if (lastUpdateTime == 0) {
        lastUpdateTime = now;
        return 0; 
    }

    float dt = (now - lastUpdateTime) / 1e6;
    lastUpdateTime = now;

    if (!_enabled) {
        _lastOutput = 0;
        return _lastOutput;
    }

    // Calcular errores
    float pError = setpoint - input;
    // Corrección: la división es para toda la resta, no solo para _lastPError
    float dError = (pError - _lastPError) / dt;

    _integral += pError * dt;
    _lastPError = pError;

    float pTerm = _kp * pError;
    float dTerm = _kd * dError;


    // Calcular salida PID
    float output = pTerm + _ki * _integral + dTerm;

    // Limitar salida
    if (output > _outputMax) output = _outputMax;
    else if (output < _outputMin) output = _outputMin;

    _lastOutput = output;
    return _lastOutput;
}
