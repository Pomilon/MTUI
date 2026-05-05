# Hooks API

`rc-tui` implements a subset of standard React hooks to manage state and side effects within functional components.

## `useState`

Stores state that persists across renders.

```python
count, set_count = useState(initial_value)
```

- **Example**:
  ```python
  count, set_count = useState(0)
  return Button(f"Clicked {count} times", on_click=lambda _: set_count(count + 1))
  ```

## `useEffect`

Handles side effects like timers, data fetching, or manual DOM manipulations.

```python
useEffect(callback, dependencies)
```

- **Example**:
  ```python
  useEffect(lambda: print("Mounted!"), []) # Runs once on mount
  ```

- **Cleanup**: Return a function from the callback to handle cleanup.
  ```python
  def start_timer():
      t = threading.Timer(1.0, tick)
      t.start()
      return lambda: t.cancel()
  
  useEffect(start_timer, [])
  ```

## `useMemo`

Memoizes a computed value to avoid expensive recalculations.

```python
memoized_value = useMemo(lambda: expensive_func(a, b), [a, b])
```

## `useCallback`

Memoizes a function definition to prevent unnecessary re-renders of children that depend on function identity.

```python
memoized_callback = useCallback(lambda x: x + y, [y])
```

## `useRef`

Provides a mutable object whose `.current` property persists across renders. Useful for accessing underlying DOM elements or storing values without triggering a re-render.

```python
my_ref = useRef(None)
return Box(ref=my_ref)
```

## Rules of Hooks

1. **Only Call Hooks at the Top Level**: Don't call hooks inside loops, conditions, or nested functions.
2. **Only Call Hooks from Functional Components**: Or from other custom hooks.
