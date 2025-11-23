from mkdocs.plugins import BasePlugin

from mkdocs_mistune.markdown_parser import MarkdownParser


class MistunePlugin(BasePlugin):
    config_scheme = ()

    def on_page_markdown(self, markdown: str, /, *, page, config, files) -> str | None:
        page.meta["original_markdown"] = markdown
        return "<!-- MISTUNE RENDER PLACEHOLDER -->"

    def on_page_content(self, html: str, /, *, page, config, files) -> str | None:
        return MarkdownParser().parse_and_render(page.meta["original_markdown"])  # type: ignore
