# mistune plugins

## math

enhanced math plugin for server-side render.

engine: typst, katex, mathjax
format: svg, mathml or html

! typst.ts alone is ~7MB. only recommend when the doc is very large and very format-heavy.

## frontmatter

block plugin or directive plugin.

- [x] support yaml, toml, json frontmatter (with block syntax), or directive (without parser syntax overhead)
- [ ] able to config a various of plugins, including math and graph

## graph

directive plugin.

engine: mermaid, graphviz, maybe more
render: server-side or client-side

## tabbed

https://facelessuser.github.io/pymdown-extensions/extensions/tabbed/

## emoji

https://facelessuser.github.io/pymdown-extensions/extensions/emoji/

