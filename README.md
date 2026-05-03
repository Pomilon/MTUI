# RC-TUI

RC-TUI is a modern, high-performance Terminal User Interface (TUI) library for Python, inspired by React. It features a hooks-based state management system, efficient virtualization for large datasets, and a powerful rendering engine with support for advanced widgets.

## Features

- React-Inspired Hooks: Use useState, useEffect, useMemo, useCallback, and useRef to manage component state and lifecycle.
- Efficient Virtualization: Render lists with thousands of items smoothly using the VirtualList widget.
- Advanced Widgets:
  - Table: Sortable columns and dynamic data rendering.
  - Tabs: Intuitive tab-based navigation.
  - Inputs & Textareas: Full keyboard support with focus management.
  - Progress Bars & Switches: Highly customizable visual indicators.
- Native Performance: Core rendering and layout logic designed for speed and responsiveness.
- Developer Inspector: Toggle with F12 to inspect the UI tree, dimensions, and styling in real-time.

## Installation

```bash
pip install rctui # package available soon!
```

## Building from Source

RC-TUI uses a C++ core for high-performance rendering. To build it from source, you'll need a C++17 compiler and CMake.

```bash
# Clone the repository
git clone https://github.com/Pomilon/RC-TUI.git
cd RC-TUI

# Install the package in editable mode
pip install -e .
```

## Quick Start

```python
from rctui import App, Box, Text, Button, useState

def MyComponent(props):
    count, set_count = useState(0)
    
    return Box(
        flex_direction="column",
        align_items="center",
        justify_content="center",
        children=[
            Text(f"Count: {count}", fg=(0, 255, 255)),
            Button("Increment", on_click=lambda: set_count(count + 1), bg=(0, 128, 0))
        ]
    )

app = App(MyComponent)
app.run()
```

## Advanced Usage

### Virtualized List

```python
from rctui import VirtualList, Text

items = [{"id": i, "name": f"Item {i}"} for i in range(1000)]

def render_item(item, index):
    return Text(f"Row {index}: {item['name']}")

# Inside a component:
VirtualList(
    items=items,
    render_item=render_item,
    item_height=1
)
```

### Hooks

```python
from rctui import useState, useEffect
import threading
import time

def Timer(props):
    seconds, set_seconds = useState(0)
    
    def effect():
        running = True
        def loop():
            while running:
                time.sleep(1)
                set_seconds(s => s + 1)
        
        t = threading.Thread(target=loop, daemon=True)
        t.start()
        
        return lambda: setattr(running, False) # Cleanup function
        
    useEffect(effect, [])
    
    return Text(f"Elapsed: {seconds}s")
```

## Developer Tools

Press F12 while the app is running to enable the Hover Inspector. Hover over any element to see its type, coordinates, and bounding box.

## License

MIT - Copyright (c) 2026 Pomilon
