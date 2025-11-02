INSERT INTO chapters (chapter_number, chapter_name) VALUES (1, 'Search Strategies');

INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
VALUES (1, 1, 'N-Queens Problem');

INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
VALUES (1, 2, 'Graph Coloring');

INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
VALUES (1, 3, 'Knights Tour');

INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
VALUES (1, 4, 'Generalized Hanoi');

INSERT INTO question_templates (chapter_id, subchapter_id, template_text, difficulty)
VALUES (
    1, 
    1, 
    'Pentru problema {SearchStrategyProblem} cu instanta {SSP_Instance}, care dintre strategiile predate la curs este cea mai potrivita in a rezolva cerinta?',
    'medium'
);

-- X = problem
INSERT INTO template_variables (template_id, variable_name, description)
VALUES (1, 'SearchStrategyProblem', 'Problem type: n-queens, knight tour, graph coloring');

-- Y = instance
INSERT INTO template_variables (template_id, variable_name, description, data_type)
VALUES (1, 'SSP_Instance', 'Specific instance of the problem', 'json');

-- X = n-queens
INSERT INTO variable_values (template_variable_id, value_json)
VALUES (1, '"n-queens"');

-- Y = instance (8-queens example)
INSERT INTO variable_values (template_variable_id, value_json)
VALUES (2, '{"n": 4, "board": "empty"}');
