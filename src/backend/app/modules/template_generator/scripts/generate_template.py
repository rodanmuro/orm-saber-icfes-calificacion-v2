from __future__ import annotations

import argparse

from app.modules.template_generator.pipeline import generate_template_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate OMR template artifacts")
    parser.add_argument("--config", required=True, help="Path to template config JSON")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    args = parser.parse_args()

    pdf_path, json_path = generate_template_artifacts(
        config_path=args.config,
        output_dir=args.output_dir,
    )

    print(f"PDF: {pdf_path}")
    print(f"JSON: {json_path}")


if __name__ == "__main__":
    main()
