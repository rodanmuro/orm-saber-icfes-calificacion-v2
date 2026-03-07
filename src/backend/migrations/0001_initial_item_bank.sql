-- Initial schema for ACT_0032 (teacher/student/item + curricular lite tables).

CREATE TABLE IF NOT EXISTS teacher (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_uuid VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(120) NOT NULL,
    last_name VARCHAR(120) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_uuid VARCHAR(64) NOT NULL UNIQUE,
    document_type VARCHAR(16) NOT NULL,
    document_number VARCHAR(32) NOT NULL,
    email VARCHAR(255) UNIQUE,
    first_name VARCHAR(120) NOT NULL,
    last_name VARCHAR(120) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_document UNIQUE (document_type, document_number)
);

CREATE TABLE IF NOT EXISTS standard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS competency (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    standard_id INTEGER NOT NULL,
    code VARCHAR(64) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_competency_standard_code UNIQUE (standard_id, code),
    CONSTRAINT fk_competency_standard FOREIGN KEY (standard_id) REFERENCES standard(id)
);

CREATE TABLE IF NOT EXISTS item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    statement TEXT NOT NULL,
    options JSON NOT NULL,
    correct_answer VARCHAR(1) NOT NULL,
    subject VARCHAR(120),
    difficulty VARCHAR(32),
    standard_id INTEGER,
    competency_id INTEGER,
    metadata_json JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_item_teacher FOREIGN KEY (teacher_id) REFERENCES teacher(id),
    CONSTRAINT fk_item_standard FOREIGN KEY (standard_id) REFERENCES standard(id),
    CONSTRAINT fk_item_competency FOREIGN KEY (competency_id) REFERENCES competency(id)
);

CREATE INDEX IF NOT EXISTS ix_teacher_external_uuid ON teacher(external_uuid);
CREATE INDEX IF NOT EXISTS ix_teacher_email ON teacher(email);
CREATE INDEX IF NOT EXISTS ix_student_document_type ON student(document_type);
CREATE INDEX IF NOT EXISTS ix_student_document_number ON student(document_number);
CREATE INDEX IF NOT EXISTS ix_standard_code ON standard(code);
CREATE INDEX IF NOT EXISTS ix_competency_standard_id ON competency(standard_id);
CREATE INDEX IF NOT EXISTS ix_competency_code ON competency(code);
CREATE INDEX IF NOT EXISTS ix_item_teacher_id ON item(teacher_id);
CREATE INDEX IF NOT EXISTS ix_item_standard_id ON item(standard_id);
CREATE INDEX IF NOT EXISTS ix_item_competency_id ON item(competency_id);
CREATE INDEX IF NOT EXISTS ix_item_subject ON item(subject);
CREATE INDEX IF NOT EXISTS ix_item_difficulty ON item(difficulty);

