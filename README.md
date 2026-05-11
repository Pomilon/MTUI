# rc-tui

**rc-tui** is a high-performance, React-inspired Terminal User Interface (TUI) library for Python. It combines the declarative power of modern web frameworks with a high-performance C++ rendering engine to create fluid, beautiful, and complex terminal applications.

## Key Features

-   **Declarative UI**: Build interfaces using components, props, and state, just like React.
-   **High-Performance Engine**: Core rendering, terminal management, and diffing logic implemented in C++ for maximum speed.
-   **Advanced Styling**: Web-like styling with Hex colors, pseudo-classes (`hover_style`, `focus_style`), inheritance, and text effects (italic, underline, etc.).
-   **Full Mouse Support**: Support for clicking, scrolling, and **real-time motion tracking** for hover effects and tooltips.
-   **Built-in Layout Engine**: Flexbox-like layout system with support for `gap`, `flex_grow`, and percentage dimensions.
-   **Rich Component Library**: Includes Box, Text, Button, Input, ScrollBox, Markdown, Code, Tables, and more.

## Platform Support

| Platform | Support Status | Notes |
| :--- | :--- | :--- |
| **Linux** | ✅ Fully Supported | Primary development and testing platform. |
| **macOS** | ✅ Supported | Verified via CI/CD (GitHub Actions). |
| **Windows** | ✅ Supported | Verified via CI/CD (GitHub Actions). Requires Windows 10+. |

## Installation

```bash
pip install rc-tui
```

*Note: Since this library uses native extensions, binary wheels are provided for Linux and macOS. If no wheel is available for your architecture, you will need `cmake`, `ninja`, and a C++17 compiler installed.*

## Quick Start

```python
from rc_tui import App, Component, Box, Text, Button, useState

class Counter(Component):
    def render(self):
        count, set_count = useState(0)
        
        return Box(
            flex_direction="column",
            align_items="center",
            justify_content="center",
            border="single",
            children=[
                Text(f"Count: {count}", style={"bold": True}),
                Button(
                    "Increment", 
                    on_click=lambda _: set_count(count + 1)
                )
            ]
        )

if __name__ == "__main__":
    app = App(Counter)
    app.run()
```

## Documentation

For detailed information, see the [docs](./docs) folder:
- [Architecture](./docs/architecture.md)
- [Component Reference](./docs/components.md)
- [Hooks API](./docs/hooks.md)
- [Events & Input](./docs/events.md)

## License

MIT
