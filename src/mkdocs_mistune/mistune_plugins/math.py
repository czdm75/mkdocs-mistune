from typing import TYPE_CHECKING, Literal, Match, Optional

from mistune.plugins import Plugin

if TYPE_CHECKING:
    from mistune.block_parser import BlockParser
    from mistune.core import ST, BaseRenderer, BlockState, InlineState
    from mistune.inline_parser import InlineParser
    from mistune.markdown import Markdown

from mistune.plugins.math import BLOCK_MATH_PATTERN, INLINE_MATH_PATTERN

MathEngine = Literal["typst", "mathjax", "katex", "frontmatter", "client"]
RenderMode = Literal["inline", "block"]

__all__ = ["MathPlugin"]


def _render_math_typst(mode: RenderMode, text: str) -> str:
    import typst as t

    match mode:
        case "inline":
            raw = f"${text}$"
        case "block":
            raw = f"$ {text} $"
        case _:
            raise ValueError("invalid render mode: " + mode)

    input = "\n".join(
        [
            "#set page(width: auto, height: auto, margin: 0pt, fill: none)",
            '#show math.equation: set text(top-edge: "bounds", bottom-edge: "bounds")',
            raw,
        ]
    )

    return t.compile(input.encode("utf-8"), format="svg").decode("utf-8")


def _render_math_mathjax(text: str) -> str:
    # TODO: implement multiple formats
    raise NotImplementedError()


def _render_math_katex(text: str) -> str:
    # TODO: implement
    raise NotImplementedError()


def render_math(mode: RenderMode, engine: MathEngine, text: str) -> str:
    match mode:
        case "inline":
            left, right = '<span class="math_inline">', "</span>"
        case "block":
            left, right = '<div class="math_block">', "</div>"
        case _:
            raise ValueError("invalid token type: " + mode)

    match engine:
        case "typst":
            content = _render_math_typst(mode, text)
        case "client":
            content = text
        case _:
            raise NotImplementedError()

    return "".join([left, content, right])


class MathPlugin(Plugin):
    def __init__(self, engine: MathEngine = "client"):
        if engine not in ("typst", "mathjax", "katex", "frontmatter", "client"):
            raise ValueError("invalid config math engine: " + engine)
        self.engine = engine

    def __call__(self, md: "Markdown") -> None:
        md.inline.register("inline_math", INLINE_MATH_PATTERN, self.parse_inline_math, before="link")
        md.block.register("block_math", BLOCK_MATH_PATTERN, self.parse_block_math, before="list")
        md.block.insert_rule(md.block.block_quote_rules, "block_math", before="list")
        md.block.insert_rule(md.block.list_rules, "block_math", before="list")

        if md.renderer and md.renderer.NAME == "html":
            for engine in ("typst", "mathjax", "katex", "math"):
                for mode in ("inline", "block"):
                    md.renderer.register(
                        name=f"{mode}_math_{engine}", method=lambda renderer, text: render_math(mode, engine, text)
                    )

    def _get_math_engine(self, frontmatter_engine: Optional[MathEngine]) -> Optional[MathEngine]:
        if frontmatter_engine in ("typst", "mathjax", "katex", "client"):
            return frontmatter_engine
        elif frontmatter_engine is not None:
            raise ValueError("invalid math_engine in frontmatter: " + frontmatter_engine)
        elif self.engine in ("typst", "mathjax", "katex", "client"):
            return self.engine
        else:
            # plugin engine is frontmatter but frontmatter engine is None, disabled
            return

    def _parse_math(self, mode: RenderMode, m: Match[str], state: "ST") -> Optional[int]:
        """
        Convert math blocks to {block | inline}_{typst|mathjax|katex|math}
        """
        frontmatter_engine = state.env.get("frontmatter", {}).get("math_engine")
        engine = self._get_math_engine(frontmatter_engine)
        if not engine:
            return

        token_type = f"{mode}_math_{engine}"
        text = m.group("math_text")
        state.append_token({"type": token_type, "raw": text})
        return m.end() + 1

    def parse_block_math(self, block: "BlockParser", m: Match[str], state: "BlockState") -> Optional[int]:
        return self._parse_math("block", m, state)

    def parse_inline_math(self, inline: "InlineParser", m: Match[str], state: "InlineState") -> Optional[int]:
        return self._parse_math("inline", m, state)
