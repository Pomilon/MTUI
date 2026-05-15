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


if __name__ == "__main__":
    test_full_integration()
    test_button_keyboard_activation()
    test_button_keyboard_no_on_click()
    test_button_keyboard_activation_with_event()
