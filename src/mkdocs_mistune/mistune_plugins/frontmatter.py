YAML_FRONTMATTER_PATTERN = r"^---\s*\n(?P<yaml_frontmatter>[\s\S]*?)\n---\s*(?=\n|$)"
TOML_FRONTMATTER_PATTERN = r"^+++s*\n(?P<toml_frontmatter>[\s\S]*?)\n+++s*(?=\n|$)"
JSON_FRONTMATTER_PATTERN = r"^\{\s*\n(?P<json_frontmatter>[\s\S]*?)\n\}\s*(?=\n|$)"

import functools
from typing import Callable


def parse_frontmatter(regex_group: str, load_func: Callable):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                assert kwargs["state"].pos == 1
                text = kwargs["m"].group("yaml_frontmatter")
                frontmatter = load_func(text)
                kwargs["state"].env["frontmatter"] = frontmatter
                return kwargs["m"].end() + 1
            except:
                return

        return wrapper

    return decorator


def parse_yaml(text):
    import yaml

    return yaml.load(text, Loader=yaml.CLoader)


def parse_toml(text):
    pass


def parse_json(text):
    import json

    return json.loads(f"{{{text}}}")
