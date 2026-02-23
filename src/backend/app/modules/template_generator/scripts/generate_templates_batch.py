from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.modules.template_generator.metadata_validation import validate_metadata_structure
from app.modules.template_generator.pipeline import generate_template_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate template artifacts for multiple configs and validate metadata"
    )
    parser.add_argument(
        "--configs",
        nargs="+",
        required=True,
        help="List of config files (JSON/YAML)",
    )
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first error",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    has_errors = False

    for config in args.configs:
        print(f"[START] {config}")
        try:
            pdf_path, json_path = generate_template_artifacts(
                config_path=config,
                output_dir=output_dir,
            )
            payload = json.loads(Path(json_path).read_text(encoding="utf-8"))
            issues = validate_metadata_structure(payload)
            if issues:
                has_errors = True
                print(f"[ERROR] {config} metadata validation failed")
                for issue in issues:
                    print(f"  - {issue}")
                if args.fail_fast:
                    break
            else:
                print(f"[OK] {config}")
                print(f"  PDF: {pdf_path}")
                print(f"  JSON: {json_path}")
        except Exception as exc:  # noqa: BLE001
            has_errors = True
            print(f"[ERROR] {config}: {exc}")
            if args.fail_fast:
                break

    if has_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
