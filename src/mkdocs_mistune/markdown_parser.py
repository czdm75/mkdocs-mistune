from typing import Dict, Tuple

import mistune
from mistune.directives import Admonition, FencedDirective

__all__ = ["MISTUNE_PLUGINS", "MarkdownParser"]

MISTUNE_PLUGINS = [
    # inline plugins
    "strikethrough",
    "url",
    "abbr",
    "superscript",
    "subscript",
    # block plugins
    "task_lists",
    "footnotes",
    "table",
    FencedDirective([Admonition()]),
]


class MarkdownParser:
    def __init__(self, plugins=None, output="html"):
        if output == "html":
            self.renderer = mistune.HTMLRenderer(escape=False)
        elif output == "ast":
            self.renderer = None
        else:
            raise Exception("unknown output format")

        self.plugins = MISTUNE_PLUGINS.copy() if plugins is None else plugins
        self.markdown = mistune.create_markdown(
            renderer=self.renderer, plugins=self.plugins
        )

    def parse(self, markdown: str) -> str:
        return self.markdown(markdown)
