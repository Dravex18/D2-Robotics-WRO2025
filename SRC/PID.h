#ifndef PID_h
#define PID_h

class PID {
  public:
    PID(float kp, float ki, float kd);
    void setTunings(float kp, float ki, float kd);
    void setOutputLimits(float min, float max);
    void enable();
    void disable();
    bool isEnabled();
    void reset();
    float compute(float setpoint, float input);  // ahora recibe setpoint e input

  private:
    float _kp, _ki, _kd;
    float _integral;
    float _outputMin, _outputMax;
    bool _enabled;
    float _lastOutput;
    float _lastPError = 0;
    unsigned long lastUpdateTime = 0;
};

#endif
