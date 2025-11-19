from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin


class MistunePlugin(BasePlugin):
    config_scheme = (
        (
            "math_provider",
            config_options.Choice(("katex", "mathjax", "typst"), default="katex"),
        ),
        (
            "math_mode",
            config_options.Choice(("js", "pre-compile"), default="js"),
        ),
        (
            "math_enabled",
            config_options.Choice(
                ("enabled", "disabled", "frontmatter"), default="frontmatter"
            ),
        ),
        (
            "highlight_provider",
            config_options.Choice(("pygments", "highlight.js"), default="pygments"),
        ),
    )

    def on_config(self, config):
        self.mistune_plugins = MISTUNE_PLUGINS
        if self.config.math_enabled != "disabled":
            self.mistune_plugins.append("math")

        return config

    def on_page_markdown(self, markdown: str, /, *, page, config, files) -> str | None:
        return "<!-- MISTUNE RENDER PLACEHOLDER -->"

    def on_page_content(self, html: str, /, *, page, config, files) -> str | None:
        parser = MistuneParser(plugins=self.mistune_plugins)
        # take from page.file, check frontmatter and render
        page.file
        return
