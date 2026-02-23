from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2

from app.modules.omr_reader.alignment import align_image_to_template
from app.modules.omr_reader.errors import OMRReadInputError
from app.modules.omr_reader.loader import load_local_read_input


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Align a template photo using ArUco markers and homography"
    )
    parser.add_argument("--image", required=True, help="Path to input photo")
    parser.add_argument("--metadata", required=True, help="Path to template metadata JSON")
    parser.add_argument("--output-image", required=True, help="Path to save aligned image")
    parser.add_argument(
        "--px-per-mm",
        type=float,
        default=10.0,
        help="Pixel density for aligned output image",
    )
    args = parser.parse_args()

    try:
        context = load_local_read_input(image_path=args.image, metadata_path=args.metadata)
        aligned = align_image_to_template(
            image=context.image,
            metadata=context.metadata,
            px_per_mm=args.px_per_mm,
        )
    except OMRReadInputError as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)

    output_path = Path(args.output_image)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ok = cv2.imwrite(str(output_path), aligned.aligned_image)
    if not ok:
        print(f"[ERROR] could not write output image '{output_path}'")
        sys.exit(1)

    print("[OK] Photo aligned successfully")
    print(f"  Output: {output_path}")
    print(f"  Markers detected: {aligned.detected_marker_ids}")
    print(f"  Size: {aligned.output_width_px}x{aligned.output_height_px}")


if __name__ == "__main__":
    main()
