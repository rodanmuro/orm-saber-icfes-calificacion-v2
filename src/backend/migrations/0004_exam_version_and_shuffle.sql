-- ACT_0035: exam version publication with reproducible shuffle

CREATE TABLE IF NOT EXISTS exam_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    version_code VARCHAR(64) NOT NULL,
    seed_shuffle INTEGER NOT NULL,
    shuffle_questions BOOLEAN NOT NULL DEFAULT 1,
    shuffle_options BOOLEAN NOT NULL DEFAULT 1,
    answer_key_json JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_exam_version_code UNIQUE (exam_id, version_code),
    CONSTRAINT fk_exam_version_exam FOREIGN KEY (exam_id) REFERENCES exam(id)
);

CREATE TABLE IF NOT EXISTS exam_version_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_version_id INTEGER NOT NULL,
    source_exam_item_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    question_number INTEGER NOT NULL,
    option_map_json JSON NOT NULL,
    correct_answer_original VARCHAR(1) NOT NULL,
    correct_answer_mapped VARCHAR(1) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_exam_version_item_qnum UNIQUE (exam_version_id, question_number),
    CONSTRAINT uq_exam_version_item_source UNIQUE (exam_version_id, source_exam_item_id),
    CONSTRAINT fk_exam_version_item_version FOREIGN KEY (exam_version_id) REFERENCES exam_version(id),
    CONSTRAINT fk_exam_version_item_exam_item FOREIGN KEY (source_exam_item_id) REFERENCES exam_item(id),
    CONSTRAINT fk_exam_version_item_item FOREIGN KEY (item_id) REFERENCES item(id)
);

CREATE INDEX IF NOT EXISTS ix_exam_version_exam_id ON exam_version(exam_id);
CREATE INDEX IF NOT EXISTS ix_exam_version_version_code ON exam_version(version_code);
CREATE INDEX IF NOT EXISTS ix_exam_version_item_version_id ON exam_version_item(exam_version_id);
CREATE INDEX IF NOT EXISTS ix_exam_version_item_item_id ON exam_version_item(item_id);
CREATE INDEX IF NOT EXISTS ix_exam_version_item_qnum ON exam_version_item(question_number);
