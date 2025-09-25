"""
=========================================================
 Raspberry Pi Camera V3 – Latency & FPS Measurement
   (toggles for AF, AE/AWB, and ISP cost)
=========================================================

Reports once per second:
- avg capture→userland latency (ms)
- 95th percentile latency (p95)
- frames per second (FPS)

Toggles:
- AUTO_EXPOSURE / AUTO_WB: enable or lock AE/AWB
- AUTO_FOCUS: enable continuous AF or lock manual focus
- LOW_ISP_COST: disable denoise/sharpen to reduce ISP load
- FRAME_DURATION_LOCK: lock frame time (try for steady fps; mode-dependent)

Flip the flags to compare how each feature impacts latency & FPS.
"""

from picamera2 import Picamera2
import time, statistics

# ======= TOGGLES =======
AUTO_EXPOSURE     = True    # True: AE on;  False: manual exposure
AUTO_WB           = True    # True: AWB on; False: manual color gains
AUTO_FOCUS        = False   # True: continuous AF; False: manual lens position
LOW_ISP_COST      = True    # True: minimal denoise/sharpen; False: default
FRAME_DURATION_LOCK = False # True: force fixed frame time (mode must support)

# ======= CAMERA CONFIG =======
W, H = 1536, 864
FORMAT = "BGR888"     # BGR for OpenCV; heavier than YUV420
BUFFER_COUNT = 3
REPORT_EVERY_S = 1.0

# Manual values used when autos are off (tweak after a quick auto-cal run)
MANUAL_EXPOSURE_US = 4000
MANUAL_AGAIN       = 1.0
MANUAL_COLOUR_GAINS = (1.5, 1.2)  # (R, B)
MANUAL_LENS_POS    = 0.50         # 0..1 (approx), depends on module & focus distance

# ======= SETUP =======
picam2 = Picamera2()
cfg = picam2.create_video_configuration(
    main={"size": (W, H), "format": FORMAT},
    buffer_count=BUFFER_COUNT
)
picam2.configure(cfg)

controls = {}

# AE / AWB
if AUTO_EXPOSURE:
    controls["AeEnable"] = True
else:
    controls.update({
        "AeEnable": False,
        "ExposureTime": MANUAL_EXPOSURE_US,
        "AnalogueGain": MANUAL_AGAIN,
    })

if AUTO_WB:
    controls["AwbEnable"] = True
else:
    controls.update({
        "AwbEnable": False,
        "ColourGains": MANUAL_COLOUR_GAINS,
    })

# AF
if AUTO_FOCUS:
    # 2 = Continuous AF; 1 = Auto (single trigger); 0 = Manual
    controls["AfMode"] = 2
else:
    controls.update({
        "AfMode": 0,                  # manual focus
        "LensPosition": MANUAL_LENS_POS,
    })

# ISP cost
if LOW_ISP_COST:
    controls.update({
        "NoiseReductionMode": 0,      # minimal denoise
        "Sharpness": 0.0,             # avoid extra sharpening work
        # "EdgeEnhancementMode": 0,   # if available in your build
    })

# Frame duration lock (try to stabilize fps if your mode supports it)
if FRAME_DURATION_LOCK:
    # Example: lock to ~120 fps if sensor/mode allows (8333 µs)
    # Use values your mode supports; otherwise the driver may ignore it.
    controls["FrameDurationLimits"] = (8333, 8333)

picam2.set_controls(controls)
print("Controls:", controls)

# ======= METRICS =======
latencies_ms = []
frame_counter = 0
last_report = time.monotonic()
last_count = 0

def p_percentile(values, p=0.95):
    if not values:
        return 0.0
    arr = sorted(values)
    if len(arr) == 1:
        return arr[0]
    k = int(round(p * (len(arr) - 1)))
    return arr[k]

def on_post(req):
    global frame_counter
    md = req.get_metadata()
    ts_sensor_ns = md.get("SensorTimestamp")
    if ts_sensor_ns is not None:
        now_ns = time.monotonic_ns()
        latencies_ms.append((now_ns - ts_sensor_ns) / 1e6)
    frame_counter += 1
    # DO NOT release here; Picamera2 handles it.

picam2.post_callback = on_post
picam2.start()
print("Measuring latency + FPS… Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(0.01)
        now = time.monotonic()
        if (now - last_report) >= REPORT_EVERY_S:
            data = latencies_ms[:]
            latencies_ms.clear()

            count_now = frame_counter
            frames = count_now - last_count
            elapsed = now - last_report if (now - last_report) > 0 else 1e-9
            fps = frames / elapsed

            if data:
                avg = statistics.fmean(data)
                p95 = p_percentile(data, 0.95)
                print(f"avg {avg:.2f} ms | p95 {p95:.2f} ms | n={len(data)} | FPS {fps:.1f}")
            else:
                print(f"no frames | FPS {fps:.1f}")

            last_report = now
            last_count = count_now
except KeyboardInterrupt:
    pass
finally:
    picam2.stop()
