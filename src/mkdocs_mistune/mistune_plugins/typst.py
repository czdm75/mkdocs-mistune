from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mistune.markdown import Markdown

    from mistune import BaseRenderer


from mistune.plugins import math


def render_math(math: str) -> str:
    import typst as t

    input = "\n".join(
        [
            "#set page(width: auto, height: auto, margin: 0pt, fill: none)",
            '#show math.equation: set text(top-edge: "bounds", bottom-edge: "bounds")',
            math,
        ]
    )

    return t.compile(input.encode("utf-8"), format="svg").decode("utf-8")


def render_block_math(renderer: "BaseRenderer", text: str) -> str:
    return "\n".join(['<div class="math">', render_math(f"$ {text} $"), "</div>"])


def render_inline_math(renderer: "BaseRenderer", text: str) -> str:
    return "".join(['<span class="math">', render_math(f"${text}$"), "</span>"])


def typst(md: "Markdown") -> None:
    """A mistune plugin use same syntax parser as math plugin, but render with typst.
    :param md: Markdown instance
    """
    md.block.register(
        "block_math", math.BLOCK_MATH_PATTERN, math.parse_block_math, before="list"
    )
    md.inline.register(
        "inline_math", math.INLINE_MATH_PATTERN, math.parse_inline_math, before="link"
    )
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("block_math", render_block_math)
        md.renderer.register("inline_math", render_inline_math)
