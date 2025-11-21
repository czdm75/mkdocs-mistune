import json
import tomllib
from typing import TYPE_CHECKING, Any, Callable, Dict, Match, Optional

try:
    import yaml
except ImportError:
    yaml = None

if TYPE_CHECKING:
    from mistune.block_parser import BlockParser
    from mistune.core import BlockState
    from mistune.markdown import Markdown

YAML_FRONTMATTER_PATTERN = r"^---\s*\n(?P<yaml_frontmatter>[\s\S]*?)\n---\s*(?=\n|$)"
TOML_FRONTMATTER_PATTERN = r"^\+\+\+\s*\n(?P<toml_frontmatter>[\s\S]*?)\n\+\+\+\s*(?=\n|$)"
JSON_FRONTMATTER_PATTERN = r"^\{\s*\n(?P<json_frontmatter>[\s\S]*?)\n\}\s*(?=\n|$)"


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
        state.append_token({"type": "frontmatter", "raw": parsed_data})
        return m.end() + 1
    except error_type:
        return None


def parse_block_yaml_frontmatter(block: "BlockParser", m: Match[str], state: "BlockState") -> Optional[int]:
    if yaml is None:
        return None
    else:
        parser = (lambda t: yaml.load(t, Loader=yaml.CLoader),)
        return _parse_frontmatter(
            m,
            state,
            "yaml_frontmatter",
            parser,
            yaml.YAMLError,
        )


def parse_block_toml_frontmatter(block: "BlockParser", m: Match[str], state: "BlockState") -> Optional[int]:
    if tomllib is None:
        return None
    return _parse_frontmatter(m, state, "toml_frontmatter", tomllib.loads, tomllib.TOMLDecodeError)


def parse_block_json_frontmatter(block: "BlockParser", m: Match[str], state: "BlockState") -> Optional[int]:
    return _parse_frontmatter(
        m,
        state,
        "json_frontmatter",
        lambda t: json.loads(f"{{{t}}}"),
        json.JSONDecodeError,
    )


def frontmatter(md: "Markdown") -> None:
    md.block.register(
        "block_yaml_frontmatter", YAML_FRONTMATTER_PATTERN, parse_block_yaml_frontmatter, before="fenced_code"
    )
    md.block.register(
        "block_toml_frontmatter", TOML_FRONTMATTER_PATTERN, parse_block_toml_frontmatter, before="fenced_code"
    )
    md.block.register(
        "block_json_frontmatter", JSON_FRONTMATTER_PATTERN, parse_block_json_frontmatter, before="fenced_code"
    )
