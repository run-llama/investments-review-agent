from jinja2 import Template


def get_prompt() -> Template:
    return Template(
        "Your task is to analyze the trends and performance of an investment portfolio "
        "(and possibly come up with improvement suggestions) based on these tables:\n\n{{tables}}\n\n"
    )
