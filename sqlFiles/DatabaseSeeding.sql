DROP TABLE IF EXISTS questions_answers CASCADE;
DROP TABLE IF EXISTS problem_instances CASCADE;
DROP TABLE IF EXISTS template_variables CASCADE;
DROP TABLE IF EXISTS question_templates CASCADE;
DROP TABLE IF EXISTS subchapters CASCADE;
DROP TABLE IF EXISTS chapters CASCADE;

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

DO $$
DECLARE
    chapter_id INT;
    nqueens_sub_id INT;
    graph_sub_id INT;
    knights_sub_id INT;
    hanoi_sub_id INT;

    nqueens_template_id INT;
    graph_template_id INT;
    knights_template_id INT;
    hanoi_template_id INT;
    nash_combined_sub_id INT;
    nash_combined_template_id INT;
BEGIN
    INSERT INTO chapters (chapter_number, chapter_name)
    VALUES (1, 'Search Strategies')
    RETURNING id INTO chapter_id;

    INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
    VALUES (chapter_id, 1, 'N-Queens') RETURNING id INTO nqueens_sub_id;

    INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
    VALUES (chapter_id, 2, 'Graph Coloring') RETURNING id INTO graph_sub_id;

    INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
    VALUES (chapter_id, 3, 'Knights Tour') RETURNING id INTO knights_sub_id;

    INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
    VALUES (chapter_id, 4, 'Generalized Hanoi') RETURNING id INTO hanoi_sub_id;

    INSERT INTO question_templates (chapter_id, subchapter_id, template_text, difficulty)
    VALUES (chapter_id, nqueens_sub_id, 
            'Pentru problema {problem_name} cu instanta {instance}, care este cea mai potrivita strategie predata la curs pentru a o rezolva?',
            'medium') RETURNING id INTO nqueens_template_id;

    INSERT INTO question_templates (chapter_id, subchapter_id, template_text, difficulty)
    VALUES (chapter_id, graph_sub_id, 
            'Pentru problema {problem_name} cu instanta {instance}, care este cea mai potrivita strategie predata la curs pentru a o rezolva?',
            'medium') RETURNING id INTO graph_template_id;

    INSERT INTO question_templates (chapter_id, subchapter_id, template_text, difficulty)
    VALUES (chapter_id, knights_sub_id, 
            'Pentru problema {problem_name} cu instanta {instance}, care este cea mai potrivita strategie predata la curs pentru a o rezolva?',
            'medium') RETURNING id INTO knights_template_id;

    INSERT INTO question_templates (chapter_id, subchapter_id, template_text, difficulty)
    VALUES (chapter_id, hanoi_sub_id, 
            'Pentru problema {problem_name} cu instanta {instance}, care este cea mai potrivita strategie predata la curs pentru a o rezolva?',
            'medium') RETURNING id INTO hanoi_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES (nqueens_template_id, 'problem_name', 'string'),
           (nqueens_template_id, 'instance', 'JSON'),
           (graph_template_id, 'problem_name', 'string'),
           (graph_template_id, 'instance', 'JSON'),
           (knights_template_id, 'problem_name', 'string'),
           (knights_template_id, 'instance', 'JSON'),
           (hanoi_template_id, 'problem_name', 'string'),
           (hanoi_template_id, 'instance', 'JSON');

INSERT INTO problem_instances (template_id, instance_params)
VALUES (
     nqueens_template_id,
    '{
      "problem_name": "N-Queens",
      "board_size": 4,
      "queen_number_on_board": 2,
      "board": [
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
      ]
    }'::jsonb
);

    ------------------------------------------------------
    -- CHAPTER 2 – Game Theory (Nash)
    ------------------------------------------------------
    INSERT INTO chapters (chapter_number, chapter_name)
    VALUES (2, 'Game Theory')
    RETURNING id INTO chapter_id2;

    INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
    VALUES
        (chapter_id2, 1, 'Nash Equilibrium (Pure)'),
        (chapter_id2, 2, 'Nash Equilibrium (Mixed)')
    RETURNING id INTO nash_pure_sub_id, nash_mixed_sub_id;

    ------------------------------------------------------
    -- Templates pentru Nash Pure
    ------------------------------------------------------
    INSERT INTO question_templates (chapter_id, subchapter_id, template_text, difficulty)
    VALUES (
        chapter_id2,
        nash_pure_sub_id,
        'Pentru jocul următor, exista echilibru Nash pur? Dacă da, care este acesta? Instanță: {instance}',
        'medium'
    ) RETURNING id INTO nash_pure_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES
        (nash_pure_template_id, 'instance', 'JSON');

    ------------------------------------------------------
    -- Templates pentru Nash Mixed
    ------------------------------------------------------
    INSERT INTO question_templates (chapter_id, subchapter_id, template_text, difficulty)
    VALUES (
        chapter_id2,
        nash_mixed_sub_id,
        'Pentru jocul următor, determinați echilibrul Nash în strategii mixte. Instanță: {instance}',
        'hard'
    ) RETURNING id INTO nash_mixed_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES
        (nash_mixed_template_id, 'instance', 'JSON');

END $$;