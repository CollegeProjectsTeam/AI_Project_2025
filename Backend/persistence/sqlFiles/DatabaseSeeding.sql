-- Database Seeding -- Script de populare al bazei de date
-- Seed data pentru capitole/subcapitole/templates/variables

DO $$
DECLARE
    -- Search Strategies
    chapter_id1 INT;
    nqueens_sub_id INT;
    graph_sub_id INT;
    knights_sub_id INT;
    hanoi_sub_id INT;

    nqueens_template_id INT;
    graph_template_id INT;
    knights_template_id INT;
    hanoi_template_id INT;

    -- Game Theory
    chapter_id2 INT;

    -- Nash (unificat)
    nash_sub_id INT;
    nash_pure_template_id INT;
    nash_mixed_template_id INT;
    nash_combined_template_id INT;

    -- MinMax
    minimax_sub_id INT;
    minimax_template_id INT;

    -- CSP
    chapter_id3 INT;
    csp_sub_id INT;
    csp_template_id INT;
BEGIN
    ------------------------------------------------------
    -- CHAPTER 1 – Search Strategies
    ------------------------------------------------------
    INSERT INTO chapters (chapter_number, chapter_name)
    VALUES (1, 'Search Strategies')
    RETURNING id INTO chapter_id1;

    INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
    VALUES (chapter_id1, 1, 'N-Queens')
    RETURNING id INTO nqueens_sub_id;

    INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
    VALUES (chapter_id1, 2, 'Graph Coloring')
    RETURNING id INTO graph_sub_id;

    INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
    VALUES (chapter_id1, 3, 'Knights Tour')
    RETURNING id INTO knights_sub_id;

    INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
    VALUES (chapter_id1, 4, 'Generalized Hanoi')
    RETURNING id INTO hanoi_sub_id;

    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        nqueens_sub_id,
        'Pentru problema {problem_name} cu instanta {instance}, care este cea mai potrivita strategie predata la curs pentru a o rezolva?',
        'medium'
    ) RETURNING id INTO nqueens_template_id;

    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        graph_sub_id,
        'Pentru problema {problem_name} cu instanta {instance}, care este cea mai potrivita strategie predata la curs pentru a o rezolva?',
        'medium'
    ) RETURNING id INTO graph_template_id;

    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        knights_sub_id,
        'Pentru problema {problem_name} cu instanta {instance}, care este cea mai potrivita strategie predata la curs pentru a o rezolva?',
        'medium'
    ) RETURNING id INTO knights_template_id;

    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        hanoi_sub_id,
        'Pentru problema {problem_name} cu instanta {instance}, care este cea mai potrivita strategie predata la curs pentru a o rezolva?',
        'medium'
    ) RETURNING id INTO hanoi_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES
        (nqueens_template_id, 'problem_name', 'string'),
        (nqueens_template_id, 'instance', 'JSON'),
        (graph_template_id, 'problem_name', 'string'),
        (graph_template_id, 'instance', 'JSON'),
        (knights_template_id, 'problem_name', 'string'),
        (knights_template_id, 'instance', 'JSON'),
        (hanoi_template_id, 'problem_name', 'string'),
        (hanoi_template_id, 'instance', 'JSON');

    ------------------------------------------------------
    -- CHAPTER 2 – Game Theory
    ------------------------------------------------------
    INSERT INTO chapters (chapter_number, chapter_name)
    VALUES (2, 'Game Theory')
    RETURNING id INTO chapter_id2;

    ------------------------------------------------------
    -- Subchapter 1 – Nash Equilibrium (unificat)
    ------------------------------------------------------
    INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
    VALUES (chapter_id2, 1, 'Nash Equilibrium')
    RETURNING id INTO nash_sub_id;

    -- Nash easy (pure)
    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        nash_sub_id,
        'Pentru jocul urmator, exista echilibru Nash pur? Daca da, scrieti echilibrul (doar raspunsul final). Instanta: {instance}',
        'easy'
    ) RETURNING id INTO nash_pure_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES (nash_pure_template_id, 'instance', 'JSON');

    -- Nash medium (mixed)
    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        nash_sub_id,
        'Pentru jocul urmator, determinati echilibrul Nash in strategii mixte (doar raspunsul final). Instanta: {instance}',
        'medium'
    ) RETURNING id INTO nash_mixed_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES (nash_mixed_template_id, 'instance', 'JSON');

    -- Nash hard (combined)
    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        nash_sub_id,
        'Pentru jocul urmator, indicati toate echilibrele Nash existente (pure si/sau mixte), daca exista (doar raspunsul final). Instanta: {instance}',
        'hard'
    ) RETURNING id INTO nash_combined_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES (nash_combined_template_id, 'instance', 'JSON');

    ------------------------------------------------------
    -- Subchapter 2 – MinMax (Alpha-Beta)
    ------------------------------------------------------
    INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
    VALUES (chapter_id2, 2, 'MinMax (Alpha-Beta)')
    RETURNING id INTO minimax_sub_id;

    -- MinMax EASY (2 variante) - doar valoarea radacinii
    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        minimax_sub_id,
        'Aplicati MinMax cu optimizarea Alpha-Beta si determinati valoarea din radacina (doar raspunsul final). Instanta: {instance}',
        'easy'
    ) RETURNING id INTO minimax_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES (minimax_template_id, 'instance', 'JSON');

    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        minimax_sub_id,
        'Pentru arborele urmator, folositi Alpha-Beta si calculati valoarea nodului radacina (doar raspunsul final). Instanta: {instance}',
        'easy'
    ) RETURNING id INTO minimax_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES (minimax_template_id, 'instance', 'JSON');

    -- MinMax MEDIUM (2 variante) - valoare radacina + nr frunze evaluate
    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        minimax_sub_id,
        'Pentru arborele dat, determinati: (1) valoarea din radacina, (2) cate frunze sunt evaluate efectiv cu Alpha-Beta (doar raspunsul final). Instanta: {instance}',
        'medium'
    ) RETURNING id INTO minimax_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES (minimax_template_id, 'instance', 'JSON');

    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        minimax_sub_id,
        'Aplicati Alpha-Beta pe arbore si scrieti doar: valoarea radacinii si numarul de frunze evaluate. Instanta: {instance}',
        'medium'
    ) RETURNING id INTO minimax_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES (minimax_template_id, 'instance', 'JSON');

    -- MinMax HARD (2 variante) - tot final, fara "demonstrati/justificati"
    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        minimax_sub_id,
        'Pentru arborele dat, determinati valoarea din radacina si numarul de frunze evaluate cu Alpha-Beta (doar raspunsul final). Instanta: {instance}',
        'hard'
    ) RETURNING id INTO minimax_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES (minimax_template_id, 'instance', 'JSON');

    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        minimax_sub_id,
        'Aplicati MinMax cu Alpha-Beta si raportati doar: valoarea radacinii + numarul de frunze evaluate. Instanta: {instance}',
        'hard'
    ) RETURNING id INTO minimax_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES (minimax_template_id, 'instance', 'JSON');

    ------------------------------------------------------
    -- CHAPTER 3 – CSP (Backtracking)
    ------------------------------------------------------
    INSERT INTO chapters (chapter_number, chapter_name)
    VALUES (3, 'Constrain Satisfaction Problems')
    RETURNING id INTO chapter_id3;

    INSERT INTO subchapters (chapter_id, subchapter_number, subchapter_name)
    VALUES (chapter_id3, 1, 'Backtracking')
    RETURNING id INTO csp_sub_id;

    -- CSP EASY (2 variante) - doar solutia finala
    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        csp_sub_id,
        'Rezolvati CSP-ul folosind Backtracking cu optimizarile indicate si scrieti doar solutia finala.
Optiuni: {options}
Cerinta: {ask_for}
Instanta:
{instance}',
        'easy'
    ) RETURNING id INTO csp_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES
        (csp_template_id, 'options', 'JSON'),
        (csp_template_id, 'ask_for', 'string'),
        (csp_template_id, 'instance', 'JSON');

    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        csp_sub_id,
        'Folosind Backtracking si optimizarile mentionate, gasiti o atribuire valida.
Optiuni: {options}
Cerinta: {ask_for}
Instanta:
{instance}',
        'easy'
    ) RETURNING id INTO csp_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES
        (csp_template_id, 'options', 'JSON'),
        (csp_template_id, 'ask_for', 'string'),
        (csp_template_id, 'instance', 'JSON');

    -- CSP MEDIUM (2 variante) - doar solutia finala
    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        csp_sub_id,
        'Date fiind variabilele, domeniile si constrangerile, rezolvati folosind Backtracking cu optimizarile mentionate si oferiti solutia.
Optiuni: {options}
Cerinta: {ask_for}
Instanta:
{instance}',
        'medium'
    ) RETURNING id INTO csp_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES
        (csp_template_id, 'options', 'JSON'),
        (csp_template_id, 'ask_for', 'string'),
        (csp_template_id, 'instance', 'JSON');

    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        csp_sub_id,
        'Aplicati Backtracking cu optimizarile specificate si introduceti raspunsul final. Luati in considerare posibilitatea lipsei unei solutii pentru exercitiul primit.
Optiuni: {options}
Cerinta: {ask_for}
Instanta:
{instance}',
        'medium'
    ) RETURNING id INTO csp_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES
        (csp_template_id, 'options', 'JSON'),
        (csp_template_id, 'ask_for', 'string'),
        (csp_template_id, 'instance', 'JSON');

    -- CSP HARD (2 variante) - doar solutia finala
    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        csp_sub_id,
        'Rezolvati CSP-ul folosind Backtracking si optimizarile indicate. Exista posibilitatea unui exercitiu fara solutie!
Optiuni: {options}
Cerinta: {ask_for}
Instanta:
{instance}',
        'hard'
    ) RETURNING id INTO csp_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES
        (csp_template_id, 'options', 'JSON'),
        (csp_template_id, 'ask_for', 'string'),
        (csp_template_id, 'instance', 'JSON');

    INSERT INTO question_templates (subchapter_id, template_text, difficulty)
    VALUES (
        csp_sub_id,
        'Avand variabilele, domeniile si constrangerile, aplicati Backtracking cu optimizarile mentionate si oferiti solutia gasita. A se lua in considerare ca exista posibilitatea unui exercitiu fara solutie.
Optiuni: {options}
Cerinta: {ask_for}
Instanta:
{instance}',
        'hard'
    ) RETURNING id INTO csp_template_id;

    INSERT INTO template_variables (template_id, variable_name, data_type)
    VALUES
        (csp_template_id, 'options', 'JSON'),
        (csp_template_id, 'ask_for', 'string'),
        (csp_template_id, 'instance', 'JSON');

END $$;
