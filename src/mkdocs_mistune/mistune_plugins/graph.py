from typing import TYPE_CHECKING, Any, Dict, Literal, Match

from mistune.directives._base import BaseDirective, DirectivePlugin

if TYPE_CHECKING:
    from mistune.block_parser import BlockParser
    from mistune.core import BlockState
    from mistune.markdown import Markdown
    from mistune.renderers.html import HTMLRenderer

__all__ = ["Graph"]

GraphSyntax = Literal["graphviz", "mermaid"]


def render_block_graph_client(renderer: "HTMLRenderer", text: str, type: str) -> str:
    return "\n".join([f'<pre class="{type}">', text, "</pre>"])


class Graph(DirectivePlugin):
    def __init__(self, mode="client"):
        self.mode = mode

    def parse_graphviz(self, block: "BlockParser", m: Match[str], state: "BlockState") -> Dict[str, Any]:
        return {"type": "block_graphviz", "raw": self.parse_content(m), "attrs": {"type": "graphviz"}}

    def parse_mermaid(self, block: "BlockParser", m: Match[str], state: "BlockState") -> Dict[str, Any]:
        return {"type": "block_mermaid", "raw": self.parse_content(m), "attrs": {"type": "mermaid"}}

    def __call__(self, directive: "BaseDirective", md: "Markdown") -> None:
        directive.register("graphviz", self.parse_graphviz)
        directive.register("mermaid", self.parse_mermaid)
        if md.renderer and md.renderer.NAME == "html" and self.mode == "client":
            md.renderer.register("block_mermaid", render_block_graph_client)
            md.renderer.register("block_graphviz", render_block_graph_client)
