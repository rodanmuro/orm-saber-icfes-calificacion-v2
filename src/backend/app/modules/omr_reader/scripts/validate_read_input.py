from __future__ import annotations

import argparse
import sys

from app.modules.omr_reader.errors import OMRReadInputError
from app.modules.omr_reader.loader import load_local_read_input


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate local read input (image + template metadata)"
    )
    parser.add_argument("--image", required=True, help="Path to filled template photo")
    parser.add_argument("--metadata", required=True, help="Path to template metadata JSON")
    args = parser.parse_args()

    try:
        context = load_local_read_input(image_path=args.image, metadata_path=args.metadata)
    except OMRReadInputError as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)

    print("[OK] Local read input is valid")
    print(f"  Image: {context.image_path}")
    print(f"  Metadata: {context.metadata_path}")
    print(f"  Template: {context.metadata['template_id']} {context.metadata['version']}")
    print(f"  Bubbles: {len(context.metadata['bubbles'])}")


if __name__ == "__main__":
    main()
