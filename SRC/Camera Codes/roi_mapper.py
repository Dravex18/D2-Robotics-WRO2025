"""
=========================================================
 ROI Mapper – Angle ↔ Pixel Conversion + Visualization
=========================================================

This tool converts Regions of Interest (ROIs) defined in camera
angles (degrees from the image center) into pixel rectangles, and
vice versa. It uses the camera’s horizontal and vertical FOV plus
image resolution to do the mapping.

Features:
- Define ROIs in angular coordinates: (v_min, v_max, h_min, h_max).
- Convert to pixel (x, y, w, h) rectangles.
- Display all ROIs on a blank canvas or on a real image.
- Draws reference cross lines (center vertical/horizontal).
- Exports ROI rectangles to CSV and a preview PNG.

Usage:
- Switch between "blank" mode (white canvas) and "image" mode
  (overlay on your own photo).
- Configure IMG_W, IMG_H, HFOV, VFOV, and your ROI definitions.
"""


import math, os, cv2, numpy as np, pandas as pd
import matplotlib.pyplot as plt

# =====================
# ===== USER INPUT =====
# =====================
MODE = "image"  # "blank" or "image"
IMAGE_PATH = r"C:\Users\davis\OneDrive\Desktop\WRO 2025\programas\Camara configuration\nwimages\zoneg4.jpg"

 # Example: '/mnt/data/your_image.jpg' when MODE == "image"

# Camera / Frame parameters (must match the image you use)
IMG_W, IMG_H = 320, 240           # width x height in pixels
HFOV_DEG, VFOV_DEG = 78.0, 48.0  # horizontal / vertical FOV in degrees

# Angle ROIs: (v_min, v_max, h_min, h_max) in degrees (relative to image center)
angle_rois = {
    #"A": (-3, 24, 18,  39),
    #"B": ( -3, 24, -22,  18),
    #"C": (-3, 15,  10,  36),
    #"D": (  -3,  15,-35, 0),
    #"E": (  -3,  15,-17, 17),
    #"F": ( 0, 15 , 0,  35),
    "G": (  -3,  15,-27, 27),
    #"H": (  0,  24,  -10,  39),
    #"I": (  0,  24,  -10,   20),
    #"J": (0, 15,  -36,  -10),

}

# ==============================
# ===== Core math utilities =====
# ==============================
def intrinsics_from_fov(img_w:int, img_h:int, hfov_deg:float, vfov_deg:float):
    hfov = math.radians(hfov_deg)
    vfov = math.radians(vfov_deg)
    fx = (img_w / 2.0) / math.tan(hfov / 2.0)
    fy = (img_h / 2.0) / math.tan(vfov / 2.0)
    cx = (img_w - 1) / 2.0
    cy = (img_h - 1) / 2.0
    return fx, fy, cx, cy

def angle_to_px(az_deg:float, el_deg:float, img_w:int, img_h:int, hfov_deg:float, vfov_deg:float):
    fx, fy, cx, cy = intrinsics_from_fov(img_w, img_h, hfov_deg, vfov_deg)
    az = math.radians(az_deg)
    el = math.radians(el_deg)
    u = cx + fx * math.tan(az)
    v = cy - fy * math.tan(el)  # minus: +elevation is up (lower v)
    return u, v

def clip_angle_range(vmin, vmax, hmin, hmax, hfov_deg, vfov_deg):
    vhalf = vfov_deg / 2.0
    hhalf = hfov_deg / 2.0
    vmin, vmax = (vmin, vmax) if vmin <= vmax else (vmax, vmin)
    hmin, hmax = (hmin, hmax) if hmin <= hmax else (hmax, hmin)
    vmin_c = max(-vhalf, min(vhalf, vmin))
    vmax_c = max(-vhalf, min(vhalf, vmax))
    hmin_c = max(-hhalf, min(hhalf, hmin))
    hmax_c = max(-hhalf, min(hhalf, hmax))
    return vmin_c, vmax_c, hmin_c, hmax_c

def angle_roi_to_px_roi(angle_box, img_w:int, img_h:int, hfov_deg:float, vfov_deg:float):
    vmin, vmax, hmin, hmax = angle_box
    vmin, vmax, hmin, hmax = clip_angle_range(vmin, vmax, hmin, hmax, hfov_deg, vfov_deg)

    # Horizontal edges → u
    uL, _ = angle_to_px(hmin, 0.0, img_w, img_h, hfov_deg, vfov_deg)
    uR, _ = angle_to_px(hmax, 0.0, img_w, img_h, hfov_deg, vfov_deg)
    # Vertical edges → v
    _, vT = angle_to_px(0.0, vmax, img_w, img_h, hfov_deg, vfov_deg)  # top edge (max elevation)
    _, vB = angle_to_px(0.0, vmin, img_w, img_h, hfov_deg, vfov_deg)  # bottom edge (min elevation)

    x = int(math.floor(min(uL, uR)))
    y = int(math.floor(min(vT, vB)))
    w = int(math.ceil(max(uL, uR))) - x
    h = int(math.ceil(max(vT, vB))) - y

    # Clip to image bounds
    if x < 0:
        w += x
        x = 0
    if y < 0:
        h += y
        y = 0
    if x + w > img_w:
        w = max(0, img_w - x)
    if y + h > img_h:
        h = max(0, img_h - y)
    return (x, y, w, h)

# ===============================
# ===== Convert & draw ROIs =====
# ===============================
# Convert all angle ROIs to pixel rectangles
px_rows = []
px_rois = {}
for name, abox in angle_rois.items():
    px = angle_roi_to_px_roi(abox, IMG_W, IMG_H, HFOV_DEG, VFOV_DEG)
    px_rois[name] = px
    px_rows.append({"ROI": name, "Angles (vmin,vmax,hmin,hmax) [deg]": abox, "Pixels (x,y,w,h)": px})

df_px = pd.DataFrame(px_rows).sort_values("ROI").reset_index(drop=True)
print("\nAngle ROIs → Pixel ROIs")
print(df_px)

# Prepare base canvas
if MODE == "image":
    if IMAGE_PATH is None or not os.path.exists(IMAGE_PATH):
        raise FileNotFoundError("MODE is 'image' but IMAGE_PATH is not set or file does not exist.")
    base_bgr = cv2.imread(IMAGE_PATH, cv2.IMREAD_COLOR)
    if base_bgr is None:
        raise ValueError("Failed to load image at IMAGE_PATH.")
    # If the loaded image size differs from IMG_WxIMG_H, resize to match parameters
    if base_bgr.shape[1] != IMG_W or base_bgr.shape[0] != IMG_H:
        base_bgr = cv2.resize(base_bgr, (IMG_W, IMG_H), interpolation=cv2.INTER_AREA)
else:
    base_bgr = np.ones((IMG_H, IMG_W, 3), dtype=np.uint8) * 255  # white blank

# Draw center reference lines
cx, cy = IMG_W // 2, IMG_H // 2
cv2.line(base_bgr, (cx, 0), (cx, IMG_H), (0, 0, 255), 1)   # vertical red
cv2.line(base_bgr, (0, cy), (IMG_W, cy), (0, 0, 255), 1)   # horizontal red

# Palette and drawing
palette = [
    (255, 0, 0), (0, 128, 255), (0, 200, 0), (200, 0, 200),
    (255, 165, 0), (0, 0, 0), (128, 0, 128), (128, 128, 0),
    (0, 128, 128), (100, 100, 255)
]
for i, (name, (x, y, w, h)) in enumerate(px_rois.items()):
    color = palette[i % len(palette)]
    cv2.rectangle(base_bgr, (x, y), (x + w, y + h), color, 2)
    tx = max(0, min(IMG_W - 20, x))
    ty = max(12, y - 5)
    cv2.putText(base_bgr, name, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

# Show preview
plt.imshow(cv2.cvtColor(base_bgr, cv2.COLOR_BGR2RGB))
title = f"ROIs ({len(px_rois)}) on {'image' if MODE=='image' else 'blank'} canvas @ {IMG_W}x{IMG_H}, FOV {HFOV_DEG}°×{VFOV_DEG}°"
plt.title(title)
plt.axis("off")
plt.show()

