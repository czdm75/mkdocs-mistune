from typing import TYPE_CHECKING, Any, Dict, Match

from mistune.directives._base import BaseDirective, DirectivePlugin

if TYPE_CHECKING:
    from mistune.block_parser import BlockParser
    from mistune.core import BlockState
    from mistune.markdown import Markdown
    from mistune.renderers.html import HTMLRenderer

__all__ = ["Graph"]

_SUPPORTED_LANGUAGES = ["mermaid", "graphviz"]


def render_block_graph(renderer: "HTMLRenderer", text: str, type: str) -> str:
    return "\n".join([f'<pre class="{type}">', text, "</pre>"])


class Graph(DirectivePlugin):
    NAME = "graph"

    def parse(self, block: "BlockParser", m: Match[str], state: "BlockState") -> Dict[str, Any]:
        return {"type": "block_graph_preview", "raw": m, "attrs": {"type": "mermaid"}}

    def __call__(self, directive: "BaseDirective", md: "Markdown") -> None:
        directive.register(self.NAME, self.parse)
        if md.renderer and md.renderer.NAME == "html":
            md.renderer.register("block_mermaid", render_block_graph)
