# ====== SIM MODE: Keyboard + Image Replay (keeps your original code commented) ======
from queue import Queue
import threading, numpy as np
import cv2, os, glob, time
# import serial
# from picamera2 import Picamera2

cv2.setNumThreads(1)  # keep OpenCV single-threaded (your original)

# ==== your pre-calibrated values (kept for real-camera mode) ====
EXPOSURE_US   = 4000
GAIN          = 5
COLOUR_GAINS  = (1.5, 1.2)
LENS_POSITION = 1

# ===============================
# MODE SWITCHES
# ===============================
INPUT_MODE = "keyboard"  # "keyboard" (sim) or "serial"
FRAME_SOURCE = "images"  # "images" (sim) or "camera"

# ===============================
# IMAGE REPLAY CONFIG (SIM ONLY)
# ===============================
# Folder with your JPG images:
IMAGE_DIR = r"C:\Users\davis\OneDrive\Desktop\WRO 2025\programas\Camara configuration\nwimages_resized_320x240"

# Global image list & index (populated at runtime)
image_files = []
current_idx = 0
img_lock = threading.Lock()

def build_image_list():
    """Find all JPGs in IMAGE_DIR, sorted by name."""
    if not os.path.isdir(IMAGE_DIR):
        raise FileNotFoundError(f"IMAGE_DIR not found: {IMAGE_DIR}")
    files = glob.glob(os.path.join(IMAGE_DIR, "*.jpg"))
    files.sort()
    if not files:
        raise FileNotFoundError(f"No JPGs found in {IMAGE_DIR}")
    return files

def list_images(max_rows=50):
    """Print a compact list of image basenames (no extension)."""
    print(f"\n[IMAGES] {len(image_files)} file(s) in {IMAGE_DIR}:")
    for i, p in enumerate(image_files[:max_rows]):
        print(f"  {i:3d}: {os.path.splitext(os.path.basename(p))[0]}")
    if len(image_files) > max_rows:
        print(f"  ... (+{len(image_files)-max_rows} more)")
    print()

def find_index_by_basename(name_no_ext: str):
    """Return index of image whose basename (no extension) matches, else -1."""
    target = name_no_ext.lower()
    for i, p in enumerate(image_files):
        base = os.path.splitext(os.path.basename(p))[0].lower()
        if base == target:
            return i
    return -1

# ===============================
# HSV THRESHOLDS (OpenCV scale!)
# ===============================
lowGreen = np.array([45, 45, 45],  dtype=np.uint8)
upGreen  = np.array([85, 255, 255], dtype=np.uint8)
lowRed1  = np.array([0,  45, 45],   dtype=np.uint8)
upRed1   = np.array([10, 255, 255], dtype=np.uint8)
lowRed2  = np.array([170,45, 45],   dtype=np.uint8)
upRed2   = np.array([179,255,255],  dtype=np.uint8)

# ===============================
# STATE / ROIs / FSM GLOBALS
# ===============================
pos = 2
min_pixels = [1200, 200]     # [near, far]
roi_colors = {}
near_rois = {'A', 'G', 'H'}

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

# pos          0          1    2     3     4     5     6
zones_cc = [["A", "B"],  "B", "C",  "D",  "E",  "F",  "G"]
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

# ===============================
# I/O ABSTRACTION
# ===============================
def wait_for_input() -> str:
    if INPUT_MODE == "keyboard":
        try:
            s = input("Key [A=CCW, C=CW, R=read/advance, P=set pos, "
                      "T=test img, N=next, B=back, L=list, I=info, F=finish]: ").strip().upper()
            return s[:1] if s else ''
        except EOFError:
            return 'F'
    # === REAL SERIAL (kept, commented) ===
    # b = ser.read(1)
    # if not b: return ''
    # return b.decode('ascii', errors='ignore')

def send_letter(letter: str) -> None:
    if len(letter) != 1:
        raise ValueError("send_letter() requires a single character, e.g. 'T'")
    if INPUT_MODE == "keyboard":
        print(f"[TX] {letter}")
    else:
        pass
        # ser.write(letter.encode('ascii', errors='ignore'))

# ===============================
# COLOR ID
# ===============================
def color_identifier(frame_bgr, roi):
    x, y, w, h = rois[roi]
    roi_bgr = frame_bgr[y:y+h, x:x+w]
    roi_hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)

    H = roi_hsv[:, :, 0]
    S = roi_hsv[:, :, 1]
    V = roi_hsv[:, :, 2]

    Smin = int(min(lowGreen[1], lowRed1[1], lowRed2[1]))
    Vmin = int(min(lowGreen[2], lowRed1[2], lowRed2[2]))
    _, s_gate = cv2.threshold(S, Smin-1, 255, cv2.THRESH_BINARY)
    _, v_gate = cv2.threshold(V, Vmin-1, 255, cv2.THRESH_BINARY)
    sv_gate   = cv2.bitwise_and(s_gate, v_gate)

    g_hue  = cv2.inRange(H, int(lowGreen[0]), int(upGreen[0]))
    g_mask = cv2.bitwise_and(g_hue, sv_gate)
    cntG   = int(cv2.countNonZero(g_mask))

    r1_hue = cv2.inRange(H, int(lowRed1[0]), int(upRed1[0]))
    r2_hue = cv2.inRange(H, int(lowRed2[0]), int(upRed2[0]))
    r_hue  = cv2.bitwise_or(r1_hue, r2_hue)
    r_mask = cv2.bitwise_and(r_hue, sv_gate)
    cntR   = int(cv2.countNonZero(r_mask))

    idx = 0 if roi in near_rois else 1
    thr = min_pixels[idx]
    if max(cntG, cntR) > thr:
        color = 'R' if cntR > cntG else 'G'
    else:
        color = 'E'
    return color

# ===============================
# CAPTURE THREADS
# ===============================
def t_capture_images():
    """Continuously publish the CURRENT image (set by index)."""
    while True:
        with img_lock:
            path = image_files[current_idx]
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is None:
            print(f"[WARN] Could not read: {path}")
            time.sleep(0.05)
            continue
        frame_bgr = cv2.resize(img, (320, 240), interpolation=cv2.INTER_AREA)
        if not q_frames.empty():
            try: q_frames.get_nowait()
            except: pass
        q_frames.put(frame_bgr)
        time.sleep(0.01)  # small sleep to avoid burning CPU

# def t_capture_camera(): ...

# ===============================
# PROCESS THREAD
# ===============================
position_result = []  # set after direction/zones selection

def t_process():
    global roi_colors
    while True:
        frame_bgr = q_frames.get()
        with result_lock:
            local_pos = pos
            local_zone = zones[local_pos]
            local_direction = direction

        roi_list = local_zone if isinstance(local_zone, (list, tuple)) else [local_zone]

        local_colors = {}
        for rk in roi_list:
            c = color_identifier(frame_bgr, rk)
            local_colors[rk] = c

        with result_lock:
            for rk, color in local_colors.items():
                roi_colors[rk] = color
                if color == 'E':
                    lane = 'E'
                else:
                    if local_direction == 'A':
                        lane = 'I' if color == 'G' else 'O'
                    else:
                        lane = 'O' if color == 'G' else 'I'

                if 'B' in roi_list:
                    position_result[1 if rk == 'B' else 0] = lane
                else:
                    position_result[local_pos] = lane

# ===============================
# HELPERS
# ===============================
def ask_position():
    while True:
        try:
            mx = len(zones) - 1
            s = input(f"Pick start pos [0..{mx}]: ").strip()
            p = int(s)
            if 0 <= p <= mx:
                return p
            print(f"Out of range. Enter a number between 0 and {mx}.")
        except Exception:
            print("Invalid input. Enter an integer.")

def ask_image_by_name():
    """Ask for basename (no extension), switch current image if found."""
    name = input("Image name (without .jpg): ").strip()
    if not name:
        print("[IMG] Empty name; keeping current image.")
        return
    idx = find_index_by_basename(name)
    if idx < 0:
        print(f"[IMG] '{name}.jpg' not found in {IMAGE_DIR}. Try 'L' to list.")
        return
    global current_idx
    with img_lock:
        current_idx = idx
    show_current_image_info()

def show_current_image_info():
    with img_lock:
        p = image_files[current_idx]
        b = os.path.basename(p)
    print(f"[IMG] current[{current_idx}] -> {b}")

# ===============================
# BOOTSTRAP
# ===============================
send_letter('S')

# Build image list before anything else
image_files = build_image_list()
with img_lock:
    current_idx = 0
list_images(max_rows=30)
show_current_image_info()

# Choose direction
while True:
    direction = wait_for_input()
    if direction in ('A', 'C'):
        break
    print("Choose direction first: A (CCW) or C (CW).")

if direction == 'A':
    transitions = transitions_cc
    zones = zones_cc
else:
    transitions = transitions_c
    zones = zones_c

position_result = ['E'] * len(zones)
with result_lock:
    pos = ask_position()
print(f"[INIT] Direction={'CCW' if direction=='A' else 'CW'}; start pos={pos}; zone={zones[pos]}")

# Start threads
if FRAME_SOURCE == "images":
    threading.Thread(target=t_capture_images, daemon=True).start()
# else: threading.Thread(target=t_capture_camera, daemon=True).start()
threading.Thread(target=t_process, daemon=True).start()

# ===============================
# MAIN LOOP (keyboard-based protocol)
# ===============================
print("\nControls: A=CCW | C=CW | R=read+advance | P=set pos | "
      "T=test img | N=next | B=back | L=list | I=info | F=finish\n")

while True:
    cmd = wait_for_input()
    if not cmd:
        continue

    if cmd in ('A', 'C'):
        with result_lock:
            new_dir = cmd
            if new_dir != direction:
                direction = new_dir
                if direction == 'A':
                    transitions = transitions_cc
                    zones = zones_cc
                else:
                    transitions = transitions_c
                    zones = zones_c
                position_result = ['E'] * len(zones)
                pos = 0
        print(f"[DIR] Direction set to {'CCW' if direction=='A' else 'CW'}; pos reset to 0.")

    elif cmd == 'P':
        with result_lock:
            pos = ask_position()
        print(f"[POS] pos set to {pos}; zone={zones[pos]}")

    elif cmd == 'T':
        ask_image_by_name()

    elif cmd == 'N':
        with img_lock:
            current_idx = (current_idx + 1) % len(image_files)
        show_current_image_info()

    elif cmd == 'B':
        with img_lock:
            current_idx = (current_idx - 1) % len(image_files)
        show_current_image_info()

    elif cmd == 'L':
        list_images(max_rows=60)

    elif cmd == 'I':
        show_current_image_info()

    elif cmd == 'R':
        with result_lock:
            lane = position_result[pos]
            print(f"[pos {pos}] -> lane: {lane}")
            send_letter(lane)
            #pos = transitions.get((pos, lane), pos)

    elif cmd == 'F':
        print("Finishing.")
        break

    else:
        print("Unknown key. Use A, C, R, P, T, N, B, L, I, or F.")
