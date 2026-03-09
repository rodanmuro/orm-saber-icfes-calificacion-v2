from app.modules.omr_scoring.persistence import persist_omr_attempt


class _DummySession:
    def __init__(self) -> None:
        self.objects = []
        self._attempt_id = 0

    def add(self, obj):
        if obj.__class__.__name__ == 'OmrAttempt':
            self._attempt_id += 1
            obj.id = self._attempt_id
        self.objects.append(obj)

    def flush(self):
        return None

    def commit(self):
        return None

    def refresh(self, obj):
        return obj


def test_persist_omr_attempt_read_only() -> None:
    db = _DummySession()
    result_payload = {
        'questions': [
            {'question_number': 1, 'marked_options': ['A']},
            {'question_number': 2, 'marked_options': []},
            {'question_number': 3, 'marked_options': ['A', 'B']},
        ],
        'diagnostics': {
            'manual_review_required': True,
            'uploaded_image_path': '/tmp/test.jpg',
        },
    }

    attempt = persist_omr_attempt(
        db=db,
        result_payload=result_payload,
        teacher_id=None,
        exam_id=None,
        exam_code_detected='1234',
        grading_block=None,
    )

    assert attempt.id == 1
    assert attempt.status == 'read_only'
    assert attempt.total_questions == 3
    assert attempt.blank_count == 1
    assert attempt.ambiguous_count == 1
