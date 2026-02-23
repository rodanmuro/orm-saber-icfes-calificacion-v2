from __future__ import annotations

from app.modules.template_generator.contracts import ArucoConfig, BlockGeometry, MarkerPlacement


def build_aruco_layout(printable_area: BlockGeometry, aruco: ArucoConfig) -> list[MarkerPlacement]:
    half_size = aruco.marker_size_mm / 2.0
    inset = aruco.corner_inset_mm

    top_y = printable_area.y_mm + inset + aruco.corner_offsets_mm.top_left.y_mm + half_size
    bottom_y = (
        printable_area.y_mm
        + printable_area.height_mm
        - inset
        - aruco.corner_offsets_mm.bottom_left.y_mm
        - half_size
    )
    left_x = printable_area.x_mm + inset + aruco.corner_offsets_mm.top_left.x_mm + half_size
    right_x = (
        printable_area.x_mm
        + printable_area.width_mm
        - inset
        - aruco.corner_offsets_mm.top_right.x_mm
        - half_size
    )

    bottom_right_x = (
        printable_area.x_mm
        + printable_area.width_mm
        - inset
        - aruco.corner_offsets_mm.bottom_right.x_mm
        - half_size
    )
    top_right_y = printable_area.y_mm + inset + aruco.corner_offsets_mm.top_right.y_mm + half_size
    bottom_left_x = printable_area.x_mm + inset + aruco.corner_offsets_mm.bottom_left.x_mm + half_size
    bottom_right_y = (
        printable_area.y_mm
        + printable_area.height_mm
        - inset
        - aruco.corner_offsets_mm.bottom_right.y_mm
        - half_size
    )

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
            center_y_mm=top_right_y,
            size_mm=aruco.marker_size_mm,
        ),
        MarkerPlacement(
            marker_id=aruco.ids[2],
            corner="bottom_left",
            center_x_mm=bottom_left_x,
            center_y_mm=bottom_y,
            size_mm=aruco.marker_size_mm,
        ),
        MarkerPlacement(
            marker_id=aruco.ids[3],
            corner="bottom_right",
            center_x_mm=bottom_right_x,
            center_y_mm=bottom_right_y,
            size_mm=aruco.marker_size_mm,
        ),
    ]
