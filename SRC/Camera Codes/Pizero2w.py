from picamera2 import Picamera2
from queue import Queue
import threading, numpy as np
import cv2, serial

cv2.setNumThreads(1)  # force OpenCV to run single-threaded (avoid overhead with our own threads)

# ==== your pre-calibrated values ====
EXPOSURE_US   = 4000
GAIN          = 5
COLOUR_GAINS  = (1.5, 1.2)
LENS_POSITION = 1

# ==== camera: low-latency preview (BGR) ====
picam2 = Picamera2()
cfg = picam2.create_preview_configuration(
    main={"size": (320, 240), "format": "BGR888"},   # << BGR for direct HSV
    buffer_count=3
)
picam2.configure(cfg)
picam2.start()

# manual/locked imaging
picam2.set_controls({
    "AeEnable": False, "AwbEnable": False,
    "ExposureTime": EXPOSURE_US, "AnalogueGain": GAIN,
    "ColourGains": COLOUR_GAINS,
    "AfMode": 0, "LensPosition": LENS_POSITION
})

# ===============================
# HSV THRESHOLDS (OpenCV scale!)
# OpenCV HSV: H∈[0..179], S∈[0..255], V∈[0..255]
# Normal HSV (degrees) = H_opencv * 2  (e.g., H=45 → 90° = green)
# ===============================
lowGreen = np.array([45, 60, 50],  dtype=np.uint8)   # dark-tolerant green
upGreen  = np.array([85, 255, 255], dtype=np.uint8)
lowRed1  = np.array([0,  60, 45],   dtype=np.uint8)  # red near 0°
upRed1   = np.array([10, 255, 255], dtype=np.uint8)
lowRed2  = np.array([170,60, 45],   dtype=np.uint8)  # red near 180°
upRed2   = np.array([179,255,255],  dtype=np.uint8)

# ===============================
# STATE / ROIs / FSM GLOBALS
# ===============================
pos = 0
#             0.5m   1m
min_pixels = [1200, 200]   # tune
roi_colors = {}           # dict: {roi_key: 'R'/'G'/'E'}
near_rois = {'A', 'G'}

# ROIs (x, y, w, h) — working frame: 320x240
rois = {
    'A': (223, 0, 97, 134),   #
    'B': (79, 0, 145, 134),   #
    'C': (194, 47, 110, 87),  #
    'D': (21,  47, 139, 87),  #
    'E': (58,  47, 203, 87),  #
    'F': (159, 47, 139, 87),  #
    'G': (58,  47, 203, 87),  #
    'H': (124, 0, 196, 134),  #
    'I': (103, 41,  50, 38),
    'J': (41,  47,  78, 87),  #
}

# pos          0        1    2     3     4     5     6
zones_cc = [["A", "B"], "B", "C", "D", "E", "F", "G"]  # << fixed missing comma
transitions_cc = {
    (0, 'I'): 2, (0, 'E'): 1, (0, 'O'): 1,
    (1, 'I'): 3, (1, 'E'): 4, (1, 'O'): 5,
    (2, 'I'): 3, (2, 'E'): 4, (2, 'O'): 5,
    (3, 'I'): 2, (3, 'E'): 2, (3, 'O'): 6,
    (4, 'I'): 2, (4, 'E'): 2, (4, 'O'): 6,
    (5, 'I'): 2, (5, 'E'): 6, (5, 'O'): 6,
    (6, 'I'): 3, (6, 'E'): 4, (6, 'O'): 5,
}

zones_c = ["H", "J", "G", "F", "E", "D"]
transitions_c = {
    (0, 'I'): 1, (0, 'E'): 1, (0, 'O'): 2,
    (1, 'I'): 3, (1, 'E'): 4, (1, 'O'): 5,
    (2, 'I'): 3, (2, 'E'): 4, (2, 'O'): 5,
    (3, 'I'): 1, (3, 'E'): 1, (3, 'O'): 2,
    (4, 'I'): 1, (4, 'E'): 1, (4, 'O'): 2,
    (5, 'I'): 1, (5, 'E'): 2, (5, 'O'): 2,
}

# ==== inter-thread data ====
q_frames = Queue(maxsize=1)
result_lock = threading.Lock()

def wait_for_input() -> str:
    """
    Block until ANY byte arrives on Serial and return it as a 1-char string.
    Note: only blocks the calling thread. Other threads keep running.
    """
    b = ser.read(1)                     # blocks (use ser.timeout=None for infinite)
    if not b:                           # in case a finite timeout was set
        return ''
    return b.decode('ascii', errors='ignore')

def send_letter(letter: str) -> None:
    """
    Send exactly one ASCII character through Serial.
    Raises ValueError if you pass more than one character.
    """
    if len(letter) != 1:
        raise ValueError("send_letter() requires a single character, e.g. 'T'")
    ser.write(letter.encode('ascii', errors='ignore'))

def color_identifier(frame_bgr, roi):
    """
    ROI-only + channel-wise gating (fast).
    """
    x, y, w, h = rois[roi]
    roi_bgr = frame_bgr[y:y+h, x:x+w]                 # view (no copy)
    roi_hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)

    # Split: H∈[0..179], S/V∈[0..255]. Normal hue (degrees) = H*2
    H = roi_hsv[:, :, 0]
    S = roi_hsv[:, :, 1]
    V = roi_hsv[:, :, 2]

    # S/V gate once (cheap 1-channel thresholds)
    Smin = int(min(lowGreen[1], lowRed1[1], lowRed2[1]))
    Vmin = int(min(lowGreen[2], lowRed1[2], lowRed2[2]))
    _, s_gate = cv2.threshold(S, Smin-1, 255, cv2.THRESH_BINARY)
    _, v_gate = cv2.threshold(V, Vmin-1, 255, cv2.THRESH_BINARY)
    sv_gate   = cv2.bitwise_and(s_gate, v_gate)

    # Green hue [45..85] (~90°..170°)
    g_hue  = cv2.inRange(H, int(lowGreen[0]), int(upGreen[0]))
    g_mask = cv2.bitwise_and(g_hue, sv_gate)
    cntG   = int(cv2.countNonZero(g_mask))

    # Red wrap: [0..10] ∪ [170..180]
    r1_hue = cv2.inRange(H, int(lowRed1[0]), int(upRed1[0]))
    r2_hue = cv2.inRange(H, int(lowRed2[0]), int(upRed2[0]))
    r_hue  = cv2.bitwise_or(r1_hue, r2_hue)
    r_mask = cv2.bitwise_and(r_hue, sv_gate)
    cntR   = int(cv2.countNonZero(r_mask))

    # NOTE: use ROI key here (no undefined current_zone)
    idx = 0 if roi in near_rois else 1
    thr = min_pixels[idx]

    if max(cntG, cntR) > thr:
        color = 'R' if cntR > cntG else 'G'
    else:
        color = 'E'

    return color

# ===============================
# CAPTURE THREAD (BGR frames)
# ===============================
def t_capture():
    while True:
        req = picam2.capture_request()
        frame = req.make_array("main")  # copy needed before release
        req.release()
        q_frames.put(frame)  # blocks if processing hasn't consumed (OK if processing is faster)

# ===============================
# PROCESS THREAD
# - always uses latest frame
# ===============================
def t_process():
    global roi_colors
    while True:
        frame_bgr = q_frames.get()   # always newest frame (Queue size = 1)

        # ---- SNAPSHOT SHARED STATE (tiny critical section) ----
        with result_lock:
            local_pos = pos
            local_zone = zones[local_pos]     # zones treated read-only after init
            local_direction = direction

        # normalize: single string → list with one element
        roi_list = local_zone if isinstance(local_zone, (list, tuple)) else [local_zone]

        # ---- HEAVY WORK OUTSIDE THE LOCK ----
        local_colors = {}
        for rk in roi_list:
            c = color_identifier(frame_bgr, rk)
            local_colors[rk] = c

        # ---- COMMIT RESULTS ATOMICALLY (tiny critical section) ----

        with result_lock:
            local_result = 'E'

            for rk, color in local_colors.items():
                roi_colors[rk] = color

                # Compute lane using the snapshotted direction
                if color == 'E':
                    lane = 'E'
                else:
                    if local_direction == 'A':
                        lane = 'I' if color == 'G' else 'O'
                    else:
                        lane = 'O' if color == 'G' else 'I'


                if 'B' in roi_list:  # SPECIAL CASE (same position, different zones)
                    position_result[1 if rk == 'B' else 0] = lane  # zones_cc = [["A","B"], "B", ...
                else:
                    """
                    # len(roi_list) can be 1 or 2 here (no 'B')
                    if len(roi_list) == 2:
                        if local_result == 'E' and color != 'E':
                            local_result = lane
                    else:
                    """
                    # single-ROI: just write this lane
                    position_result[local_pos] = lane
            """
            # If it was the 2-ROI (no 'B') case, commit once after the loop
            if 'B' not in roi_list and len(roi_list) == 2:
                position_result[local_pos] = local_result
            """


# === MAIN THREAD: blocking serial ===
ser = serial.Serial('/dev/serial0', 115200, timeout=None, write_timeout=0)

send_letter('S')
direction = wait_for_input()
if direction == 'A':
    transitions = transitions_cc
    zones = zones_cc
else:
    transitions = transitions_c
    zones = zones_c
position_result = ['E'] * len(zones)


# Start threads **after** direction/zones are set
threading.Thread(target=t_capture,  daemon=True).start()
threading.Thread(target=t_process,  daemon=True).start()


while True:
    cmd = wait_for_input()
    if cmd == 'R':
        # atomically read lane and advance pos
        with result_lock:
            lane = position_result[pos]
            send_letter(lane)
            pos = transitions.get((pos, lane), pos)
        # current_zone will be read on next process loop iteration
    elif cmd == 'F':
        break
