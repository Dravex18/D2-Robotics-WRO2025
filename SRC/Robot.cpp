#include "Robot.h"
#include <Arduino.h>
#include <Wire.h>
#include <math.h>

// --- Constructor ---
Robot::Robot()
  : sonar1(trigPin1, echoPin1, (unsigned int)(MAX_DIST_M * 100)),
    sonar2(trigPin2, echoPin2, (unsigned int)(MAX_DIST_M * 100)) {
}

// --- Inicialización ---
void Robot::begin() {
    Wire.begin();

    pinMode(motorAPin1, OUTPUT);
    pinMode(motorAPin2, OUTPUT);
    pinMode(motorAPWM, OUTPUT);

    pinMode(motorBPin1, OUTPUT);
    pinMode(motorBPin2, OUTPUT);
    pinMode(motorBPWM, OUTPUT);

    steeringServo.attach(servoPin);

    mpu.initialize();
    mpu.setZGyroOffset(51);  // calibrado
}

float Robot::pingMeters(NewPing &sonar) {
    unsigned int echo_us = sonar.ping();
    if (echo_us == 0) return 0.0f;
    return echo_us * 0.0001715f;
}

// --- Distance selector ---
float Robot::getDistance(char side) {
  float d = 0.0f;
  if (DIR == 'A') {
    // DIR 'A' → sonar1 is Outer (O), sonar2 is Inner (I)
    d = (side == 'O') ? pingMeters(sonar1)
      : (side == 'I') ? pingMeters(sonar2)
      : 0.0f;
  } else if (DIR == 'H') {
    // DIR 'H' → flipped
    d = (side == 'O') ? pingMeters(sonar2)
      : (side == 'I') ? pingMeters(sonar1)
      : 0.0f;
  }

  if (d <= 0.0f) return 0.0f;   // keep "no echo" as 0.0
  return d + sensor_x_offset;   // apply offset only to valid distances
}

float Robot::getPoseXFromSensors(int setpoint) {
    float xMeasured = 0.0f;

    // Choose wall based on setpoint
    if (setpoint <= 2) {
        xMeasured = getDistance('O');           // distance from outer wall
    } else {
        xMeasured = 1.0f - getDistance('I');    // corridor width assumed = 1.0 m
    }

    // Treat invalid sonar return (0.0 from getDistance) as no measurement
    if (xMeasured <= 0.0f) return -1.0f;

    // Accept only if close to current x estimate and heading is nearly straight
    if (fabsf(heading) < 5.0f) {
        return xMeasured;
    }

    return -1.0f;  // rejected measurement
}


// --- Movimiento ---
void Robot::setDriveSpeed(float speed_mps) { // TODO: change to power-based later
    v = speed_mps;
    int sign = (speed_mps >= 0.0f) ? 1 : -1;
    long absScaled = (long)(fabsf(speed_mps) * 1000.0f);
    long pwmValue = map(absScaled, 0, 370, 0, 255);
    int pwm = (int)pwmValue * sign;
    applyPWM(pwm, motorBPin1, motorBPin2, motorBPWM);
}

void Robot::applyPWM(int pwm, uint8_t pin1, uint8_t pin2, uint8_t pwmPin) {
    digitalWrite(pin1, pwm < 0);
    digitalWrite(pin2, pwm > 0);
    analogWrite(pwmPin, abs(pwm));
}

// --- Dirección ---
void Robot::setSteerAngle(float targetAngle) {
    // Apply DIR flip first
    float adjustedTarget = (DIR == 'A') ? -targetAngle : targetAngle;

    // Asymmetry gain AFTER flip
    float asym_gain = (adjustedTarget < 0.0f) ? STEER_RATIO_LEFT : STEER_RATIO_RIGHT;

    // Apply gain
    adjustedTarget *= asym_gain;

    // Constrain only now
    adjustedTarget = constrain(adjustedTarget, -maxSteeringAngle, maxSteeringAngle);

    // Map to servo
    float simulatedAngle = centerSteering - adjustedTarget * steer_ratio;

    steeringServo.write(simulatedAngle);
}

// --- Dirección de marcha ---
void Robot::setDir(char dir) {
    if (dir == 'A' || dir == 'H') {
        DIR = dir;
    }
    // else ignore invalid input to avoid undefined behavior
}

// --- Pose y localización ---
void Robot::setPoseX(float val) { x = val; }
void Robot::setPoseY(float val) { y = val; }
void Robot::setPoseH(float val) { heading = val; }

float Robot::getPose(char axis) {
    if (axis == 'x') return x;
    if (axis == 'y') return y;
    if (axis == 'h') return heading;
    return 0.0f;
}

void Robot::updatePose() {
    unsigned long now = micros();

    if (lastUpdateTime == 0) {
        lastUpdateTime = now;
        return;
    }
    float dt = (now - lastUpdateTime) / 1e6f;
    lastUpdateTime = now;

    // --- Heading (giroscopio) ---
    mpu.getRotation(&gx, &gy, &gz);
    float gz_deg_per_sec = (float)gz / 131.0f;
    float angleZ_deg = gz_deg_per_sec * dt;
    heading += (DIR == 'A') ? angleZ_deg : -angleZ_deg;

    // --- Actualización de X / Y ---
    x += v * sin(heading * DEG_TO_RAD) * dt;
    y += v * cos(heading * DEG_TO_RAD) * dt;
}

void Robot::setZGyroOffset(int offset) {
  mpu.setZGyroOffset(offset);
}

void Robot::detachSteering() {
    steeringServo.detach();
    pinMode(servoPin, INPUT); // optional: make pin high-Z
}
