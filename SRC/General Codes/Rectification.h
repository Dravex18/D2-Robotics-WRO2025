#pragma once
#include <Arduino.h>
#include <math.h>

/*
 * Rectification (forward-only, auto-reset, using y_pos as window)
 * --------------------------------------------------------------
 * - enable(y_start, y_finish) arms a new capture window.
 * - sample(y_pos, x_measured) is called every tick (e.g., 50 ms).
 * - Sampling begins once y_pos >= y_start.
 * - When y_pos >= y_finish: computes yaw, sets isReady()=true, and auto-disables.
 * - getYawDeg() returns the yaw ONCE and clears it (mailbox style).
 * - getLastXMeasured() returns the last lateral measurement (0.0 if none).
 */
class Rectification {
public:
  static constexpr size_t MAX_SAMPLES = 96; // adjust as needed

  // Start a fresh capture window
  void enable(float y_start, float y_finish) {
    y_start_ = y_start;
    y_finish_ = y_finish;

    enabled_ = true;
    started_ = false;
    ready_   = false;

    n_ = 0;
    yaw_deg_ = 0.0f;
  }

  void disable() { enabled_ = false; }

  bool isEnabled() const { return enabled_; }
  bool isReady()   const { return ready_;   }

  // One-shot getter: returns yaw and clears flag
  float getYawDeg() {
    if (!ready_) return 0.0f;
    float yaw = yaw_deg_;
    yaw_deg_ = 0.0f;
    ready_   = false;
    return yaw;
  }

  float getLastXMeasured() const {
    if (n_ == 0) return 0.0f;
    return xs_[n_ - 1];
  }

  size_t getSampleCount() const { return n_; }

  // Called every tick (e.g., 50 ms)
  void sample(float y_pos, float x_measured) {
    if (!enabled_) return;

    // Wait until we cross y_start
    if (!started_) {
      if (y_pos >= y_start_) started_ = true;
      else return;
    }

    // If we've reached/passed y_finish, compute & finalize
    if (y_pos >= y_finish_) {
      if (n_ >= 2) computeYaw();
      enabled_ = false;
      ready_   = true;
      return;
    }

    // Store sample
    if (n_ < MAX_SAMPLES) {
      ys_[n_] = y_pos;
      xs_[n_] = x_measured;
      ++n_;
    }
  }

private:
  void computeYaw() {
    double sy = 0.0, sx = 0.0;
    for (size_t i = 0; i < n_; ++i) { sy += ys_[i]; sx += xs_[i]; }
    const double ybar = sy / n_;
    const double xbar = sx / n_;

    double Syy = 0.0, Sxy = 0.0;
    for (size_t i = 0; i < n_; ++i) {
      const double dy = ys_[i] - ybar;
      Syy += dy * dy;
      Sxy += dy * (xs_[i] - xbar);
    }
    if (Syy <= 0.0) { ready_ = false; return; }

    double m = Sxy / Syy;      
    if (m < -1.0) m = -1.0;
    if (m >  1.0) m =  1.0;

    yaw_deg_ = static_cast<float>(asin(m) * 180.0 / M_PI);
  }

  // Window on y_pos
  float y_start_  = 0.0f;
  float y_finish_ = 0.0f;

  // State
  bool  enabled_ = false;
  bool  started_ = false;
  bool  ready_   = false;

  // Data
  float ys_[MAX_SAMPLES];
  float xs_[MAX_SAMPLES];
  size_t n_ = 0;

  // Result
  float yaw_deg_ = 0.0f;
};
