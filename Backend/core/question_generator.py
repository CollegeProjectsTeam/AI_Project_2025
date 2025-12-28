import json

class QuestionGenerator:
    def render_question(self, template_text: str, instance: dict) -> str:
        if "instance" in instance and isinstance(instance["instance"], str):
            instance_str = "\n" + instance["instance"].rstrip("\n") + "\n"
        else:
            instance_str = "{\n"
            for k, v in instance.items():
                if k == "board":
                    instance_str += f'  "{k}": [\n'
                    for row in v:
                        instance_str += f"    {row},\n"
                    instance_str += "  ]\n"
                else:
                    instance_str += f'  "{k}": {json.dumps(v)},\n'
            instance_str += "}"

        text = template_text
        text = text.replace("{problem_name}", instance.get("problem_name", ""))
        text = text.replace("{instance}", instance_str)
        return text