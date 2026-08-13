# overlay_utils.py
"""
Utility untuk manipulasi gambar dan Alpha Blending PNG transparan pada frame OpenCV.
"""
import cv2
import numpy as np


def overlay_transparent(background, overlay, x, y, size=None):
    """
    Menempelkan gambar PNG transparan di atas background frame OpenCV.
    """
    if size is not None:
        overlay = cv2.resize(overlay, size)

    bg_h, bg_w, _ = background.shape
    ol_h, ol_w, ol_c = overlay.shape

    # Jika gambar tidak memiliki Alpha Channel (bukan PNG transparan)
    if ol_c < 4:
        background[y:y+ol_h, x:x+ol_w] = overlay
        return background

    # Ekstrak RGB dan Alpha Mask
    overlay_img = overlay[:, :, :3]
    alpha_mask = overlay[:, :, 3] / 255.0

    # Penanganan batas koordinat agar tidak crash/out-of-bounds
    if x >= bg_w or y >= bg_h or x + ol_w <= 0 or y + ol_h <= 0:
        return background

    x1, x2 = max(0, x), min(bg_w, x + ol_w)
    y1, y2 = max(0, y), min(bg_h, y + ol_h)

    ol_x1, ol_x2 = max(0, -x), min(ol_w, bg_w - x)
    ol_y1, ol_y2 = max(0, -y), min(ol_h, bg_h - y)

    alpha = alpha_mask[ol_y1:ol_y2, ol_x1:ol_x2, np.newaxis]

    # Formula Alpha Blending Matematika
    background[y1:y2, x1:x2] = (
        alpha * overlay_img[ol_y1:ol_y2, ol_x1:ol_x2] +
        (1 - alpha) * background[y1:y2, x1:x2]
    )

    return background