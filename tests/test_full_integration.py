import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/python')))

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

if __name__ == "__main__":
    test_full_integration()
