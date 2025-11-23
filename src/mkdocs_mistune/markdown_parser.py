import mistune
from mistune.directives import Admonition, FencedDirective

from mkdocs_mistune.mistune_plugins import Frontmatter, Graph, Math

__all__ = ["MarkdownParser"]


def mistune_plugins():
    return [
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
        Math(engine="client"),
        Frontmatter(),
        FencedDirective([Admonition(), Graph()]),
    ]


class MarkdownParser:
    def __init__(self, plugins=None):
        if plugins is None:
            self.plugins = mistune_plugins()
        else:
            self.plugins = plugins

        self.markdown = mistune.create_markdown(plugins=self.plugins)

    def parse(self, markdown: str):
        return self.markdown.parse(markdown)

    def parse_and_render(self, markdown: str) -> str:
        return self.markdown(markdown)  # type: ignore
