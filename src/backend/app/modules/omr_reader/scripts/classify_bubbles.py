from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.modules.omr_reader.alignment import align_image_to_template
from app.modules.omr_reader.bubble_classifier import classify_bubbles
from app.modules.omr_reader.errors import OMRReadInputError
from app.modules.omr_reader.loader import load_local_read_input
from app.modules.omr_reader.result_builder import build_omr_read_result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Classify bubble states from a template photo"
    )
    parser.add_argument("--image", required=True, help="Path to input photo")
    parser.add_argument("--metadata", required=True, help="Path to template metadata JSON")
    parser.add_argument("--output-json", required=True, help="Path to save bubble metrics JSON")
    parser.add_argument("--px-per-mm", type=float, default=10.0)
    parser.add_argument("--marked-threshold", type=float, default=0.33)
    parser.add_argument("--unmarked-threshold", type=float, default=0.18)
    args = parser.parse_args()

    try:
        context = load_local_read_input(image_path=args.image, metadata_path=args.metadata)
        aligned = align_image_to_template(
            image=context.image,
            metadata=context.metadata,
            px_per_mm=args.px_per_mm,
        )
        bubbles = classify_bubbles(
            aligned_image=aligned.aligned_image,
            metadata=context.metadata,
            px_per_mm=args.px_per_mm,
            marked_threshold=args.marked_threshold,
            unmarked_threshold=args.unmarked_threshold,
        )
    except OMRReadInputError as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)

    payload = build_omr_read_result(metadata=context.metadata, bubble_results=bubbles)
    payload["thresholds"] = {
        "marked": args.marked_threshold,
        "unmarked": args.unmarked_threshold,
    }
    payload["bubbles"] = [item.model_dump() for item in bubbles]

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    marked = sum(1 for item in bubbles if item.state == "marcada")
    unmarked = sum(1 for item in bubbles if item.state == "no_marcada")
    ambiguous = sum(1 for item in bubbles if item.state == "ambigua")

    print("[OK] Bubble classification completed")
    print(f"  Output: {output_path}")
    print(f"  Marked: {marked}")
    print(f"  Unmarked: {unmarked}")
    print(f"  Ambiguous: {ambiguous}")


if __name__ == "__main__":
    main()
