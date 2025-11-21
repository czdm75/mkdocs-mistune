import re
from unittest.mock import MagicMock, Mock, patch

import pytest
from mistune import Markdown

from mkdocs_mistune.mistune_plugins.math import (
    MathPlugin,
    _render_math_typst,
    render_math,
)


class TestRenderMathTypst:
    def test_inline_mode(self):
        result = _render_math_typst("inline", "x + y")
        assert isinstance(result, str)
        assert "<svg" in result
        assert "</svg>" in result

    def test_block_mode(self):
        result = _render_math_typst("block", "x + y = z")
        assert isinstance(result, str)
        assert "<svg" in result
        assert "</svg>" in result

    def test_invalid_mode(self):
        with pytest.raises(ValueError, match="invalid render mode"):
            _render_math_typst("invalid", "x + y")

    def test_complex_math_expression(self):
        result = _render_math_typst("inline", "sum_(i=1)^n i = (n(n+1))/2")
        assert isinstance(result, str)
        assert "<svg" in result


class TestRenderMath:
    def test_inline_client_mode(self):
        result = render_math("inline", "client", "x + y")
        assert result == '<span class="math_inline">x + y</span>'

    def test_block_client_mode(self):
        result = render_math("block", "client", "x + y = z")
        assert result == '<div class="math_block">x + y = z</div>'

    def test_inline_typst_mode(self):
        result = render_math("inline", "typst", "x + y")
        assert '<span class="math_inline">' in result
        assert "</span>" in result
        assert "<svg" in result

    def test_block_typst_mode(self):
        result = render_math("block", "typst", "x + y")
        assert '<div class="math_block">' in result
        assert "</div>" in result
        assert "<svg" in result

    def test_invalid_mode(self):
        with pytest.raises(ValueError, match="invalid token type"):
            render_math("invalid", "client", "x + y")

    def test_not_implemented_engine(self):
        with pytest.raises(NotImplementedError):
            render_math("inline", "mathjax", "x + y")

    def test_not_implemented_katex(self):
        with pytest.raises(NotImplementedError):
            render_math("inline", "katex", "x + y")


class TestMathPlugin:
    def test_initialization_valid_engines(self):
        for engine in ["typst", "mathjax", "katex", "frontmatter", "client"]:
            plugin = MathPlugin(engine=engine)
            assert plugin.engine == engine

    def test_initialization_invalid_engine(self):
        with pytest.raises(ValueError, match="invalid config math engine"):
            MathPlugin(engine="invalid")

    def test_default_engine(self):
        plugin = MathPlugin()
        assert plugin.engine == "client"

    def test_get_math_engine_frontmatter_priority(self):
        plugin = MathPlugin(engine="client")
        assert plugin._get_math_engine("typst") == "typst"
        assert plugin._get_math_engine("mathjax") == "mathjax"
        assert plugin._get_math_engine("katex") == "katex"
        assert plugin._get_math_engine("client") == "client"

    def test_get_math_engine_plugin_fallback(self):
        plugin = MathPlugin(engine="typst")
        assert plugin._get_math_engine(None) == "typst"

    def test_get_math_engine_invalid_frontmatter(self):
        plugin = MathPlugin(engine="client")
        with pytest.raises(ValueError, match="invalid math_engine in frontmatter"):
            plugin._get_math_engine("invalid")

    def test_get_math_engine_frontmatter_with_frontmatter_plugin(self):
        plugin = MathPlugin(engine="frontmatter")
        assert plugin._get_math_engine(None) is None

    def test_get_math_engine_frontmatter_overrides_when_plugin_is_frontmatter(self):
        plugin = MathPlugin(engine="frontmatter")
        assert plugin._get_math_engine("typst") == "typst"

    def test_parse_math_creates_correct_token(self):
        plugin = MathPlugin(engine="typst")
        match = Mock()
        match.group.return_value = "x + y"
        match.end.return_value = 10

        state = Mock()
        state.env = {"frontmatter": {}}
        state.append_token = Mock()

        result = plugin._parse_math("inline", match, state)

        assert result == 11
        state.append_token.assert_called_once_with({"type": "inline_math_typst", "raw": "x + y"})

    def test_parse_math_with_frontmatter_engine(self):
        plugin = MathPlugin(engine="client")
        match = Mock()
        match.group.return_value = "x + y"
        match.end.return_value = 10

        state = Mock()
        state.env = {"frontmatter": {"math_engine": "typst"}}
        state.append_token = Mock()

        result = plugin._parse_math("block", match, state)

        assert result == 11
        state.append_token.assert_called_once_with({"type": "block_math_typst", "raw": "x + y"})

    def test_parse_math_disabled_when_no_engine(self):
        plugin = MathPlugin(engine="frontmatter")
        match = Mock()
        state = Mock()
        state.env = {}

        result = plugin._parse_math("inline", match, state)

        assert result is None

    def test_parse_block_math(self):
        plugin = MathPlugin(engine="client")
        block = Mock()
        match = Mock()
        match.group.return_value = "x + y"
        match.end.return_value = 10

        state = Mock()
        state.env = {}
        state.append_token = Mock()

        result = plugin.parse_block_math(block, match, state)

        assert result == 11
        state.append_token.assert_called_once()

    def test_parse_inline_math(self):
        plugin = MathPlugin(engine="client")
        inline = Mock()
        match = Mock()
        match.group.return_value = "x + y"
        match.end.return_value = 10

        state = Mock()
        state.env = {}
        state.append_token = Mock()

        result = plugin.parse_inline_math(inline, match, state)

        assert result == 11
        state.append_token.assert_called_once()

    def test_call_registers_rules(self):
        plugin = MathPlugin(engine="client")
        md = Mock()
        md.inline = Mock()
        md.block = Mock()
        md.renderer = None

        md.inline.register = Mock()
        md.block.register = Mock()
        md.block.insert_rule = Mock()
        md.block.block_quote_rules = []
        md.block.list_rules = []

        plugin(md)

        md.inline.register.assert_called_once()
        md.block.register.assert_called_once()
        assert md.block.insert_rule.call_count == 2

    def test_call_registers_renderer_methods(self):
        plugin = MathPlugin(engine="client")
        md = Mock()
        md.inline = Mock()
        md.block = Mock()
        md.renderer = Mock()
        md.renderer.NAME = "html"
        md.renderer.register = Mock()

        md.inline.register = Mock()
        md.block.register = Mock()
        md.block.insert_rule = Mock()
        md.block.block_quote_rules = []
        md.block.list_rules = []

        plugin(md)

        assert md.renderer.register.call_count == 8


class TestIntegration:
    def test_inline_math_basic(self):
        md = Markdown(plugins=[MathPlugin(engine="client")])
        result = md("This is $x + y$ inline math")
        assert '<span class="math_inline">x + y</span>' in result

    def test_block_math_basic(self):
        md = Markdown(plugins=[MathPlugin(engine="client")])
        result = md("$$\nx + y = z\n$$")
        assert '<div class="math_block">x + y = z</div>' in result

    def test_multiple_inline_math(self):
        md = Markdown(plugins=[MathPlugin(engine="client")])
        result = md("Formulas: $a + b$ and $c + d$")
        assert result.count('<span class="math_inline">') == 2
        assert "a + b" in result
        assert "c + d" in result

    def test_mixed_inline_and_block_math(self):
        md = Markdown(plugins=[MathPlugin(engine="client")])
        text = "Inline $x$ and block:\n\n$$\ny = mx + b\n$$"
        result = md(text)
        assert '<span class="math_inline">x</span>' in result
        assert '<div class="math_block">y = mx + b</div>' in result

    def test_typst_engine_integration(self):
        md = Markdown(plugins=[MathPlugin(engine="typst")])
        result = md("Formula: $x + y$")
        assert '<span class="math_inline">' in result
        assert "<svg" in result

    def test_typst_block_engine_integration(self):
        md = Markdown(plugins=[MathPlugin(engine="typst")])
        result = md("$$\nx^2 + y^2 = r^2\n$$")
        assert '<div class="math_block">' in result
        assert "<svg" in result

    def test_math_with_text(self):
        md = Markdown(plugins=[MathPlugin(engine="client")])
        text = "The equation $E = mc^2$ is famous."
        result = md(text)
        assert '<span class="math_inline">E = mc^2</span>' in result
        assert "The equation" in result
        assert "is famous" in result

    def test_complex_block_math(self):
        md = Markdown(plugins=[MathPlugin(engine="client")])
        text = """
$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$
"""
        result = md(text)
        assert '<div class="math_block">' in result
        assert "\\int" in result

    def test_math_in_paragraph(self):
        md = Markdown(plugins=[MathPlugin(engine="client")])
        text = "First paragraph with $a + b$.\n\nSecond paragraph with $c - d$."
        result = md(text)
        assert result.count('<span class="math_inline">') == 2
        assert result.count("<p>") == 2

    def test_empty_plugin_with_client_engine(self):
        md = Markdown(plugins=[MathPlugin()])
        result = md("Math: $x + y$")
        assert '<span class="math_inline">x + y</span>' in result

    def test_frontmatter_engine_without_frontmatter(self):
        md = Markdown(plugins=[MathPlugin(engine="frontmatter")])
        result = md("Math: $x + y$")
        assert '<span class="math_inline">' not in result
        assert "$x + y$" in result

    def test_escaped_dollar_signs(self):
        md = Markdown(plugins=[MathPlugin(engine="client")])
        result = md("Price is \\$100")
        assert '<span class="math_inline">' not in result
        assert "100" in result

    def test_math_with_special_characters(self):
        md = Markdown(plugins=[MathPlugin(engine="client")])
        result = md("$\\alpha + \\beta = \\gamma$")
        assert '<span class="math_inline">\\alpha + \\beta = \\gamma</span>' in result

    def test_multiline_block_math(self):
        md = Markdown(plugins=[MathPlugin(engine="client")])
        text = """$$
a + b = c
d + e = f
g + h = i
$$"""
        result = md(text)
        assert '<div class="math_block">' in result
        assert "a + b = c" in result
        assert "d + e = f" in result
        assert "g + h = i" in result

    def test_math_adjacent_to_text(self):
        md = Markdown(plugins=[MathPlugin(engine="client")])
        result = md("Value=$x$, Result=$y$")
        assert result.count('<span class="math_inline">') == 2
        assert "Value=" in result
        assert ", Result=" in result

    def test_no_math_in_code_blocks(self):
        md = Markdown(plugins=[MathPlugin(engine="client")])
        text = "```\n$x + y$\n```"
        result = md(text)
        assert '<span class="math_inline">' not in result
        assert "$x + y$" in result

    def test_block_math_with_newlines(self):
        md = Markdown(plugins=[MathPlugin(engine="client")])
        text = "Before\n\n$$\nx + y\n$$\n\nAfter"
        result = md(text)
        assert '<div class="math_block">x + y</div>' in result
        assert "Before" in result
        assert "After" in result
