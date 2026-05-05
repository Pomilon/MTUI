# rc-tui

**rc-tui** is a high-performance, React-inspired Terminal User Interface (TUI) library for Python. It combines the declarative power of modern web frameworks with a high-performance C++ rendering engine to create fluid, beautiful, and complex terminal applications.

## Key Features

-   **Declarative UI**: Build interfaces using components, props, and state, just like React.
-   **High-Performance Engine**: Core rendering, terminal management, and diffing logic implemented in C++ for maximum speed.
-   **Built-in Layout Engine**: Flexbox-like layout system for easy positioning and responsiveness.
-   **Rich Component Library**: Includes Box, Text, Button, Input, ScrollBox, Markdown, Code, Tables, and more.
-   **Hooks System**: `useState`, `useEffect`, `useMemo`, and `useCallback` for clean state management.
-   **Mouse Support**: Full support for clicking, scrolling, and move events.

## Platform Support

| Platform | Support Status | Notes |
| :--- | :--- | :--- |
| **Linux** | ✅ Fully Supported | Primary development and testing platform. |
| **macOS** | ⚠️ Build Only | Wheels are provided, but functionality is currently untested. |
| **Windows** | ❌ Not Supported | CI/CD and PyPI publishing are disabled. Local builds may work but are not officially supported. |

## Installation

```bash
pip install rc-tui
```

*Note: Since this library uses native extensions, binary wheels are provided for Linux and macOS. If no wheel is available for your architecture, you will need `cmake`, `ninja`, and a C++17 compiler installed.*

## Quick Start

```python
from rctui import App, Component, Box, Text, Button, useState

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
