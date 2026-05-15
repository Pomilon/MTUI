# Hooks API

`rc-tui` implements React-style hooks for state management and side effects in components. Hooks are only valid inside `Component.render()` or functional components.

## Rules of Hooks

1. **Only call hooks at the top level** — not inside loops, conditions, or nested functions. Call order must be identical across every render.
2. **Only call hooks from components** — either `Component.render()` or a functional component body. Custom hooks (functions that call other hooks) are supported.

---

## `useState`

Returns a stateful value and a setter. The setter triggers a re-render.

```python
count, set_count = useState(0)
```

The setter accepts a new value or a function:

```python
set_count(count + 1)
set_count(lambda prev: prev + 1)
```

Example:

```python
class Counter(Component):
    def render(self):
        count, set_count = useState(0)
        return Button(
            f"Count: {count}",
            on_click=lambda: set_count(count + 1)
        )
```

---

## `useEffect`

Runs side effects after the render is committed to the screen. Matches React's `useEffect` semantics.

```python
useEffect(callback, dependencies)
```

- If `dependencies` is `None` or omitted, the effect runs after every render.
- If `dependencies` is an empty list `[]`, the effect runs once on mount.
- If `dependencies` is a list of values, the effect re-runs when any value changes.

The callback can return a cleanup function:

```python
def start_timer():
    t = threading.Timer(1.0, tick)
    t.start()
    return lambda: t.cancel()

useEffect(start_timer, [])
```

Cleanups run before the next effect run or on unmount.

---

## `useMemo`

Memoizes a computed value, recalculating only when dependencies change.

```python
sorted_data = useMemo(
    lambda: sorted(raw_data, key=lambda x: x['name']),
    [raw_data]
)
```

---

## `useCallback`

Memoizes a function definition. Equivalent to `useMemo(lambda: fn, deps)`.

```python
handle_click = useCallback(lambda: do_something(x), [x])
```

---

## `useRef`

Returns a mutable dict `{"type": "ref", "value": initial}` that persists across renders.

In v0.3.0+, the `ref` prop on elements is wired into the reconciler: when a primitive element has a `ref` prop pointing to a `useRef` return value, the `LayoutNode` is assigned to `ref["value"]`.

```python
my_ref = useRef(None)
return Box(ref=my_ref, children=[Text("Hello")])

# After render: my_ref["value"] is the LayoutNode for this Box
```

Use refs for:
- Accessing element dimensions or position
- Imperative operations on a node
- Storing mutable values that don't trigger re-renders

---

## `useWindowSize`

Returns the current terminal size `(width, height)` as a tuple. Updates on terminal resize.

```python
w, h = useWindowSize()
return Text(f"Terminal is {w}x{h}")
```

---

## Custom Hooks

Any function that calls hooks is a custom hook. Follow the same rules (top-level calls only).

```python
def useCounter(initial=0):
    count, set_count = useState(initial)
    increment = useCallback(lambda: set_count(count + 1), [count])
    return count, increment

class MyApp(Component):
    def render(self):
        count, inc = useCounter(5)
        return Button(f"Count: {count}", on_click=inc)
```
