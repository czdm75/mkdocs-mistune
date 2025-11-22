from multiprocessing import Value
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Literal, Match, Optional

from mistune import BaseRenderer
from mistune.plugins import Plugin

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

if TYPE_CHECKING:
    from mistune.block_parser import BlockParser
    from mistune.core import BlockState
    from mistune.markdown import Markdown

YAML_FRONTMATTER_PATTERN = r"^---\s*\n(?P<yaml_frontmatter>[\s\S]*?)\n---\s*(?=\n|$)"
TOML_FRONTMATTER_PATTERN = r"^\+\+\+\s*\n(?P<toml_frontmatter>[\s\S]*?)\n\+\+\+\s*(?=\n|$)"
JSON_FRONTMATTER_PATTERN = r"^\{\s*\n(?P<json_frontmatter>[\s\S]*?)\n\}\s*(?=\n|$)"

SyntaxType = Literal["yaml", "toml", "json"]


def _parse_frontmatter(
    m: Match[str],
    state: "BlockState",
    group_name: str,
    parser: Callable[[str], dict],
    error_type: type[Exception],
) -> Optional[int]:
    """Generic frontmatter parser."""
    if state.cursor != 0:
        return None
    text = m.group(group_name)
    try:
        parsed_data = parser(text)
        # Store in state.env so it can be accessed by other plugins or renderers
        state.env["frontmatter"] = parsed_data
        # Also store in token for rendering
        state.append_token({"type": "frontmatter", "attrs": {"content": parsed_data}})
        return m.end() + 1
    except error_type:
        return None


def parse_block_yaml_frontmatter(block: "BlockParser", m: Match[str], state: "BlockState") -> Optional[int]:
    if HAS_YAML:

        def parser(text: str) -> Dict[Any, Any]:
            return yaml.load(text, Loader=yaml.CLoader)  # type: ignore

        return _parse_frontmatter(
            m,
            state,
            "yaml_frontmatter",
            parser,
            yaml.YAMLError,  # type: ignore
        )
    else:
        raise ValueError("yaml is not correctly loaded")


def parse_block_toml_frontmatter(block: "BlockParser", m: Match[str], state: "BlockState") -> Optional[int]:
    import tomllib

    return _parse_frontmatter(m, state, "toml_frontmatter", tomllib.loads, tomllib.TOMLDecodeError)


def parse_block_json_frontmatter(block: "BlockParser", m: Match[str], state: "BlockState") -> Optional[int]:
    import json

    return _parse_frontmatter(
        m,
        state,
        "json_frontmatter",
        lambda t: json.loads(f"{{{t}}}"),
        json.JSONDecodeError,
    )


def debug_render_frontmatter(renderer: BaseRenderer, content: Dict[Any, Any]) -> str:
    import json

    return "\n".join(['<div class="frontmatter">', json.dumps(content), "</div>"])


def empty_render_frontmatter(renderer: BaseRenderer) -> str:
    return ""


class FrontMatterPlugin(Plugin):
    def __init__(self, syntax: Optional[List[SyntaxType]] = None, debug_render: bool = False):
        if syntax is None:
            self.syntax = ["yaml", "toml", "json"]
        else:
            self.syntax = []
            for s in syntax:
                if s in ("yaml", "toml", "json"):
                    self.syntax.append(s)
                else:
                    raise ValueError("Unknown frontmatter syntax: " + s)
        self.debug_render = debug_render

    def __call__(self, md: "Markdown") -> None:
        if "yaml" in self.syntax:
            md.block.register(
                "block_yaml_frontmatter", YAML_FRONTMATTER_PATTERN, parse_block_yaml_frontmatter, before="fenced_code"
            )
        if "toml" in self.syntax:
            md.block.register(
                "block_toml_frontmatter", TOML_FRONTMATTER_PATTERN, parse_block_toml_frontmatter, before="fenced_code"
            )
        if "json" in self.syntax:
            md.block.register(
                "block_json_frontmatter", JSON_FRONTMATTER_PATTERN, parse_block_json_frontmatter, before="fenced_code"
            )

        if md.renderer and md.renderer.NAME == "html":
            if self.debug_render:
                md.renderer.register("frontmatter", debug_render_frontmatter)
            else:
                md.renderer.register("frontmatter", empty_render_frontmatter)
