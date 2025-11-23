import re

from mistune import BlockParser, BlockState

from mkdocs_mistune.mistune_plugins.frontmatter import (
    JSON_FRONTMATTER_PATTERN,
    TOML_FRONTMATTER_PATTERN,
    YAML_FRONTMATTER_PATTERN,
    parse_block_json_frontmatter,
    parse_block_toml_frontmatter,
    parse_block_yaml_frontmatter,
)

YAML_LITERAL = """---
title: Test
author: John
---
"""

TOML_LITERAL = """+++
title = "Test"
author = "John"
+++
"""

JSON_LITERAL = """{
    "title": "Test",
    "author": "John"
}
"""

FRONTMATTER_CONTENT = {"title": "Test", "author": "John"}
FRONTMATTER_TOKEN = {"type": "frontmatter", "attrs": {"content": FRONTMATTER_CONTENT}}


class TestParseFrontmatter:
    def test_yaml_frontmatter_basic(self):
        match = re.match(YAML_FRONTMATTER_PATTERN, YAML_LITERAL)
        state = BlockState()
        assert match is not None
        assert parse_block_yaml_frontmatter(BlockParser(), match, state) == len(YAML_LITERAL) + 1
        assert state.tokens == [FRONTMATTER_TOKEN]

    def test_toml_frontmatter_basic(self):
        match = re.match(TOML_FRONTMATTER_PATTERN, TOML_LITERAL)
        state = BlockState()
        assert match is not None
        assert parse_block_toml_frontmatter(BlockParser(), match, state) == len(TOML_LITERAL) + 1
        assert state.tokens == [FRONTMATTER_TOKEN]

    def test_json_frontmatter_basic(self):
        match = re.match(JSON_FRONTMATTER_PATTERN, JSON_LITERAL)
        state = BlockState()
        assert match is not None
        assert parse_block_json_frontmatter(BlockParser(), match, state) == len(JSON_LITERAL) + 1
        assert state.tokens == [FRONTMATTER_TOKEN]
