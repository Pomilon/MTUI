# rc-tui

**rc-tui** is a high-performance, React-inspired Terminal User Interface (TUI) library for Python. It combines the declarative power of modern web frameworks with a high-performance C++ rendering engine to create fluid, beautiful, and complex terminal applications.

## Why rc-tui?

- **Declarative & Component-Based**: Build your UI with functional components and hooks (`useState`, `useEffect`).
- **Hybrid Performance**: High-frequency render logic and terminal diffing are in C++; layout and logic are in Python.
- **Advanced Styling**: Web-standard colors (Hex, RGB), pseudo-classes (`hover`, `focus`), and rich text attributes.
- **Cross-Platform**: Fully supports Linux, macOS, and Windows 10+ (Verified via CI/CD).

## Key Features (v0.2.0)

- **Rich Styling**: Hex colors, inheritance, `box_shadow`, and `text_transform`.
- **Interactive Pseudo-classes**: Define `hover_style` and `focus_style` for responsive components.
- **Full Mouse Support**: Real-time motion tracking for hovers and tooltips.
- **Flexbox Layout**: Powerful layout engine with `gap`, `flex_grow`, and percentage dimensions.
- **Markdown & Code**: Built-in support for Markdown and syntax-highlighted code blocks (via Tree-sitter).

## Installation

```bash
pip install rc-tui
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
            padding=1,
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

## Advanced Styling

```python
Text("Polished Text", style={
    'fg': '#ff00ff',           # Hex colors
    'italic': True,             # Rich attributes
    'text_transform': 'uppercase',
    'hover_style': {'fg': 'white', 'bold': True}
})
```

## Platform Support

| Platform | Support Status | Notes |
| :--- | :--- | :--- |
| **Linux** | ✅ Fully Supported | Primary development platform. |
| **macOS** | ✅ Supported | Verified via CI/CD. |
| **Windows** | ✅ Supported | Verified via CI/CD. Requires Windows 10+. |

## Documentation

- [Architecture Reference](./docs/architecture.md)
- [Component & Props API](./docs/components.md)
- [Hooks API](./docs/hooks.md)
- [Event System](./docs/events.md)

## Examples

Check out the [examples/](./examples) directory:
- `counter.py`: Basic state management.
- `styling_showcase.py`: Comprehensive styling engine demo.
- `dashboard.py`: Layout and progress indicators.

## Running Demos

After installing, run the demo scripts directly — no local path setup needed:

```bash
python tests/demo_app.py
python tests/demo_stylesheet.py
python tests/demo_features.py
```

For development, install in editable mode so changes take effect immediately:

```bash
pip install -e .
```

## License

MIT
