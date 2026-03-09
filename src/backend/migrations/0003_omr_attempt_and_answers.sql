-- ACT_0038: persistence for OMR attempts and detailed answers

CREATE TABLE IF NOT EXISTS omr_attempt (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER,
    exam_id INTEGER,
    exam_code_detected VARCHAR(64),
    status VARCHAR(32) NOT NULL,
    score_percent REAL,
    total_questions INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    incorrect_count INTEGER DEFAULT 0,
    blank_count INTEGER DEFAULT 0,
    ambiguous_count INTEGER DEFAULT 0,
    manual_review_required BOOLEAN DEFAULT 0,
    uploaded_image_path TEXT,
    trace_json_path TEXT,
    ratios_csv_path TEXT,
    auxiliary_ratios_csv_path TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_omr_attempt_teacher FOREIGN KEY (teacher_id) REFERENCES teacher(id),
    CONSTRAINT fk_omr_attempt_exam FOREIGN KEY (exam_id) REFERENCES exam(id)
);

CREATE TABLE IF NOT EXISTS omr_attempt_answer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    question_number INTEGER NOT NULL,
    item_id INTEGER,
    correct_answer VARCHAR(8),
    marked_answer VARCHAR(8),
    status VARCHAR(32) NOT NULL,
    marked_options_json JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_omr_attempt_answer_attempt FOREIGN KEY (attempt_id) REFERENCES omr_attempt(id)
);

CREATE INDEX IF NOT EXISTS ix_omr_attempt_teacher_id ON omr_attempt(teacher_id);
CREATE INDEX IF NOT EXISTS ix_omr_attempt_exam_id ON omr_attempt(exam_id);
CREATE INDEX IF NOT EXISTS ix_omr_attempt_exam_code_detected ON omr_attempt(exam_code_detected);
CREATE INDEX IF NOT EXISTS ix_omr_attempt_status ON omr_attempt(status);
CREATE INDEX IF NOT EXISTS ix_omr_attempt_answer_attempt_id ON omr_attempt_answer(attempt_id);
CREATE INDEX IF NOT EXISTS ix_omr_attempt_answer_question_number ON omr_attempt_answer(question_number);
CREATE INDEX IF NOT EXISTS ix_omr_attempt_answer_item_id ON omr_attempt_answer(item_id);
CREATE INDEX IF NOT EXISTS ix_omr_attempt_answer_status ON omr_attempt_answer(status);

