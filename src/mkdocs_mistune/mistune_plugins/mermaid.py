import re
from typing import TYPE_CHECKING, Any, Dict, List, Match, Optional

from mistune.directives._base import BaseDirective, DirectivePlugin
from mistune.util import escape as escape_text
from mistune.util import escape_url

if TYPE_CHECKING:
    from mistune.block_parser import BlockParser
    from mistune.core import BlockState
    from mistune.markdown import Markdown
    from mistune.renderers.html import HTMLRenderer


_num_re = re.compile(r"^\d+(?:\.\d*)?")
_allowed_aligns = ["top", "middle", "bottom", "left", "center", "right"]


def render_block_mermaid(
    self: "HTMLRenderer",
    src: str,
    **attrs: Any,
) -> str:
    return "\n".join(['<pre class="mermaid">', src, "</pre>"])


class Mermaid(DirectivePlugin):
    NAME = "mermaid"

    def parse(self, block: "BlockParser", m: Match[str], state: "BlockState") -> Dict[str, Any]:
        return {"type": "block_mermaid", "attrs": {"src": m}}

    def __call__(self, directive: "BaseDirective", md: "Markdown") -> None:
        directive.register(self.NAME, self.parse)
        if md.renderer and md.renderer.NAME == "html":
            md.renderer.register("block_mermaid", render_block_mermaid)
