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


def test_modal_focus_trapping():
    from rc_tui import App
    from rc_tui.reconciler import LayoutNode
    from rc_tui.core import Element

    app = App(None, terminal=MockTerminal())

    modal_button = LayoutNode(Element('button', {'text': 'OK'}))
    modal = LayoutNode(Element('modal', {}, [modal_button]))
    modal_button.parent = modal
    modal.children = [modal_button]

    bg_input = LayoutNode(Element('input', {}))
    bg = LayoutNode(Element('box', {}, [bg_input]))
    bg_input.parent = bg

    app.windows = [
        {'element': None, 'node': bg},
        {'element': None, 'node': modal},
    ]
    app._clear_focus(bg)

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
    root.children = [btn1, btn2]

    app.windows = [{'element': None, 'node': root}]
    app._clear_focus(root)

    app._cycle_focus(None)
    assert app.focused_node == btn1, "First Tab should focus btn1"

    app._cycle_focus(None)
    assert app.focused_node == btn2, "Second Tab should focus btn2"

    app.cleanup()
    print("test_normal_window_focus_untouched PASSED")


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


def test_widget_registry():
    from rc_tui.widgets import register, _MEASURE, _DRAW, _CLICK, _KEY

    register('test_widget', measure=lambda n, mw, mh: (10, 5))
    assert 'test_widget' in _MEASURE
    assert _MEASURE['test_widget'](None, 100, 50) == (10, 5)
    print("test_widget_registry PASSED")


def test_widget_dispatch_integration():
    from rc_tui.widgets import register, dispatch_widget_click, dispatch_widget_key
    from rc_tui.input import KeyEvent

    results = []
    register('test_click', on_click=lambda n, e, app: results.append('click'))
    register('test_key', on_key=lambda n, e: results.append(f"key_{e.key}"))

    dispatch_widget_click('test_click', None, None, None)
    assert results == ['click'], f"Expected ['click'], got {results}"

    dispatch_widget_key('test_key', None, KeyEvent('ENTER'))
    assert results == ['click', 'key_ENTER'], f"Expected ['click', 'key_ENTER'], got {results}"

    dispatch_widget_click('unknown_type', None, None, None)
    dispatch_widget_key('unknown_type', None, KeyEvent('x'))
    assert results == ['click', 'key_ENTER'], "Unknown types should be no-ops"

    print("test_widget_dispatch_integration PASSED")


def test_textarea_cursor_navigation():
    from rc_tui.reconciler import LayoutNode
    from rc_tui.core import Element
    from rc_tui.widgets import _KEY
    from rc_tui.input import KeyEvent

    ta = LayoutNode(Element('textarea', {'value': 'abc\ndef\nghi'}))
    ta.props['cursor_x'] = 1
    ta.props['cursor_y'] = 1

    _KEY['textarea'](ta, KeyEvent('RIGHT'))
    assert ta.props.get('cursor_x') == 2, f"Expected cursor_x=2, got {ta.props.get('cursor_x')}"
    assert ta.props.get('cursor_y') == 1

    _KEY['textarea'](ta, KeyEvent('DOWN'))
    assert ta.props['cursor_y'] == 2, f"Expected cursor_y=2"
    assert ta.props['cursor_x'] == min(2, len('ghi')), f"cursor_x should clamp to line len"

    _KEY['textarea'](ta, KeyEvent('UP'))
    assert ta.props['cursor_y'] == 1, f"Expected cursor_y=1"

    _KEY['textarea'](ta, KeyEvent('HOME'))
    assert ta.props['cursor_x'] == 0, f"Expected cursor_x=0 after HOME"

    print("test_textarea_cursor_navigation PASSED")


def test_textarea_insert_at_cursor():
    from rc_tui.reconciler import LayoutNode
    from rc_tui.core import Element
    from rc_tui.widgets import _KEY
    from rc_tui.input import KeyEvent

    ta = LayoutNode(Element('textarea', {'value': 'hello'}))
    ta.props['cursor_x'] = 2
    ta.props['cursor_y'] = 0

    _KEY['textarea'](ta, KeyEvent('X'))
    assert ta.props.get('value') == 'heXllo', f"Expected 'heXllo', got {ta.props.get('value')}"
    assert ta.props['cursor_x'] == 3

    _KEY['textarea'](ta, KeyEvent('HOME'))
    _KEY['textarea'](ta, KeyEvent('A'))
    assert ta.props.get('value') == 'AheXllo'

    print("test_textarea_insert_at_cursor PASSED")


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
    test_modal_focus_trapping()
    test_normal_window_focus_untouched()
    test_stylesheet_create_valid()
    test_stylesheet_create_type_error()
    test_stylesheet_create_warns_unknown()
    test_widget_registry()
    test_widget_dispatch_integration()
    test_textarea_cursor_navigation()
    test_textarea_insert_at_cursor()
