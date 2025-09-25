"""
=========================================================
 Raspberry Pi Camera V3 – Auto Calibration & Lock Script
=========================================================

This script quickly calibrates the camera by letting auto-exposure,
auto-white-balance, and auto-focus run for ~0.8s. It then:

1. Reads the stabilized values (exposure, gain, color gains, focus).
2. Prints them so you can copy into your own robot/vision code.
3. Locks the camera with those fixed settings (no more changes).
4. Keeps the pipeline alive so you can visually confirm.

Use this to grab good starting values and then run your main program
with fixed camera parameters for consistent results.
"""

from picamera2 import Picamera2
import time

picam2 = Picamera2()

# Fast, low-latency pipeline for calibration
config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "YUV420"},
    buffer_count=3
)
picam2.configure(config)
picam2.start()

# 1) Let AE/AWB/AF run briefly (auto)
picam2.set_controls({
    "AeEnable": True,
    "AwbEnable": True,
    "AfMode": 2,              # continuous AF for a moment
})
time.sleep(0.8)               # ~0.5–1.0 s settle time

# 2) Read settled values
meta = picam2.capture_metadata()
exp_us     = int(meta.get("ExposureTime", 4000))
again      = float(meta.get("AnalogueGain", 1.5))
rg, bg     = meta.get("ColourGains", (1.5, 1.2))
lens_pos   = float(meta.get("LensPosition", 0.5))

print("\n--- CALIBRATED VALUES (copy these) ---")
print(f"ExposureTime (us): {exp_us}")
print(f"AnalogueGain     : {again:.3f}")
print(f"ColourGains (R,B): ({rg:.3f}, {bg:.3f})")
print(f"LensPosition     : {lens_pos:.3f}")

# 3) LOCK them so they stop changing
picam2.set_controls({
    "AeLocked": True,
    "AwbLocked": True,
})
# Freeze focus by switching to manual at the last good position
picam2.set_controls({
    "AfMode": 0,              # manual focus
    "LensPosition": lens_pos
})

print("\nLocked. Use these fixed settings in your robot code:\n")
print("picam2.set_controls({")
print(f"    'AeEnable': False, 'AwbEnable': False,")
print(f"    'ExposureTime': {exp_us}, 'AnalogueGain': {again:.3f},")
print(f"    'ColourGains': ({rg:.3f}, {bg:.3f}),")
print(f"    'AfMode': 0, 'LensPosition': {lens_pos:.3f}")
print("})")

# keep running so you can visually verify if you want
try:
    while True:
        picam2.capture_array("main")  # discard; just keeps pipeline alive
except KeyboardInterrupt:
    pass
