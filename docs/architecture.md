# Architecture

`rc-tui` uses a hybrid architecture: a React-inspired Python frontend for the component model, backed by a C++ rendering engine for terminal performance.

## Layers

```
┌─────────────────────────────────────┐
│         User Application             │
│  (Component subclasses, hooks)       │
├─────────────────────────────────────┤
│        Python Frontend (rc_tui)      │
│  ┌──────┬──────┬──────┬──────┬────┐  │
│  │ DOM  │Hooks │Recon │Layout│Render│  │
│  │(elems)│(state)│(vdom)│(flex)│(draw)│  │
│  └──────┴──────┴──────┴──────┴────┘  │
│  ┌──────────────────────────────────┐ │
│  │         Canvas (clip stack)      │ │
│  └──────────────┬───────────────────┘ │
├─────────────────┼─────────────────────┤
│       C++ Backend (_rctui_core)       │
│  ┌────────┬──────┬────────┬─────────┐ │
│  │Terminal│Buffer│Renderer│ Markdown│ │
│  │(ANSI)  │(grid)│ (diff) │ (parser)│ │
│  └────────┴──────┴────────┴─────────┘ │
├───────────────────────────────────────┤
│            OS / Terminal               │
└───────────────────────────────────────┘
```

## Render Loop (per frame)

1. **State change** — A hook like `set_count` or an event handler runs, marking the frame dirty.
2. **Reconciliation** — `build_tree()` walks the element tree, diffs against the previous tree, and creates `LayoutNode` instances. Key-based matching preserves state across re-renders.
3. **Measure** — Each node's intrinsic size is computed bottom-up.
4. **Layout** — `do_layout()` runs a flexbox algorithm top-down, assigning positions based on `flex_direction`, `gap`, `flex_grow`, `justify_content`, `align_items`, and padding/margin.
5. **Draw** — Each node renders into the C++ `Buffer` via `Canvas` (which manages a clip-rect stack for scrolling and overflow).
6. **Diff & Flush** — The C++ `Renderer` compares the old and new buffers cell-by-cell, emitting only changed cells to the terminal. This minimizes ANSI escape overhead.
7. **Effects** — Pending `useEffect` callbacks run after the frame is committed (matching React's commit-phase semantics).

## Window Management

The `App` maintains a stack of windows. Each window has its own element tree. The top window receives all events (mouse and keyboard). Dialogs and modals are pushed as new windows; closable windows are popped. When a modal is on top, focus cycling (Tab) is automatically trapped within the modal's subtree.

## C++ / Python Split

| Concern | Layer | Reason |
|---|---|---|
| Component model, hooks, state | Python | Complex, changeable logic |
| Flexbox layout | Python | Algorithmic, needs rapid iteration |
| Widget rendering (text, buttons, inputs) | Python | Each widget has unique logic |
| Terminal raw mode, ANSI codes | C++ | OS-specific, performance-critical |
| Cell buffer (2D grid of styled cells) | C++ | Bulk operations need native speed |
| Diff-based screen update | C++ | Cell-by-cell comparison is a tight loop |
| Markdown parsing | C++ | Offloaded for performance |

## Key Design Decisions

- **No immediate mode** — The UI is retained (tree persists across frames) with declarative updates, not immediate-mode draw calls per frame.
- **Canvas clip stack** — Each nested scrolling container pushes a clip rect; the stack is reset every frame.
- **State held in hook arrays** — Each component instance stores its hooks in a numbered list, indexed by call order (same rule as React: hooks must not be called conditionally).
- **Effects run after paint** — Side effects never block the render loop.
