from __future__ import annotations

from app.modules.omr_reader.contracts import BubbleReadResult
from app.modules.omr_reader.auxiliary_blocks import read_auxiliary_blocks


def test_read_auxiliary_blocks_single_choice_and_single_per_column(monkeypatch) -> None:
    metadata = {
        "auxiliary_blocks": [
            {
                "block_id": "document_type",
                "title": "DOCUMENTO",
                "block_type": "omr",
                "x_mm": 10,
                "y_mm": 10,
                "width_mm": 30,
                "height_mm": 40,
                "omr_config": {
                    "rows": 3,
                    "cols": 1,
                    "bubble_diameter_mm": 4.0,
                    "spacing_x_mm": 8.0,
                    "spacing_y_mm": 8.0,
                    "selection_mode": "single_choice",
                    "row_labels": ["RC", "TI", "CC"],
                },
            },
            {
                "block_id": "student_identity_number",
                "title": "NUMERO DE IDENTIDAD",
                "block_type": "omr",
                "x_mm": 20,
                "y_mm": 20,
                "width_mm": 80,
                "height_mm": 60,
                "omr_config": {
                    "rows": 3,
                    "cols": 2,
                    "bubble_diameter_mm": 4.0,
                    "spacing_x_mm": 8.0,
                    "spacing_y_mm": 8.0,
                    "selection_mode": "single_per_column",
                    "row_labels": ["0", "1", "2"],
                },
            },
        ]
    }

    calls = {"count": 0}

    def fake_classify_bubbles(**kwargs):
        calls["count"] += 1
        bubbles = kwargs["metadata"]["bubbles"]
        block_id = bubbles[0]["group_id"]

        if block_id == "document_type":
            return [
                BubbleReadResult(
                    bubble_id=b["bubble_id"],
                    group_id=b["group_id"],
                    row=b["row"],
                    col=b["col"],
                    label=b["label"],
                    fill_ratio=0.72 if b["row"] == 1 else 0.02,
                    state="marcada" if b["row"] == 1 else "no_marcada",
                )
                for b in bubbles
            ]

        # col0 -> row2; col1 -> ambiguous (row0 and row1 both marked)
        out: list[BubbleReadResult] = []
        for b in bubbles:
            state = "no_marcada"
            ratio = 0.01
            if b["col"] == 0 and b["row"] == 2:
                state, ratio = "marcada", 0.7
            if b["col"] == 1 and b["row"] in {0, 1}:
                state, ratio = ("marcada", 0.6) if b["row"] == 1 else ("marcada", 0.55)
            out.append(
                BubbleReadResult(
                    bubble_id=b["bubble_id"],
                    group_id=b["group_id"],
                    row=b["row"],
                    col=b["col"],
                    label=b["label"],
                    fill_ratio=ratio,
                    state=state,
                )
            )
        return out

    monkeypatch.setattr(
        "app.modules.omr_reader.auxiliary_blocks.classify_bubbles",
        fake_classify_bubbles,
    )

    payload = read_auxiliary_blocks(
        aligned_image=None,  # not used due monkeypatch
        metadata=metadata,
        px_per_mm=10.0,
        marked_threshold=0.12,
        unmarked_threshold=0.1,
        robust_mode=True,
    )

    assert calls["count"] == 2
    assert payload["summary"]["total_blocks"] == 2
    assert payload["summary"]["manual_review_blocks"] == 1

    by_id = {item["block_id"]: item for item in payload["blocks"]}
    doc = by_id["document_type"]
    assert doc["selected"]["value"] == "TI"
    assert doc["selected"]["status"] == "ok"

    sid = by_id["student_identity_number"]
    assert sid["selection_mode"] == "single_per_column"
    assert sid["columns"][0]["value"] == "2"
    assert sid["columns"][0]["status"] == "ok"
    assert sid["columns"][1]["value"] == "1"
    assert sid["columns"][1]["status"] == "ambiguous"
    assert sid["manual_review_required"] is True
