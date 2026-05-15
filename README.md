# rc-tui

**rc-tui** is a high-performance, React-inspired Terminal User Interface (TUI) library for Python. It combines declarative components and hooks with a C++ rendering engine for fluid terminal applications.

## Why rc-tui?

- **Declarative & Component-Based** — Build UIs with components, hooks, and a flexbox layout engine. Familiar if you know React.
- **Hybrid Performance** — Render logic and terminal diffing in C++; layout and component logic in Python.
- **Rich Styling** — Hex and RGB colors, style inheritance, pseudo-classes (`hover`, `focus`), and text transforms.
- **30+ Widgets** — From buttons and inputs to tables, virtual lists, markdown renderer, and modals.
- **Cross-Platform** — Linux, macOS, and Windows 10+.

## Key Features (v0.4.0)

- **Component Model** — Class-based and functional components with key-based reconciliation.
- **Hooks** — `useState`, `useEffect`, `useMemo`, `useCallback`, `useRef`, `useWindowSize`. Effects properly trigger re-renders.
- **Flexbox Layout** — Column/row layout with `flex_grow`, `gap`, `justify_content`, `align_items`, padding, margin, and percentage dimensions.
- **Keyboard Navigation** — Tab to cycle focus, Space/Enter to activate buttons and toggles. Focus trapped inside modals.
- **Rich Styling** — Hex and RGB colors, style arrays, `hover_style`/`focus_style` pseudo-classes, `box_shadow`, `text_transform`.
- **Full Mouse Support** — Click, scroll, hover tracking, tooltips. Clickable scrollbar thumbs.
- **Window Management** — Stack-based windows, dialogs, modals with auto-dim background. Context manager support for clean exit.
- **Advanced Widgets** — `Table` (sortable), `VirtualList` (windowed, persistent scroll), `Markdown`, `Code` (syntax-highlighted via Tree-sitter), `Accordion`, `Slider`, `Timeline`.
- **Textarea with Cursor** — Arrow keys, HOME/END, insert and delete at cursor position.
- **Refs** — `useRef` wired to `LayoutNode` for imperative access.
- **StyleSheet Validation** — `StyleSheet.create` validates prop names and types at definition time.
- **Extensible Widget System** — Widget handlers registered via `widgets.register()`, enabling custom widget types without editing core files.

## Installation

```bash
pip install rc-tui
```

For development:

```bash
pip install -e .
```

## Quick Start

```python
from rc_tui import App, Component, Box, Text, Button, useState

class Counter(Component):
    def render(self):
        count, set_count = useState(0)
        
        return Box(
            flex_direction="column",
            align_items="center",
            gap=1,
            border="rounded",
            padding=2,
            children=[
                Text(f"Value: {count}", style={'bold': True, 'fg': 'cyan'}),
                Button(
                    "Increment", 
                    on_click=lambda _: set_count(count + 1),
                    style={'hover_style': {'bg': 'green'}}
                )
            ]
        )

if __name__ == "__main__":
    App(Counter).run()
```

Press **Tab** to cycle focus, **Space**/**Enter** to activate the button, **F12** for the inspector overlay.

## Platform Support

| Platform | Status |
|---|---|
| **Linux** | ✅ Fully supported |
| **macOS** | ✅ Supported (CI-verified) |
| **Windows** | ✅ Supported (CI-verified, 10+) |

## Documentation

- [Architecture Reference](./docs/architecture.md)
- [Component & Props API](./docs/components.md) — all 30+ widgets, layout props, styling, refs
- [Hooks API](./docs/hooks.md) — useState, useEffect, useRef, useMemo, useCallback, useWindowSize
- [Event System](./docs/events.md) — keyboard, mouse, focus management, modal trapping

## Running Demos

```bash
python tests/demo_app.py
python tests/demo_stylesheet.py
python tests/demo_features.py
python tests/demo_features_v2.py
```

## License

MIT
