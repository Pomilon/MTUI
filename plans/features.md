# Animation System & Responsive Features

## Objective
Introduce a duration-based animation system, responsive layout hooks, and expand the component library with standard UI elements.

## Phase 1: Animation System (REMOVED)
- Animation system was removed due to TUI freezing issues. Focus shifted to Responsive Layouts and Standard Components.

## Phase 2: Responsive Layouts
- **Hook**: `useWindowSize()` returns `(width, height)`.
- **Mechanism**:
  - `App` will track terminal size changes and notify hooks.
  - Components using `useWindowSize` will re-render on resize.

## Phase 3: New Components
- **Slider**: `Slider(value, min, max, on_change)`.
- **Tooltip**: `Tooltip(text, children)`.
- **Accordion**: `Accordion(title, children, expanded)`.

## Verification
- Create a demo showing a "sidebar" that slides in/out with an animation.
- Create a demo that changes layout (e.g., from row to column) based on window width.
- Verify new components work with mouse and keyboard.
