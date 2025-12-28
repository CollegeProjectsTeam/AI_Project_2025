def q_insert_instance():
    return """
    INSERT INTO problem_instances (template_id, instance_params)
    VALUES (%s, %s) RETURNING id;
    """

def q_insert_qa():
    return """
    INSERT INTO questions_answers (instance_id, generated_question, correct_answer, variables_used)
    VALUES (%s, %s, %s, %s) RETURNING id;
    """
