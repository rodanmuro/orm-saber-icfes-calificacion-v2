from __future__ import annotations

import cv2
from PIL import Image
from reportlab.lib.utils import ImageReader


def build_aruco_image_reader(
    *,
    dictionary_name: str,
    marker_id: int,
    marker_pixels: int,
) -> ImageReader:
    if marker_pixels <= 0:
        raise ValueError("marker_pixels must be > 0")

    aruco_module = cv2.aruco
    if not hasattr(aruco_module, dictionary_name):
        raise ValueError(f"unsupported aruco dictionary '{dictionary_name}'")

    dictionary_code = getattr(aruco_module, dictionary_name)
    dictionary = aruco_module.getPredefinedDictionary(dictionary_code)
    marker_img = aruco_module.generateImageMarker(dictionary, marker_id, marker_pixels)
    marker_img_pil = Image.fromarray(marker_img)

    return ImageReader(marker_img_pil)
