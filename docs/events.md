# Events & Input

`rc-tui` dispatches keyboard and mouse events to the top-most window's component tree. Events propagate via props (`on_click`, `on_key_down`, etc.) set on individual elements.

## Focus Management

Only one element can be focused at a time. Focusable types: `input`, `button`, `checkbox`, `radiobutton`, `switch`, `select`, `tabselect`, `textarea`.

- **Tab** — Cycles focus through all focusable elements in the current window.
- **Click** — Focuses the clicked element if it's focusable.
- **Modal trapping (v0.3.0+)** — When a `Dialog` or `Modal` is open, Tab cycling is automatically restricted to elements within that modal. Focus cannot escape to the background window.

Toggle the inspector overlay with **F12** to see element types, positions, and sizes.

## Keyboard Events

Key events are dispatched to the focused node. The `KeyEvent` dataclass contains:

```python
@dataclass
class KeyEvent:
    key: str        # Key name or single character
    ctrl: bool      # True if Ctrl is held
    shift: bool     # True if Shift is held
    alt: bool       # True if Alt is held
```

### Handling keys

Use `on_key_down` on any focusable element:

```python
def handle_key(event):
    if event.key == "q":
        app.stop()
    elif event.key == "UP":
        scroll_up()
    return True  # Mark as handled

Input(on_key_down=handle_key)
```

The handler receives the `KeyEvent` and should return `True` if the event was consumed.

### Per-widget keyboard behavior

| Widget | Keys | Behavior |
|---|---|---|
| `Button` | Space, Enter | Triggers `on_click` |
| `Input` | Printable, Backspace | Edits text value |
| `Input` | Enter | Triggers `on_submit` |
| `Textarea` | Printable, Backspace, Enter | Edits multi-line text |
| `Checkbox` | Space, Enter | Toggles `checked` |
| `RadioButton` | Space, Enter | Selects |
| `Switch` | Space, Enter | Toggles `on` |
| `TabSelect` | Left, Right, Space, Enter | Cycles tabs |
| `Select` | Space, Enter, Down, Up | Opens dropdown popup |

### Common key names

- Movement: `UP`, `DOWN`, `LEFT`, `RIGHT`
- Action: `ENTER`, `BACKSPACE`, `TAB`, `ESC`
- Function: `F1`–`F12`
- Navigation: `HOME`, `END`, `PAGE_UP`, `PAGE_DOWN`
- Control: `CTRL_A`–`CTRL_Z` (Ctrl+C terminates the app)

## Mouse Events

Mouse events dispatch to the element under the cursor. The `MouseEvent` dataclass:

```python
@dataclass
class MouseEvent:
    type: str     # 'CLICK', 'MOVE', 'SCROLL', 'RELEASE'
    x: int
    y: int
    button: int   # Mouse button (1=left, 2=middle, 3=right)
    delta: int    # Scroll delta (positive = down)
```

### Event types

| Type | Trigger | Behavior |
|---|---|---|
| `MOVE` | Mouse moves | Updates `hovered_node`, applies `hover_style` |
| `CLICK` | Button press | Focuses target, triggers per-widget click logic |
| `SCROLL` | Wheel rotation | Scrolls nearest `ScrollBox` ancestor |
| `RELEASE` | Button release | (Reserved for future drag support) |

### Per-widget click behavior

| Widget | Click Effect |
|---|---|
| `Button` | Walks up tree to find `on_click` handler |
| `TabSelect` | Computes which tab was clicked by x-position |
| `Select` | Opens popup menu |
| `Checkbox` | Toggles `checked` and calls `on_change` |
| `RadioButton` | Sets `selected=True` |
| `Switch` | Toggles `on` and calls `on_change` |
| `ScrollBox` | Click on scrollbar column jumps to that scroll position |

## The Top-Window Rule

Events only dispatch to the top-most window in the `App.windows` stack. This means:
- Modals and dialogs receive events first.
- Background windows are effectively inert while a modal is open.
- Clicking outside a modal's bounds hits the dimmed overlay — no event reaches the background window.
- Tab focus cycling respects the current top window (and its modal trapping).

## Low-Level Access

The `InputManager` is available via `app.input_manager` for custom event handling:

```python
events = app.input_manager.get_events()
for event in events:
    if isinstance(event, KeyEvent):
        handle_key(event)
```

This is rarely needed — prefer declarative event props (`on_click`, `on_key_down`, etc.) on elements.
