-- Database creator -- Folosit ptr a crea baza de date si tabelele acesteia
-- Schema: chapters -> subchapters -> question_templates -> template_variables

BEGIN;

DROP TABLE IF EXISTS template_variables CASCADE;
DROP TABLE IF EXISTS question_templates CASCADE;
DROP TABLE IF EXISTS subchapters CASCADE;
DROP TABLE IF EXISTS chapters CASCADE;

CREATE TABLE chapters (
    id SERIAL PRIMARY KEY,
    chapter_number INT NOT NULL UNIQUE,
    chapter_name TEXT NOT NULL,
    CONSTRAINT chk_chapter_name_not_empty
        CHECK (length(trim(chapter_name)) > 0)
);

CREATE TABLE subchapters (
    id SERIAL PRIMARY KEY,
    chapter_id INT NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    subchapter_number INT NOT NULL,
    subchapter_name TEXT NOT NULL,
    UNIQUE (chapter_id, subchapter_number),
    CONSTRAINT chk_subchapter_name_not_empty
        CHECK (length(trim(subchapter_name)) > 0)
);

CREATE TABLE question_templates (
    id SERIAL PRIMARY KEY,
    subchapter_id INT NOT NULL REFERENCES subchapters(id) ON DELETE CASCADE,
    template_text TEXT NOT NULL,
    difficulty VARCHAR(20)
        CHECK (difficulty IN ('easy', 'medium', 'hard'))
        DEFAULT 'medium',
    CONSTRAINT chk_template_text_not_empty
        CHECK (length(trim(template_text)) > 0)
);

CREATE TABLE template_variables (
    id SERIAL PRIMARY KEY,
    template_id INT NOT NULL REFERENCES question_templates(id) ON DELETE CASCADE,
    variable_name TEXT NOT NULL,
    data_type VARCHAR(50) DEFAULT 'string',
    CONSTRAINT chk_variable_name_not_empty
        CHECK (length(trim(variable_name)) > 0),
    CONSTRAINT uq_template_variables_template_var
        UNIQUE (template_id, variable_name)
);


CREATE INDEX IF NOT EXISTS idx_subchapters_chapter_id
    ON subchapters(chapter_id);

CREATE INDEX IF NOT EXISTS idx_question_templates_subchapter
    ON question_templates(subchapter_id);

CREATE INDEX IF NOT EXISTS idx_question_templates_difficulty
    ON question_templates(difficulty);

CREATE INDEX IF NOT EXISTS idx_question_templates_sub_diff
    ON question_templates(subchapter_id, difficulty);

CREATE INDEX IF NOT EXISTS idx_template_variables_template_id
    ON template_variables(template_id);

COMMIT;