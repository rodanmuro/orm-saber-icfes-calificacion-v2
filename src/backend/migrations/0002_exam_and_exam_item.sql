-- ACT_0034: exam and exam_item tables

CREATE TABLE IF NOT EXISTS exam (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    exam_code VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_exam_teacher_code UNIQUE (teacher_id, exam_code),
    CONSTRAINT fk_exam_teacher FOREIGN KEY (teacher_id) REFERENCES teacher(id)
);

CREATE TABLE IF NOT EXISTS exam_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    order_position INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_exam_item_pair UNIQUE (exam_id, item_id),
    CONSTRAINT uq_exam_item_order UNIQUE (exam_id, order_position),
    CONSTRAINT fk_exam_item_exam FOREIGN KEY (exam_id) REFERENCES exam(id),
    CONSTRAINT fk_exam_item_item FOREIGN KEY (item_id) REFERENCES item(id)
);

CREATE INDEX IF NOT EXISTS ix_exam_teacher_id ON exam(teacher_id);
CREATE INDEX IF NOT EXISTS ix_exam_exam_code ON exam(exam_code);
CREATE INDEX IF NOT EXISTS ix_exam_item_exam_id ON exam_item(exam_id);
CREATE INDEX IF NOT EXISTS ix_exam_item_item_id ON exam_item(item_id);
CREATE INDEX IF NOT EXISTS ix_exam_item_order_position ON exam_item(order_position);

