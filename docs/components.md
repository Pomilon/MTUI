# Component Reference

All `rc-tui` components share a set of common props for layout and styling.

## Common Props

-   **`width` / `height`**: Absolute (e.g., `10`, `"20"`) or Percentage (e.g., `"50%"`, `"100%"`).
-   **`margin` / `padding`**: Spacing around/inside the element.
-   **`flex_direction`**: `"row"` (default) or `"column"`.
-   **`gap`**: Numeric spacing between children in a flex container.
-   **`justify_content`**: `"start"`, `"center"`, `"end"`, `"space-between"`, `"space-around"`.
-   **`align_items`**: `"start"`, `"center"`, `"end"`.
-   **`border`**: `"none"`, `"single"`, `"double"`, `"rounded"`.
-   **`tooltip`**: Text to display in a floating overlay on hover.
-   **`style`**: A dictionary (or list of dictionaries) containing:
    - `fg`: Foreground color (RGB tuple, Hex string `#RRGGBB`, or Name e.g. `'red'`).
    - `bg`: Background color.
    - `bold`, `italic`, `underline`, `strikethrough`: Booleans.
    - `text_transform`: `"uppercase"`, `"lowercase"`, `"capitalize"`.
    - `box_shadow`: Boolean (renders a dark offset behind the element).
    - `hover_style`: Dictionary of styles applied when the mouse is over the element.
    - `focus_style`: Dictionary of styles applied when the element is focused (e.g. via Tab).

---

## Core Components

### `Box`
The primary layout container. Equivalent to `<div>` in HTML.
- **Props**: All common props.

### `Text`
Standard text display.
- **Props**: `text` (str). Supports multi-line.

### `Button`
Interactive button component.
- **Props**: `text` (str), `on_click` (callable).

### `Input`
Single-line text input.
- **Props**: `value`, `placeholder`, `on_change`.

### `ProgressBar`
Visual progress indicator.
- **Props**: `progress` (0.0 to 1.0), `color`.

### `Markdown`
Rich text renderer using Tree-sitter.
- **Props**: `content` (str). Supports headers, bold, italic, code blocks, and lists.

### `Code`
Syntax highlighted code block.
- **Props**: `content` (str), `language` (str).

### `ScrollBox`
A scrollable container for content that exceeds its bounds.
- **Props**: `scroll_x`, `scroll_y`, `on_scroll`.

### `Table`
Grid layout for structured data.
- **Props**: `headers`, `rows`, `column_widths`.

---

## Utility Components

- `Divider`: Horizontal or vertical line.
- `AsciiFont`: Large stylized text using `pyfiglet`.
- `Checkbox` / `RadioButton` / `Switch`: Form inputs.
- `Dialog` / `Modal`: Overlays for user interaction.
- `Toast`: Transient notification messages.
