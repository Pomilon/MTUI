# Events & Input

`rc-tui` provides a unified event system for handling keyboard and mouse input across different terminal emulators.

## Event Dispatching

Events are automatically dispatched to the focused component. Functional components can listen for events using props like `on_key_press`, `on_click`, `on_mouse_move`, etc.

## Keyboard Events

Keyboard events contain the key name or the raw character.

```python
def handle_key(event):
    if event.key == "q":
        app.quit()
    elif event.key == "UP":
        scroll_up()

return Box(on_key_press=handle_key)
```

### Common Key Names
- `UP`, `DOWN`, `LEFT`, `RIGHT`
- `ENTER`, `BACKSPACE`, `TAB`, `ESC`
- `F1` - `F12`
- `HOME`, `END`, `PAGE_UP`, `PAGE_DOWN`
- `CTRL_A` - `CTRL_Z`

## Mouse Events

Mouse events provide coordinates and button information.

```python
def handle_click(event):
    print(f"Clicked at {event.x}, {event.y} with button {event.button}")

return Box(on_click=handle_click)
```

### Event Types
- `CLICK`: Button pressed and released.
- `SCROLL`: Mouse wheel moved (includes `delta`).
- `MOVE`: Mouse moved (if mouse tracking is enabled).
- `RELEASE`: Button released.

## Focus Management

Only one component can have focus at a time. 
- Focus can be cycled using the `TAB` key.
- Components must be "focusable" (e.g., `Button`, `Input`) to receive focus.
- You can manually manage focus using the `focused_node` property of the `App` instance.

## Low-Level Access

For advanced use cases, you can access the `InputManager` directly via the `App` instance, though this is generally discouraged in favor of the declarative event props.
