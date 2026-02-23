from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from app.modules.omr_reader import (
    align_image_to_template,
    build_omr_read_result,
    classify_bubbles,
    load_local_read_input,
)
from app.modules.omr_reader.errors import OMRReadInputError


def _extract_answer_key(result_payload: dict[str, Any]) -> dict[int, list[str]]:
    key: dict[int, list[str]] = {}
    for question in result_payload.get("questions", []):
        qn = int(question["question_number"])
        marks = list(question.get("marked_options", []))
        key[qn] = sorted(marks)
    if not key:
        raise ValueError("key json does not contain questions")
    return key


def _rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    h, w = image.shape[:2]
    center = (w / 2.0, h / 2.0)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        image,
        matrix,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )


def _add_gaussian_noise(image: np.ndarray, sigma: float, rng: np.random.Generator) -> np.ndarray:
    if sigma <= 0:
        return image
    noise = rng.normal(loc=0.0, scale=sigma, size=image.shape).astype(np.float32)
    noisy = image.astype(np.float32) + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)


def _apply_variant(
    image: np.ndarray,
    *,
    angle_deg: float,
    blur_kernel: int,
    noise_sigma: float,
    alpha: float,
    beta: float,
    rng: np.random.Generator,
) -> np.ndarray:
    result = _rotate_image(image, angle_deg)
    if blur_kernel > 1:
        result = cv2.GaussianBlur(result, (blur_kernel, blur_kernel), 0)
    result = cv2.convertScaleAbs(result, alpha=alpha, beta=beta)
    result = _add_gaussian_noise(result, noise_sigma, rng)
    return result


def _build_html_report(report_payload: dict[str, Any]) -> str:
    rows_html: list[str] = []
    for item in report_payload["results"]:
        wrong_count = len(item.get("wrong_questions", []))
        rows_html.append(
            "<tr>"
            f"<td>{item['index']}</td>"
            f"<td>{item['file_name']}</td>"
            f"<td>{item['status']}</td>"
            f"<td>{item['accuracy']:.4f}</td>"
            f"<td>{'SI' if item['exact_match'] else 'NO'}</td>"
            f"<td>{wrong_count}</td>"
            f"<td>{item.get('error_reason', '-')}</td>"
            "</tr>"
        )

    summary = report_payload["summary"]
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Reporte cien_pruebas OMR</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f7fa; color: #1f2937; }}
    h1 {{ margin-bottom: 8px; }}
    .summary {{ background: #fff; border: 1px solid #d1d5db; padding: 12px; border-radius: 8px; margin-bottom: 16px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #d1d5db; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 8px; text-align: left; font-size: 13px; }}
    th {{ background: #111827; color: #fff; position: sticky; top: 0; }}
    tr:nth-child(even) {{ background: #f9fafb; }}
    .ok {{ color: #065f46; font-weight: 600; }}
    .bad {{ color: #991b1b; font-weight: 600; }}
  </style>
</head>
<body>
  <h1>Informe de pruebas OMR (100 variantes)</h1>
  <div class="summary">
    <div><strong>Generado:</strong> {report_payload['generated_at']}</div>
    <div><strong>Total:</strong> {summary['total_images']}</div>
    <div><strong>Exactas:</strong> <span class="ok">{summary['exact_matches']}</span></div>
    <div><strong>Con diferencias:</strong> <span class="bad">{summary['mismatch_images']}</span></div>
    <div><strong>Error de pipeline:</strong> <span class="bad">{summary['pipeline_errors']}</span></div>
    <div><strong>Exactitud promedio por pregunta:</strong> {summary['avg_accuracy']:.4f}</div>
    <div><strong>Exactitud minima por imagen:</strong> {summary['min_accuracy']:.4f}</div>
  </div>
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>Archivo</th>
        <th>Estado</th>
        <th>Exactitud</th>
        <th>Exacta</th>
        <th>Preguntas erradas</th>
        <th>Motivo</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows_html)}
    </tbody>
  </table>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera 100 variantes de una foto OMR y evalua precision contra una clave."
    )
    parser.add_argument("--base-image", required=True, help="Ruta de imagen base diligenciada")
    parser.add_argument("--metadata", required=True, help="Ruta metadata de plantilla")
    parser.add_argument(
        "--key-json",
        required=True,
        help="Ruta JSON con respuestas validadas (questions[*].marked_options)",
    )
    parser.add_argument(
        "--output-dir",
        default="data/input/diligenciadas/cien_pruebas",
        help="Carpeta de salida del experimento",
    )
    parser.add_argument("--num-variants", type=int, default=100)
    parser.add_argument("--seed", type=int, default=23022026)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    random.seed(args.seed)

    base_image_path = Path(args.base_image)
    metadata_path = Path(args.metadata)
    key_path = Path(args.key_json)
    output_dir = Path(args.output_dir)
    variants_dir = output_dir / "variantes"
    results_dir = output_dir / "resultados"
    reads_dir = results_dir / "lecturas_json"

    variants_dir.mkdir(parents=True, exist_ok=True)
    reads_dir.mkdir(parents=True, exist_ok=True)

    base_image = cv2.imread(str(base_image_path), cv2.IMREAD_COLOR)
    if base_image is None:
        raise ValueError(f"no se pudo cargar imagen base: {base_image_path}")

    key_payload = json.loads(key_path.read_text(encoding="utf-8"))
    answer_key = _extract_answer_key(key_payload)
    total_questions = len(answer_key)

    report_rows: list[dict[str, Any]] = []
    exact_matches = 0
    mismatches = 0
    pipeline_errors = 0
    accuracies: list[float] = []

    for i in range(1, args.num_variants + 1):
        angle = float(rng.uniform(-15.0, 15.0))
        blur_kernel = random.choice([1, 3, 5, 7])
        noise_sigma = float(rng.uniform(0.0, 20.0))
        alpha = float(rng.uniform(0.82, 1.18))
        beta = float(rng.uniform(-30.0, 30.0))
        jpeg_quality = int(rng.integers(55, 97))

        variant = _apply_variant(
            base_image,
            angle_deg=angle,
            blur_kernel=blur_kernel,
            noise_sigma=noise_sigma,
            alpha=alpha,
            beta=beta,
            rng=rng,
        )

        file_name = f"foto_var_{i:03d}.jpg"
        variant_path = variants_dir / file_name
        cv2.imwrite(
            str(variant_path),
            variant,
            [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality],
        )

        row: dict[str, Any] = {
            "index": i,
            "file_name": file_name,
            "augmentation": {
                "angle_deg": round(angle, 4),
                "blur_kernel": blur_kernel,
                "noise_sigma": round(noise_sigma, 4),
                "alpha": round(alpha, 4),
                "beta": round(beta, 4),
                "jpeg_quality": jpeg_quality,
            },
            "status": "",
            "accuracy": 0.0,
            "exact_match": False,
            "wrong_questions": [],
            "error_reason": None,
        }

        try:
            context = load_local_read_input(
                image_path=str(variant_path),
                metadata_path=str(metadata_path),
            )
            aligned = align_image_to_template(
                image=context.image,
                metadata=context.metadata,
                px_per_mm=10.0,
            )
            bubbles = classify_bubbles(
                aligned_image=aligned.aligned_image,
                metadata=context.metadata,
                px_per_mm=10.0,
                marked_threshold=0.33,
                unmarked_threshold=0.18,
            )
            result_payload = build_omr_read_result(
                metadata=context.metadata,
                bubble_results=bubbles,
            )

            read_json_path = reads_dir / f"foto_var_{i:03d}_resultado.json"
            read_json_path.write_text(
                json.dumps(result_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            wrong_questions: list[dict[str, Any]] = []
            predicted_map = {
                int(item["question_number"]): sorted(item.get("marked_options", []))
                for item in result_payload.get("questions", [])
            }
            for qn in sorted(answer_key.keys()):
                expected = answer_key[qn]
                predicted = predicted_map.get(qn, [])
                if expected != predicted:
                    wrong_questions.append(
                        {
                            "question_number": qn,
                            "expected": expected,
                            "predicted": predicted,
                        }
                    )

            correct = total_questions - len(wrong_questions)
            accuracy = correct / total_questions if total_questions else 0.0
            accuracies.append(accuracy)

            row["accuracy"] = round(accuracy, 6)
            row["wrong_questions"] = wrong_questions
            row["exact_match"] = len(wrong_questions) == 0
            if row["exact_match"]:
                row["status"] = "ok"
                exact_matches += 1
            else:
                row["status"] = "mismatch"
                row["error_reason"] = (
                    f"{len(wrong_questions)} preguntas difieren de la clave"
                )
                mismatches += 1

        except OMRReadInputError as exc:
            row["status"] = "pipeline_error"
            row["error_reason"] = str(exc)
            row["accuracy"] = 0.0
            accuracies.append(0.0)
            pipeline_errors += 1

        report_rows.append(row)

    summary = {
        "total_images": args.num_variants,
        "exact_matches": exact_matches,
        "mismatch_images": mismatches,
        "pipeline_errors": pipeline_errors,
        "avg_accuracy": float(sum(accuracies) / len(accuracies)) if accuracies else 0.0,
        "min_accuracy": float(min(accuracies)) if accuracies else 0.0,
    }

    report_payload = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "base_image": str(base_image_path),
        "metadata": str(metadata_path),
        "key_json": str(key_path),
        "num_variants": args.num_variants,
        "seed": args.seed,
        "summary": summary,
        "results": report_rows,
    }

    report_json_path = results_dir / "reporte_cien_pruebas.json"
    report_json_path.write_text(
        json.dumps(report_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    report_html_path = results_dir / "reporte_cien_pruebas.html"
    report_html_path.write_text(_build_html_report(report_payload), encoding="utf-8")

    print("[OK] Benchmark completado")
    print(f"  Variantes: {variants_dir}")
    print(f"  Lecturas: {reads_dir}")
    print(f"  Reporte JSON: {report_json_path}")
    print(f"  Reporte HTML: {report_html_path}")
    print(f"  Exactas: {summary['exact_matches']}/{summary['total_images']}")
    print(f"  Mismatch: {summary['mismatch_images']}")
    print(f"  Pipeline error: {summary['pipeline_errors']}")
    print(f"  Accuracy promedio: {summary['avg_accuracy']:.4f}")


if __name__ == "__main__":
    main()
