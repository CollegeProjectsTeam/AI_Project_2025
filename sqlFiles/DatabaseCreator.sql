-- ========================================
-- DROPPING TABLES WHEN CREATING THE DB
-- ========================================

DROP TABLE IF EXISTS chapters CASCADE;
DROP TABLE IF EXISTS subchapters CASCADE;
DROP TABLE IF EXISTS question_templates CASCADE;
DROP TABLE IF EXISTS questions_answers CASCADE;
DROP TABLE IF EXISTS template_variables CASCADE;
DROP TABLE IF EXISTS variable_values CASCADE;
DROP TABLE IF EXISTS problem_instances CASCADE;

-- ========================================
-- CHAPTERS
-- ========================================
CREATE TABLE chapters (
    id SERIAL PRIMARY KEY,
    chapter_number INT NOT NULL,
    chapter_name TEXT NOT NULL
);

-- ========================================
-- SUBCHAPTERS
-- ========================================
CREATE TABLE subchapters (
    id SERIAL PRIMARY KEY,
    chapter_id INT NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    subchapter_number INT NOT NULL,
    subchapter_name TEXT NOT NULL
);

-- ========================================
-- QUESTION TEMPLATES
-- ========================================
CREATE TABLE question_templates (
    id SERIAL PRIMARY KEY,
    chapter_id INT NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    subchapter_id INT NOT NULL REFERENCES subchapters(id) ON DELETE CASCADE,
    template_text TEXT NOT NULL,
	 difficulty VARCHAR(20) CHECK (difficulty IN ('easy', 'medium', 'hard')) DEFAULT 'medium'
);

-- ========================================
-- TEMPLATE VARIABLES (variable definitions per template)
-- ========================================
CREATE TABLE template_variables (
    id SERIAL PRIMARY KEY,
    template_id INT NOT NULL REFERENCES question_templates(id) ON DELETE CASCADE,
    variable_name TEXT NOT NULL,   -- e.g. 'problem', 'instance'
    description TEXT,
    data_type VARCHAR(50) DEFAULT 'string'  -- can be 'string', 'json', 'int', etc.
);

-- ========================================
-- VARIABLE VALUES (specific values for a variable, e.g., problem types)
-- ========================================
CREATE TABLE variable_values (
    id SERIAL PRIMARY KEY,
    template_variable_id INT NOT NULL REFERENCES template_variables(id) ON DELETE CASCADE,
    value_json JSONB NOT NULL       -- e.g., "n-queens", "graph coloring"
);

-- ========================================
-- PROBLEM INSTANCES (link specific instances to a problem)
-- ========================================
CREATE TABLE problem_instances (
    id SERIAL PRIMARY KEY,
    problem_value_id INT NOT NULL REFERENCES variable_values(id) ON DELETE CASCADE,
    instance_json JSONB NOT NULL    -- e.g., {"n": 8, "board": "empty"}
);

-- ========================================
-- GENERATED QUESTIONS & ANSWERS
-- ========================================
CREATE TABLE questions_answers (
    id SERIAL PRIMARY KEY,
    template_id INT NOT NULL REFERENCES question_templates(id) ON DELETE CASCADE,
    generated_question TEXT NOT NULL,  -- full text after variable substitution
    correct_answer TEXT NOT NULL,
    variables_used JSONB               -- which variable values were used in generation
);