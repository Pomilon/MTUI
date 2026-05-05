# Component Reference

All `rc-tui` components share a set of common props for layout and styling.

## Common Props

-   **`width` / `height`**: Absolute (e.g., `10`, `"20"`) or Percentage (e.g., `"50%"`, `"100%"`).
-   **`margin` / `padding`**: Spacing around/inside the element.
-   **`flex_direction`**: `"row"` (default) or `"column"`.
-   **`justify_content`**: `"start"`, `"center"`, `"end"`, `"space-between"`, `"space-around"`.
-   **`align_items`**: `"start"`, `"center"`, `"end"`.
-   **`border`**: `"none"`, `"single"`, `"double"`, `"rounded"`.
-   **`style`**: A dictionary containing:
    - `fg`: Foreground color (RGB tuple or ANSI color name).
    - `bg`: Background color.
    - `bold`: Boolean.
    - `underline`: Boolean.

---

## Core Components

### `Box`
The fundamental container for layout. Equivalent to `<div>` in HTML.

### `Text`
Displays a string of text. Supports word wrapping.

### `Button`
An interactive element with `on_click` support.

### `Input`
A single-line text input field.

### `ScrollBox`
A container that provides vertical and/or horizontal scrolling for its children.

### `Markdown`
Renders formatted markdown text, including headers, lists, and code blocks.

### `Code`
Syntax-highlighted code blocks (using `tree-sitter`).

### `Table`
Renders tabular data with headers and rows.

### `ProgressBar`
A visual representation of progress (0.0 to 1.0).

### `AsciiFont`
Renders text using ASCII art fonts (via `pyfiglet`).

---

## Example: Complex Layout

```python
Box(
    flex_direction="column",
    width="100%",
    height="100%",
    children=[
        # Header
        Box(
            height=3,
            border="single",
            children=[Text("My Dashboard", style={"bold": True})]
        ),
        # Main Content
        Box(
            flex_direction="row",
            children=[
                # Sidebar
                Box(width=20, border="single", children=[...]),
                # Main Body
                Box(flex_grow=1, border="single", children=[...])
            ]
        ),
        # Footer
        Box(height=1, children=[Text("Press Q to quit")])
    ]
)
```
