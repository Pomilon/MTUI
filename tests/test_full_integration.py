from rc_tui import Box, Text, StyleSheet, Button, useState
from rc_tui.core import resolve_node_style

# We'll use a unit-test style verification since we can't interact with a TUI here
def test_full_integration():
    styles = StyleSheet.create({
        'container': {
            'flex_direction': 'column',
            'bg': (20, 20, 30),
            'padding': 2,
            'border': True
        },
        'header': {
            'fg': (0, 255, 255),
            'bold': True
        },
        'button_base': {
            'bg': (0, 100, 0),
            'padding_left': 2
        },
        'button_active': {
            'bg': (0, 200, 0),
            'bold': True
        }
    })

    def UserCard(name, role):
        # Emulating what the reconciler would do
        props = {'style': styles['container'], 'title': name}
        resolved = resolve_node_style(props)
        return resolved

    # 1. Verify custom component prop merging
    card_props = UserCard("Alice", "Admin")
    assert card_props['bg'] == (20, 20, 30)
    assert card_props['title'] == "Alice"
    assert card_props['padding'] == 2
    assert card_props['border'] is True

    # 2. Verify conditional style arrays
    count = 1
    btn_props = {'style': [styles['button_base'], styles['button_active'] if count % 2 == 1 else {}], 'text': 'Click'}
    resolved_btn = resolve_node_style(btn_props)
    assert resolved_btn['bg'] == (0, 200, 0)
    assert resolved_btn['bold'] is True
    assert resolved_btn['padding_left'] == 2

    count = 2
    btn_props = {'style': [styles['button_base'], styles['button_active'] if count % 2 == 1 else {}], 'text': 'Click'}
    resolved_btn = resolve_node_style(btn_props)
    assert resolved_btn['bg'] == (0, 100, 0)
    assert resolved_btn.get('bold') is None or resolved_btn['bold'] is False
    assert resolved_btn['padding_left'] == 2

    print("Full integration verification passed!")

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

    app.dispatch_event(KeyEvent(' '))
    assert len(click_log) == 1, f"Expected 1 click after SPACE, got {len(click_log)}"

    app.dispatch_event(KeyEvent('ENTER'))
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

    app.dispatch_event(KeyEvent(' '))
    app.dispatch_event(KeyEvent('ENTER'))
    app.cleanup()
    print("test_button_keyboard_no_on_click PASSED")


def test_button_keyboard_activation_with_event():
    from rc_tui import App
    from rc_tui.reconciler import LayoutNode
    from rc_tui.core import Element
    from rc_tui.input import KeyEvent

    received = []
    app = App(None, terminal=MockTerminal())
    button = LayoutNode(Element('button', {'on_click': lambda e: received.append(e.key)}))
    button.is_focused = True
    app.focused_node = button
    app.windows[-1]['node'] = button

    app.dispatch_event(KeyEvent(' '))
    assert len(received) == 1, f"Expected 1 event, got {len(received)}"
    assert received[0] == ' ', f"Expected key=' ', got '{received[0]}'"

    app.dispatch_event(KeyEvent('ENTER'))
    assert len(received) == 2, f"Expected 2 events, got {len(received)}"
    assert received[1] == 'ENTER', f"Expected key='ENTER', got '{received[1]}'"

    app.cleanup()
    print("test_button_keyboard_activation_with_event PASSED")


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
    child = LayoutNode(Element('text', {'text': 'Hello\n\n'}))
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
    child = LayoutNode(Element('text', {'text': 'Hello\n\n'}))
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
    # remaining cross-axis = inner_h - ch = 10 - 1 = 9, offset = 9/2 = 4
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


if __name__ == "__main__":
    test_full_integration()
    test_button_keyboard_activation()
    test_button_keyboard_no_on_click()
    test_button_keyboard_activation_with_event()
    test_justify_content_center()
    test_justify_content_flex_end()
    test_align_items_center()
    test_justify_content_flex_start_default()
    test_ref_wired_to_layout_node()
    test_ref_no_op_when_absent()
