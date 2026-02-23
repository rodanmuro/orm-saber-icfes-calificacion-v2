from __future__ import annotations

from app.modules.template_generator.contracts import ArucoConfig, MarkerPlacement, PageConfig


def build_aruco_layout(page: PageConfig, aruco: ArucoConfig) -> list[MarkerPlacement]:
    half_size = aruco.marker_size_mm / 2.0
    inset = aruco.corner_inset_mm

    top_y = inset + half_size
    bottom_y = page.height_mm - inset - half_size
    left_x = inset + half_size
    right_x = page.width_mm - inset - half_size

    return [
        MarkerPlacement(
            marker_id=aruco.ids[0],
            corner="top_left",
            center_x_mm=left_x,
            center_y_mm=top_y,
            size_mm=aruco.marker_size_mm,
        ),
        MarkerPlacement(
            marker_id=aruco.ids[1],
            corner="top_right",
            center_x_mm=right_x,
            center_y_mm=top_y,
            size_mm=aruco.marker_size_mm,
        ),
        MarkerPlacement(
            marker_id=aruco.ids[2],
            corner="bottom_left",
            center_x_mm=left_x,
            center_y_mm=bottom_y,
            size_mm=aruco.marker_size_mm,
        ),
        MarkerPlacement(
            marker_id=aruco.ids[3],
            corner="bottom_right",
            center_x_mm=right_x,
            center_y_mm=bottom_y,
            size_mm=aruco.marker_size_mm,
        ),
    ]
