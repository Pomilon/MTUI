# Architecture

`rc-tui` uses a hybrid architecture designed for both ease of use (Python) and high performance (C++).

## Core Components

### 1. Python Frontend (`src/python/rc_tui`)
The Python layer provides the React-inspired programming model:
- **Reconciler**: Manages the component tree and decides which parts of the UI need to be updated based on state changes.
- **Hooks**: Implements `useState`, `useEffect`, etc., maintaining state across renders.
- **DOM/Elements**: Defines the high-level UI components and their properties.
- **Layout Engine**: Calculates the size and position of elements using a flexbox-like algorithm.

### 2. C++ Backend (`src/cpp`)
The C++ layer handles the heavy lifting via `pybind11` bindings:
- **Terminal Management**: Low-level ANSI escape sequence handling for raw mode, colors, and cursor movement.
- **Buffer System**: An efficient 2D grid of `Cell` objects representing the screen state.
- **Renderer**: Compares the current and previous buffers to perform "smart" diff-based rendering, only updating modified cells to minimize terminal I/O.
- **Performance**: Heavy operations like markdown parsing or complex drawing are offloaded to C++.

## The Render Loop

1. **State Update**: A hook like `set_count` is called.
2. **Reconciliation**: Python identifies the modified branch of the component tree.
3. **Layout**: The engine recalculates positions and dimensions.
4. **Drawing**: Elements "draw" themselves onto a C++ `Buffer`.
5. **Diff & Flush**: The C++ `Renderer` compares the new buffer with the terminal's current state and writes only the minimal set of escape sequences to `stdout`.

## Performance Considerations

- **Surgical Updates**: Only changed components are re-rendered.
- **C++ Offloading**: Large buffers and intensive terminal I/O are handled at the native level.
- **Minimal System Calls**: Drawing occurs in memory; terminal communication is batched and flushed once per frame.
