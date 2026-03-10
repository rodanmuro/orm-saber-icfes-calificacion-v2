from app.modules.exam_version.service import publish_exam_version


class _FakeItem:
    def __init__(self, item_id: int, correct_answer: str) -> None:
        self.id = item_id
        self.correct_answer = correct_answer


class _FakeExamItem:
    def __init__(self, row_id: int, order_position: int, item_id: int, correct_answer: str) -> None:
        self.id = row_id
        self.order_position = order_position
        self.item_id = item_id
        self.item = _FakeItem(item_id=item_id, correct_answer=correct_answer)


def test_publish_exam_version_is_reproducible() -> None:
    exam_items = [
        _FakeExamItem(row_id=1, order_position=1, item_id=101, correct_answer="A"),
        _FakeExamItem(row_id=2, order_position=2, item_id=102, correct_answer="B"),
        _FakeExamItem(row_id=3, order_position=3, item_id=103, correct_answer="C"),
    ]

    result_1 = publish_exam_version(
        exam_items=exam_items,
        seed_shuffle=12345,
        shuffle_questions=True,
        shuffle_options=True,
    )
    result_2 = publish_exam_version(
        exam_items=exam_items,
        seed_shuffle=12345,
        shuffle_questions=True,
        shuffle_options=True,
    )

    assert result_1.answer_key == result_2.answer_key
    assert [r.item_id for r in result_1.rows] == [r.item_id for r in result_2.rows]
    assert [r.option_map for r in result_1.rows] == [r.option_map for r in result_2.rows]


def test_publish_exam_version_without_option_shuffle() -> None:
    exam_items = [
        _FakeExamItem(row_id=1, order_position=1, item_id=101, correct_answer="D"),
    ]
    result = publish_exam_version(
        exam_items=exam_items,
        seed_shuffle=1,
        shuffle_questions=False,
        shuffle_options=False,
    )

    assert result.answer_key == {"1": "D"}
    assert result.rows[0].option_map == {"A": "A", "B": "B", "C": "C", "D": "D"}
    assert result.rows[0].correct_answer_mapped == "D"
