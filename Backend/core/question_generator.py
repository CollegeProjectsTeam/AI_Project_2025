import json
import re


class QuestionGenerator:
    def render_question(self, template_text: str, instance: dict) -> str:
        if "instance" in instance and isinstance(instance["instance"], str):
            instance_str = "\n" + instance["instance"].rstrip("\n") + "\n"
        else:
            instance_str = self._pretty_instance(instance)

        text = template_text
        text = text.replace("{problem_name}", instance.get("problem_name", ""))
        text = text.replace("{instance}", instance_str)

        text = re.sub(r"\n\}\n\s*,\s*(?=\w)", "\n}\n", text)
        text = re.sub(r"\n\]\n\s*,\s*(?=\w)", "\n]\n", text)

        return text

    def _pretty_instance(self, instance: dict) -> str:
        lines = ["{"]

        for k, v in instance.items():
            if k == "board" and isinstance(v, list):
                lines.append('  "board": [')
                for row in v:
                    if isinstance(row, list):
                        lines.append(f"    {row},")
                    else:
                        lines.append(f"    {json.dumps(row)},")
                if lines[-1].endswith(","):
                    lines[-1] = lines[-1][:-1]
                lines.append("  ],")
            else:
                lines.append(f'  "{k}": {json.dumps(v)},')

        if lines[-1].endswith(","):
            lines[-1] = lines[-1][:-1]
        lines.append("}")

        return "\n" + "\n".join(lines) + "\n"
