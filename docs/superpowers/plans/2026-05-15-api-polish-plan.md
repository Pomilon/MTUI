# API Polish (Phase 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship 5 high-impact API polish fixes: button keyboard activation, justify_content/align_items, ref wiring, modal focus trapping, and StyleSheet.create validation.

**Architecture:** All 5 changes are independent and touch different files. They can be implemented in any order. Each adds small, well-bounded logic to existing functions without refactoring.

**Tech Stack:** Python 3.9+, setuptools/CMake build (but no C++ changes needed)

---

### Task 1: Button keyboard activation

**Files:**
- Modify: `src/python/rc_tui/app.py` (~10 lines in `dispatch_event`)
- Test: `tests/test_full_integration.py` (add test function)

- [ ] **Step 1: Write the failing test**

Add a `MockTerminal` class and test to the bottom of `tests/test_full_integration.py`:

```python
class MockTerminal:
    def enable_raw_mode(self): pass
    def enter_alternate_screen(self): pass
    def enable_mouse_tracking(self): pass
    def disable_raw_mode(self): pass
    def exit_alternate_screen(self): pass
    def disable_mouse_tracking(self): pass
    def clear_screen(self): pass
    def get_size(self): return (80, 24)


def test_button_keyboard_activation():
    from rc_tui import App
    from rc_tui.reconciler import LayoutNode
    from rc_tui.core import Element
    from rc_tui.input import KeyEvent

    click_log = []
    app = App(None, terminal=MockTerminal())

    button = LayoutNode(Element('button', {'on_click': lambda: click_log.append('clicked')}))
    button.is_focused = True
    app.focused_node = button
    app.windows[-1]['node'] = button

    app.dispatch_event(KeyEvent(' ', 'SPACE'))
    assert len(click_log) == 1, f"Expected 1 click after SPACE, got {len(click_log)}"

    app.dispatch_event(KeyEvent('ENTER', 'ENTER'))
    assert len(click_log) == 2, f"Expected 2 clicks after ENTER, got {len(click_log)}"

    app.cleanup()
    print("test_button_keyboard_activation PASSED")


def test_button_keyboard_no_on_click():
    from rc_tui import App
    from rc_tui.reconciler import LayoutNode
    from rc_tui.core import Element
    from rc_tui.input import KeyEvent

    app = App(None, terminal=MockTerminal())
    button = LayoutNode(Element('button', {}))
    button.is_focused = True
    app.focused_node = button
    app.windows[-1]['node'] = button

    # Should not crash when button has no on_click
    app.dispatch_event(KeyEvent(' ', 'SPACE'))
    app.dispatch_event(KeyEvent('ENTER', 'ENTER'))
    app.cleanup()
    print("test_button_keyboard_no_on_click PASSED")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python tests/test_full_integration.py
```

Expected: `AssertionError` or `AttributeError` because Button key handler doesn't exist yet.

- [ ] **Step 3: Write minimal implementation**

In `src/python/rc_tui/app.py`, inside `dispatch_event()`, in the `KeyEvent` branch under `if focused_node:`, add a handler after the `textarea` block (around line 465):

```python
if focused_node.type == 'button' and event.key in (' ', 'ENTER'):
    on_click = focused_node.props.get('on_click')
    if on_click:
        try:
            if hasattr(on_click, '__code__'):
                num_args = on_click.__code__.co_argcount
                num_defaults = len(on_click.__defaults__ or [])
                if num_args - num_defaults > 0:
                    on_click(event)
                else:
                    on_click()
            else:
                try:
                    on_click(event)
                except TypeError:
                    on_click()
        except Exception as e:
            self.log_error(f"on_click handler error: {e}")
    self.request_render()
    return
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python tests/test_full_integration.py
```

Expected: Both new tests print PASSED, no assertion errors.

- [ ] **Step 5: Commit**

```bash
git add src/python/rc_tui/app.py tests/test_full_integration.py
git commit -m "feat: add keyboard activation for Button (Space/Enter)"
```

---

### Task 2: Implement justify_content / align_items

**Files:**
- Modify: `src/python/rc_tui/layout.py` (~40 lines added to `do_layout`)
- Test: `tests/test_full_integration.py` (add test functions)

- [ ] **Step 1: Write the failing test**

Add to `tests/test_full_integration.py`:

```python
def test_justify_content_center():
    from rc_tui.layout import do_layout, measure
    from rc_tui.reconciler import LayoutNode
    from rc_tui.core import Element

    parent = LayoutNode(Element('box', {
        'flex_direction': 'column',
        'width': 40,
        'height': 20,
        'justify_content': 'center'
    }))
    child = LayoutNode(Element('text', {'text': 'Hello'}))
    child.w = 5
    child.h = 3
    parent.children = [child]

    measure(parent, 40, 20)
    do_layout(parent, 0, 0, 40, 20)

    # With justify_content: center in a 20-high container with one 3-high child,
    # remaining_space = 17, offset = 17/2 = 8 (integer division)
    assert child.y == 8, f"Expected child.y=8, got {child.y}"
    print("test_justify_content_center PASSED")


def test_justify_content_flex_end():
    from rc_tui.layout import do_layout, measure
    from rc_tui.reconciler import LayoutNode
    from rc_tui.core import Element

    parent = LayoutNode(Element('box', {
        'flex_direction': 'column',
        'width': 40,
        'height': 20,
        'justify_content': 'flex-end'
    }))
    child = LayoutNode(Element('text', {'text': 'Hello'}))
    child.w = 5
    child.h = 3
    parent.children = [child]

    measure(parent, 40, 20)
    do_layout(parent, 0, 0, 40, 20)

    # remaining_space = 17, offset = 17
    assert child.y == 17, f"Expected child.y=17, got {child.y}"
    print("test_justify_content_flex_end PASSED")


def test_align_items_center():
    from rc_tui.layout import do_layout, measure
    from rc_tui.reconciler import LayoutNode
    from rc_tui.core import Element

    parent = LayoutNode(Element('box', {
        'flex_direction': 'row',
        'width': 40,
        'height': 10,
        'align_items': 'center'
    }))
    child = LayoutNode(Element('text', {'text': 'Hi'}))
    child.w = 2
    child.h = 1
    parent.children = [child]

    measure(parent, 40, 10)
    do_layout(parent, 0, 0, 40, 10)

    # In a row, align_items controls vertical positioning.
    # Container h=10, child h=1 with no padding/margin on container.
    # remaining cross-axis = 10 - 1 = 9, offset = 9/2 = 4
    assert child.y == 4, f"Expected child.y=4, got {child.y}"
    print("test_align_items_center PASSED")


def test_justify_content_flex_start_default():
    from rc_tui.layout import do_layout, measure
    from rc_tui.reconciler import LayoutNode
    from rc_tui.core import Element

    parent = LayoutNode(Element('box', {
        'flex_direction': 'column',
        'width': 40,
        'height': 20,
    }))
    child = LayoutNode(Element('text', {'text': 'Hello'}))
    child.w = 5
    child.h = 3
    parent.children = [child]

    measure(parent, 40, 20)
    do_layout(parent, 0, 0, 40, 20)

    # Default flex-start: no offset
    assert child.y == 0, f"Expected child.y=0 (default), got {child.y}"
    print("test_justify_content_flex_start_default PASSED")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python tests/test_full_integration.py
```

Expected: Assertion errors because justify_content/align_items are not implemented.

- [ ] **Step 3: Write minimal implementation**

In `src/python/rc_tui/layout.py`, modify `do_layout()`. After computing `inner_w` and `inner_h` (line 179), and after the flex measurement loop, add justify_content offset logic before the child layout loop.

First read `justify_content` and `align_items` from props right after the gap calculation (~line 190):

```python
justify = node.props.get('justify_content', 'flex-start')
align = node.props.get('align_items', 'flex-start')
```

Then add main-axis justify offset before the positioning loop (~line 206-208). After `remaining_space` is computed:

```python
# justify_content offset on main axis
justify_offset = 0
if flex_dir == 'column':
    if justify == 'center':
        justify_offset = remaining_space // 2
    elif justify == 'flex-end':
        justify_offset = remaining_space
    elif justify == 'space-between' and len(non_null_children) > 1:
        gap = remaining_space // (len(non_null_children) - 1)
    elif justify == 'space-around':
        gap = remaining_space // len(non_null_children)
        justify_offset = gap // 2
else:
    if justify == 'center':
        justify_offset = remaining_space // 2
    elif justify == 'flex-end':
        justify_offset = remaining_space
    elif justify == 'space-between' and len(non_null_children) > 1:
        gap = remaining_space // (len(non_null_children) - 1)
    elif justify == 'space-around':
        gap = remaining_space // len(non_null_children)
        justify_offset = gap // 2
```

Then apply the offset to the starting position (~lines 207-208):

```python
current_x = pl + (justify_offset if flex_dir == 'row' else 0)
current_y = pt + (justify_offset if flex_dir == 'column' else 0)
```

Add cross-axis alignment inside the child loop, right before `do_layout(child, ...)`. For each child, after computing `cw` and `ch`:

```python
# align_items on cross axis
cross_offset = 0
if align == 'center':
    if flex_dir == 'column':
        cross_offset = (inner_w - cw) // 2
    else:
        cross_offset = (inner_h - ch) // 2
elif align == 'flex-end':
    if flex_dir == 'column':
        cross_offset = inner_w - cw
    else:
        cross_offset = inner_h - ch
elif align == 'stretch':
    if flex_dir == 'column':
        cw = max(cw, inner_w)
    else:
        ch = max(ch, inner_h)

do_layout(child, current_x + (cross_offset if flex_dir == 'row' else 0),
          current_y + (cross_offset if flex_dir == 'column' else 0),
          cw, ch, ...)
```

The full modified section of `do_layout()` (~lines 204-233) becomes:

```python
    remaining_space = max(0, (inner_h if flex_dir == 'column' else inner_w) - fixed_space)

    justify = node.props.get('justify_content', 'flex-start')
    align = node.props.get('align_items', 'flex-start')

    justify_offset = 0
    if flex_dir == 'column':
        if justify == 'center':
            justify_offset = remaining_space // 2
        elif justify == 'flex-end':
            justify_offset = remaining_space
        elif justify == 'space-between' and len(non_null_children) > 1:
            gap = remaining_space // (len(non_null_children) - 1)
        elif justify == 'space-around':
            gap = remaining_space // len(non_null_children)
            justify_offset = gap // 2
    else:
        if justify == 'center':
            justify_offset = remaining_space // 2
        elif justify == 'flex-end':
            justify_offset = remaining_space
        elif justify == 'space-between' and len(non_null_children) > 1:
            gap = remaining_space // (len(non_null_children) - 1)
        elif justify == 'space-around':
            gap = remaining_space // len(non_null_children)
            justify_offset = gap // 2

    current_x = pl + (justify_offset if flex_dir == 'row' else 0)
    current_y = pt + (justify_offset if flex_dir == 'column' else 0)

    for i, (child, cw, ch, grow) in enumerate(child_measures):
        if grow > 0:
            share = int(remaining_space * (grow / flex_total)) if flex_total > 0 else 0
            if flex_dir == 'column':
                ch = share
                cw = inner_w
            else:
                cw = share
                ch = inner_h
        else:
            if flex_dir == 'column' and child.props.get('width') is None:
                cw = inner_w
            if flex_dir == 'row' and child.props.get('height') is None:
                ch = inner_h

        cross_offset = 0
        if align == 'center':
            if flex_dir == 'column':
                cross_offset = (inner_w - cw) // 2
            else:
                cross_offset = (inner_h - ch) // 2
        elif align == 'flex-end':
            if flex_dir == 'column':
                cross_offset = inner_w - cw
            else:
                cross_offset = inner_h - ch
        elif align == 'stretch':
            if flex_dir == 'column':
                cw = max(cw, inner_w)
            else:
                ch = max(ch, inner_h)

        scroll_off_y = node.scroll_y if node.type == 'scrollbox' else 0
        scroll_off_x = node.scroll_x if node.type == 'scrollbox' else 0

        do_layout(child, current_x + (cross_offset if flex_dir == 'row' else 0),
                  current_y + (cross_offset if flex_dir == 'column' else 0),
                  cw, ch,
                  node.screen_x - scroll_off_x, node.screen_y - scroll_off_y)

        if flex_dir == 'column':
            current_y += ch + gap
        else:
            current_x += cw + gap
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python tests/test_full_integration.py
```

Expected: All 4 new layout tests print PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/python/rc_tui/layout.py tests/test_full_integration.py
git commit -m "feat: implement justify_content and align_items layout props"
```

---

### Task 3: Wire ref into reconciler

**Files:**
- Modify: `src/python/rc_tui/reconciler.py` (~4 lines added to `build_tree`)
- Test: `tests/test_full_integration.py` (add test function)

- [ ] **Step 1: Write the failing test**

Add to `tests/test_full_integration.py`:

```python
def test_ref_wired_to_layout_node():
    from rc_tui.reconciler import build_tree
    from rc_tui.core import Element

    ref_holder = {"value": None}
    el = Element('box', {'ref': ref_holder}, [
        Element('text', {'text': 'child'})
    ])

    class MockApp:
        focused_node = None
        windows = []

    node = build_tree(el, MockApp())
    assert ref_holder["value"] is not None, "ref.value was not set"
    assert ref_holder["value"].type == 'box', f"Expected type 'box', got {ref_holder['value'].type}"
    assert len(ref_holder["value"].children) == 1
    print("test_ref_wired_to_layout_node PASSED")


def test_ref_no_op_when_absent():
    from rc_tui.reconciler import build_tree
    from rc_tui.core import Element

    class MockApp:
        focused_node = None
        windows = []

    el = Element('box', {}, [])
    node = build_tree(el, MockApp())
    assert node is not None
    assert node.type == 'box'
    print("test_ref_no_op_when_absent PASSED")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python tests/test_full_integration.py
```

Expected: `AssertionError` on `ref_holder["value"] is not None` (ref not wired).

- [ ] **Step 3: Write minimal implementation**

In `src/python/rc_tui/reconciler.py`, at the end of the primitive element branch (after the key-based reconciliation and state carry-over, right before `return node` on line 175), add:

```python
ref = element.props.get('ref')
if isinstance(ref, dict) and 'value' in ref:
    ref['value'] = node
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python tests/test_full_integration.py
```

Expected: Both ref tests print PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/python/rc_tui/reconciler.py tests/test_full_integration.py
git commit -m "feat: wire ref prop into reconciler to expose LayoutNode"
```

---

### Task 4: Focus trapping in modals

**Files:**
- Modify: `src/python/rc_tui/app.py` (~5 lines added to `_cycle_focus`)
- Test: `tests/test_full_integration.py` (add test functions)

- [ ] **Step 1: Write the failing test**

Add to `tests/test_full_integration.py`:

```python
def test_modal_focus_trapping():
    from rc_tui import App
    from rc_tui.reconciler import LayoutNode
    from rc_tui.core import Element

    app = App(None, terminal=MockTerminal())

    # Build a tree where modal is the top window
    modal_button = LayoutNode(Element('button', {'text': 'OK'}))
    modal = LayoutNode(Element('modal', {}, [modal_button]))
    modal_button.parent = modal

    # Background window with another focusable element
    bg_input = LayoutNode(Element('input', {}))
    bg = LayoutNode(Element('box', {}, [bg_input]))
    bg_input.parent = bg

    # Set up window stack with modal on top
    app.windows = [
        {'element': None, 'node': bg},
        {'element': None, 'node': modal},
    ]
    app._clear_focus(bg)

    # Tab should only work within the modal
    app._cycle_focus(None)
    assert app.focused_node == modal_button, \
        f"Tab should focus modal button, got {app.focused_node.type if app.focused_node else None}"

    app.cleanup()
    print("test_modal_focus_trapping PASSED")


def test_normal_window_focus_untouched():
    from rc_tui import App
    from rc_tui.reconciler import LayoutNode
    from rc_tui.core import Element

    app = App(None, terminal=MockTerminal())

    btn1 = LayoutNode(Element('button', {'text': 'A'}))
    btn2 = LayoutNode(Element('button', {'text': 'B'}))
    root = LayoutNode(Element('box', {}, [btn1, btn2]))
    btn1.parent = root
    btn2.parent = root

    app.windows = [{'element': None, 'node': root}]
    app._clear_focus(root)

    app._cycle_focus(None)
    assert app.focused_node == btn1, "First Tab should focus btn1"

    app._cycle_focus(None)
    assert app.focused_node == btn2, "Second Tab should focus btn2"

    app.cleanup()
    print("test_normal_window_focus_untouched PASSED")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python tests/test_full_integration.py
```

Expected: Focus test fails because `_cycle_focus` doesn't check for modal windows.

- [ ] **Step 3: Write minimal implementation**

In `src/python/rc_tui/app.py`, modify `_cycle_focus()` at line 484. Replace the current function:

```python
def _cycle_focus(self, node):
    if self.windows:
        top_node = self.windows[-1].get('node')
        if top_node and top_node.type in ('dialog', 'modal'):
            node = top_node

    if node is None:
        return

    focusable_types = ('input', 'button', 'checkbox', 'radiobutton', 'switch', 'select', 'tabselect', 'textarea')

    all_focusable = []
    def collect(n):
        if n.type in focusable_types:
            all_focusable.append(n)
        for child in n.children:
            collect(child)
    collect(node)

    if not all_focusable: return

    current_idx = -1
    for i, n in enumerate(all_focusable):
        if n.is_focused:
            current_idx = i
            break

    self._clear_focus(node)
    next_idx = (current_idx + 1) % len(all_focusable)
    all_focusable[next_idx].is_focused = True
    self.focused_node = all_focusable[next_idx]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python tests/test_full_integration.py
```

Expected: Both focus tests print PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/python/rc_tui/app.py tests/test_full_integration.py
git commit -m "feat: trap focus within modal/dialog windows during Tab cycling"
```

---

### Task 5: StyleSheet.create validation

**Files:**
- Modify: `src/python/rc_tui/core.py` (~30 lines added to `StyleSheet.create`)
- Test: `tests/test_full_integration.py` (add test functions)

- [ ] **Step 1: Write the failing test**

Add to `tests/test_full_integration.py`:

```python
def test_stylesheet_create_valid():
    from rc_tui import StyleSheet

    styles = StyleSheet.create({
        'container': {
            'bg': (20, 20, 30),
            'padding': 2,
            'border': True,
            'bold': False,
        }
    })
    assert styles['container']['bg'] == (20, 20, 30)
    assert styles['container']['border'] is True
    print("test_stylesheet_create_valid PASSED")


def test_stylesheet_create_type_error():
    from rc_tui import StyleSheet
    import traceback

    try:
        StyleSheet.create({
            'bad_bool': {'border': 'yes'}
        })
        assert False, "Should have raised TypeError"
    except TypeError as e:
        assert "bool" in str(e).lower()
        print("test_stylesheet_create_type_error PASSED")


def test_stylesheet_create_warns_unknown():
    from rc_tui import StyleSheet
    import warnings

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        StyleSheet.create({
            'test': {'nonexistent_prop': 42}
        })
        assert len(w) >= 1, "Expected at least one warning"
        assert "unknown" in str(w[0].message).lower() or "nonexistent" in str(w[0].message).lower()
        print("test_stylesheet_create_warns_unknown PASSED")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python tests/test_full_integration.py
```

Expected: The type error test and warning test fail because `StyleSheet.create` doesn't validate.

- [ ] **Step 3: Write minimal implementation**

Replace `StyleSheet.create` in `src/python/rc_tui/core.py`:

```python
@staticmethod
def create(styles):
    RECOGNIZED = {
        'fg', 'bg', 'bold', 'italic', 'underline', 'strikethrough',
        'padding', 'margin', 'width', 'height', 'flex_grow', 'flex_direction',
        'gap', 'border', 'border_type', 'border_fg', 'border_bg',
        'hover_style', 'focus_style', 'tooltip',
        'text_transform', 'box_shadow',
        'align_items', 'justify_content',
        'padding_top', 'padding_bottom', 'padding_left', 'padding_right',
        'margin_top', 'margin_bottom', 'margin_left', 'margin_right',
        'title', 'color', 'bg_color', 'font_weight', 'text_align', 'font_family',
        'on_click', 'on_change', 'on_submit', 'on_key_down', 'on_scroll',
        'on_focus', 'on_blur', 'on_mouse_enter', 'on_mouse_leave',
        'key', 'ref', 'style', 'children', 'text',
        'scrollbar_style', 'scrollbar_track_style',
        'x', 'y', 'offset', 'count', 'language', 'content',
        'message', 'duration', 'dim',
        'label', 'checked', 'selected_index', 'options',
        'value', 'placeholder', 'type', 'on', 'min', 'max',
        'items', 'render_item', 'item_height',
        'columns', 'data',
        'font', 'size',
    }
    COLOR_PROPS = {'fg', 'bg', 'border_fg', 'border_bg', 'color', 'bg_color'}
    BOOL_PROPS = {'bold', 'italic', 'underline', 'strikethrough', 'border', 'dim'}
    INT_PROPS = {
        'padding', 'margin', 'gap',
        'padding_top', 'padding_bottom', 'padding_left', 'padding_right',
        'margin_top', 'margin_bottom', 'margin_left', 'margin_right',
        'width', 'height', 'flex_grow', 'x', 'y',
        'min', 'max', 'item_height', 'offset', 'count',
        'duration', 'selected_index',
    }

    for name, style in styles.items():
        if not isinstance(style, dict):
            raise TypeError(f"Style '{name}': expected dict, got {type(style).__name__}")
        for key, value in style.items():
            if key not in RECOGNIZED:
                import warnings
                warnings.warn(f"Style '{name}': unknown prop '{key}'")
            if key in BOOL_PROPS and not isinstance(value, bool):
                raise TypeError(f"Style '{name}.{key}': expected bool, got {type(value).__name__}")
            if key in INT_PROPS and value is not None and not isinstance(value, (int, float)):
                raise TypeError(f"Style '{name}.{key}': expected number, got {type(value).__name__}")

    return styles
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python tests/test_full_integration.py
```

Expected: All 3 StyleSheet tests print PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/python/rc_tui/core.py tests/test_full_integration.py
git commit -m "feat: add validation and warnings to StyleSheet.create"
```

---

## All tasks complete — final verification

- [ ] **Run all tests**

```bash
python tests/test_full_integration.py
```

Expected: All tests print PASSED, no assertion errors.

- [ ] **Final commit (version bump)**

```bash
git add -A && git commit -m "chore: bump version to v0.3.0"
git tag v0.3.0
```
