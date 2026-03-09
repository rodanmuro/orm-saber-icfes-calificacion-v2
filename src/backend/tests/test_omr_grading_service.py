from app.modules.omr_scoring.service import build_answer_key_from_exam_items, grade_omr_questions


class _FakeItem:
    def __init__(self, correct_answer: str) -> None:
        self.correct_answer = correct_answer


class _FakeExamItem:
    def __init__(self, item_id: int, order_position: int, correct_answer: str) -> None:
        self.item_id = item_id
        self.order_position = order_position
        self.item = _FakeItem(correct_answer=correct_answer)


def test_grade_omr_questions_summary() -> None:
    exam_items = [
        _FakeExamItem(item_id=101, order_position=1, correct_answer="A"),
        _FakeExamItem(item_id=102, order_position=2, correct_answer="B"),
        _FakeExamItem(item_id=103, order_position=3, correct_answer="C"),
    ]
    answer_key = build_answer_key_from_exam_items(exam_items)
    omr_questions = [
        {"question_number": 1, "marked_options": ["A"]},
        {"question_number": 2, "marked_options": []},
        {"question_number": 3, "marked_options": ["A", "C"]},
    ]

    graded = grade_omr_questions(answer_key=answer_key, omr_questions=omr_questions)
    assert graded["summary"]["total_questions"] == 3
    assert graded["summary"]["correct"] == 1
    assert graded["summary"]["blank"] == 1
    assert graded["summary"]["ambiguous"] == 1
    assert graded["summary"]["incorrect"] == 0
    assert graded["summary"]["score_percent"] == 33.33

