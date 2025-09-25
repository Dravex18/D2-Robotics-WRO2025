#ifndef ROBOT_H
#define ROBOT_H

#include <AS5600.h>
#include <Servo.h>
#include <NewPing.h>
#include "I2Cdev.h"
#include "MPU6050.h"
#include "LowPassFilter.h"

class Robot {
  public:
    Robot();
    void begin();

    // --- Pose y localización ---
    void setPoseX(float val);                 // Asigna valor a X
    void setPoseY(float val);                 // Asigna valor a Y
    void setPoseH(float val);                 // Asigna heading (rotación)
    float getPose(char axis);                 // Obtiene X, Y o heading según 'x', 'y', 'h'
    void updatePose();                        // Actualiza la pose a partir de sensores y modo seleccionado
    float getDistance(char side);
    float getPoseXFromSensors(int setpoint);
    void detachSteering();

    // --- Movimiento y dirección ---
    void setDriveSpeed(float speed_mps);     // Establece velocidad de desplazamiento
    void setSteerAngle(float targetAngle);    // Define ángulo absoluto de dirección
    void setZGyroOffset(int offset);

    // --- Dirección y sensores ---
    void setDir(char dir);                 // 'A' (antihorario) o 'H' (horario)

  private:
    void applyPWM(int pwm, uint8_t pin1, uint8_t pin2, uint8_t pwmPin);

    // Pines
    static const uint8_t trigPin1 = 15, echoPin1 = 14;      // Outer si DIR == 'A'
    static const uint8_t trigPin2 = 18, echoPin2 = 19;      // Inner si DIR == 'A'
    static constexpr float MAX_DIST_M = 0.6f; 
    static const uint8_t motorAPin1 = 6, motorAPin2 = 7, motorAPWM = 10;
    static const uint8_t motorBPin1 = 8, motorBPin2 = 9, motorBPWM = 11;
    static const uint8_t servoPin = 20;

    // Componentes
    Servo steeringServo;
    MPU6050 mpu;
    NewPing sonar1;  // declare only
    NewPing sonar2;
    float pingMeters(NewPing &sonar);

    // Estado
    float x = 0, y = 0, heading = 0;
    float v = 0;
    char  DIR = 'A';                       // 'A' by default
    unsigned long lastUpdateTime = 0;
    

    // Sensor de giro
    int16_t gx, gy, gz;

    // Offsets y configuración
    const float sensor_x_offset = 0.04;
    const float maxSteeringAngle = 28.0;
    const float steer_ratio=2.76;
    const float centerSteering = 82;

    const float STEER_RATIO_LEFT  = 1.00f;  // gain when targetAngle > 0  (left)
    const float STEER_RATIO_RIGHT = 0.76f;  // gain when targetAngle < 0  (right) 
};

#endif

