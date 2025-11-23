import re

import mistune
import pytest

from mkdocs_mistune.mistune_plugins.math import (
    Math,
    _render_math_typst,
    render_math,
)


class TestRenderMathTypst:
    def test_inline_mode(self):
        result = _render_math_typst("inline", "x + y")
        assert isinstance(result, str)
        assert re.match("^<svg.*</svg>\\s*$", result, re.DOTALL) is not None

    def test_block_mode(self):
        result = _render_math_typst("block", "x + y")
        assert isinstance(result, str)
        assert re.match("^<svg.*</svg>\\s*$", result, re.DOTALL) is not None

    def test_invalid_mode(self):
        with pytest.raises(ValueError, match="invalid render mode"):
            _render_math_typst("invalid", "x + y")  # type: ignore


class TestRenderMath:
    def test_inline_client_mode(self):
        result = render_math("inline", "client", "x + y")
        assert result == '<span class="math_inline">x + y</span>'

    def test_block_client_mode(self):
        result = render_math("block", "client", "x + y = z")
        assert result == '<div class="math_block">x + y = z</div>'


class TestIntegration:
    def test_inline_math_basic(self):
        markdown = mistune.create_markdown(plugins=[Math()])
        result = markdown("This is $x + y$ inline math")
        assert '<span class="math_inline">x + y</span>' in result

    def test_block_math_basic(self):
        markdown = mistune.create_markdown(plugins=[Math()])
        result = markdown("This is\n$$\nx + y\n$$\nblock math")
        assert '<div class="math_block">x + y</div>' in result
