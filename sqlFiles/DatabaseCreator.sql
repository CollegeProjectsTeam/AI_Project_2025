DROP TABLE IF EXISTS chapters CASCADE;
DROP TABLE IF EXISTS subchapters CASCADE;
DROP TABLE IF EXISTS question_templates CASCADE;
DROP TABLE IF EXISTS template_variables CASCADE;
DROP TABLE IF EXISTS problem_instances CASCADE;
DROP TABLE IF EXISTS questions_answers CASCADE;

CREATE TABLE chapters (
    id SERIAL PRIMARY KEY,
    chapter_number INT NOT NULL UNIQUE,
    chapter_name TEXT NOT NULL
);

CREATE TABLE subchapters (
    id SERIAL PRIMARY KEY,
    chapter_id INT NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    subchapter_number INT NOT NULL UNIQUE,
    subchapter_name TEXT NOT NULL
);

CREATE TABLE question_templates (
    id SERIAL PRIMARY KEY,
    chapter_id INT NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    subchapter_id INT NOT NULL REFERENCES subchapters(id) ON DELETE CASCADE,
    template_text TEXT NOT NULL,
    difficulty VARCHAR(20) CHECK (difficulty IN ('easy', 'medium', 'hard')) DEFAULT 'medium'
);

CREATE TABLE template_variables (
    id SERIAL PRIMARY KEY,
    template_id INT NOT NULL REFERENCES question_templates(id) ON DELETE CASCADE,
    variable_name TEXT NOT NULL,
    data_type VARCHAR(50) DEFAULT 'string'
);

CREATE TABLE problem_instances (
    id SERIAL PRIMARY KEY,
    template_id INT NOT NULL REFERENCES question_templates(id) ON DELETE CASCADE,
    instance_params JSONB NOT NULL
);

CREATE TABLE questions_answers (
    id SERIAL PRIMARY KEY,
    instance_id INT NOT NULL REFERENCES problem_instances(id) ON DELETE CASCADE,
    generated_question TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    variables_used JSONB
);