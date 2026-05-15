from .layout import parse_dim as layout_parse_dim, get_spacing as layout_get_spacing
from . import tui_core

_MEASURE = {}
_DRAW = {}
_CLICK = {}
_KEY = {}


def _measure_text(node, max_w, max_h):
    text = str(node.props.get('text', ''))
    lines = text.split('\n')
    w = max((len(l) for l in lines), default=0)
    h = len(lines)
    return w, h


def _measure_span(node, max_w, max_h):
    return _measure_text(node, max_w, max_h)


def _measure_input(node, max_w, max_h):
    w_prop = node.props.get('width')
    h_prop = node.props.get('height')
    (pt, pb, pl, pr), (mt, mb, ml, mr) = layout_get_spacing(node)
    w = layout_parse_dim(w_prop, max_w) if w_prop is not None else (max_w if max_w is not None else 20)
    h = layout_parse_dim(h_prop, max_h) if h_prop is not None else 1
    return w + pl + pr + ml + mr, h + pt + pb + mt + mb


def _measure_textarea(node, max_w, max_h):
    w_prop = node.props.get('width')
    h_prop = node.props.get('height')
    (pt, pb, pl, pr), (mt, mb, ml, mr) = layout_get_spacing(node)
    w = layout_parse_dim(w_prop, max_w) if w_prop is not None else (max_w if max_w is not None else 20)
    h = layout_parse_dim(h_prop, max_h) if h_prop is not None else 5
    return w + pl + pr + ml + mr, h + pt + pb + mt + mb


def _measure_progressbar(node, max_w, max_h):
    w_prop = node.props.get('width')
    h_prop = node.props.get('height')
    (pt, pb, pl, pr), (mt, mb, ml, mr) = layout_get_spacing(node)
    w = layout_parse_dim(w_prop, max_w) if w_prop is not None else (max_w if max_w is not None else 20)
    h = layout_parse_dim(h_prop, max_h) if h_prop is not None else 1
    return w + pl + pr + ml + mr, h + pt + pb + mt + mb


def _measure_button(node, max_w, max_h):
    w_prop = node.props.get('width')
    h_prop = node.props.get('height')
    text = str(node.props.get('text', ''))
    (pt, pb, pl, pr), (mt, mb, ml, mr) = layout_get_spacing(node)
    w = layout_parse_dim(w_prop, max_w) if w_prop is not None else (len(text) + 4)
    h = layout_parse_dim(h_prop, max_h) if h_prop is not None else 1
    return w + pl + pr + ml + mr, h + pt + pb + mt + mb


def _measure_checkbox(node, max_w, max_h):
    w_prop = node.props.get('width')
    h_prop = node.props.get('height')
    label = str(node.props.get('label', ''))
    (pt, pb, pl, pr), (mt, mb, ml, mr) = layout_get_spacing(node)
    w = layout_parse_dim(w_prop, max_w) if w_prop is not None else (len(label) + 4)
    h = layout_parse_dim(h_prop, max_h) if h_prop is not None else 1
    return w + pl + pr + ml + mr, h + pt + pb + mt + mb


def _measure_divider(node, max_w, max_h):
    w = max_w if max_w is not None else 1
    return w, 1


def _measure_radiobutton(node, max_w, max_h):
    w_prop = node.props.get('width')
    label = str(node.props.get('label', ''))
    (pt, pb, pl, pr), (mt, mb, ml, mr) = layout_get_spacing(node)
    w = layout_parse_dim(w_prop, max_w) if w_prop is not None else (len(label) + 4)
    return w + ml + mr, 1 + mt + mb


def _measure_switch(node, max_w, max_h):
    w_prop = node.props.get('width')
    label = str(node.props.get('label', ''))
    (pt, pb, pl, pr), (mt, mb, ml, mr) = layout_get_spacing(node)
    w = layout_parse_dim(w_prop, max_w) if w_prop is not None else (len(label) + 10)
    return w + ml + mr, 1 + mt + mb


def _measure_select(node, max_w, max_h):
    w_prop = node.props.get('width')
    options = node.props.get('options', [])
    max_opt_w = max((len(str(o)) for o in options), default=0)
    (pt, pb, pl, pr), (mt, mb, ml, mr) = layout_get_spacing(node)
    w = layout_parse_dim(w_prop, max_w) if w_prop is not None else (max_opt_w + 6)
    return w + pl + pr + ml + mr, 1 + pt + pb + mt + mb


def _measure_tabselect(node, max_w, max_h):
    options = node.props.get('options', [])
    (pt, pb, pl, pr), (mt, mb, ml, mr) = layout_get_spacing(node)
    total_w = sum(len(str(o)) + 4 for o in options)
    return total_w + ml + mr, 1 + mt + mb


def _measure_code(node, max_w, max_h):
    w_prop = node.props.get('width')
    h_prop = node.props.get('height')
    (pt, pb, pl, pr), (mt, mb, ml, mr) = layout_get_spacing(node)
    w = layout_parse_dim(w_prop, max_w) if w_prop is not None else (max_w if max_w is not None else 40)
    h = layout_parse_dim(h_prop, max_h) if h_prop is not None else 10
    return w + ml + mr, h + mt + mb


def _measure_diff(node, max_w, max_h):
    return _measure_code(node, max_w, max_h)


def _measure_markdown(node, max_w, max_h):
    w_prop = node.props.get('width')
    h_prop = node.props.get('height')
    content = str(node.props.get('content', ''))
    (pt, pb, pl, pr), (mt, mb, ml, mr) = layout_get_spacing(node)
    w = layout_parse_dim(w_prop, max_w) if w_prop is not None else (max_w if max_w is not None else 40)
    h = layout_parse_dim(h_prop, max_h) if h_prop is not None else len(content.split('\n')) + 2
    return w + ml + mr, h + mt + mb


def _measure_linenumber(node, max_w, max_h):
    count = node.props.get('count', 0)
    w = len(str(count)) + 2
    return w, 1


def _measure_asciifont(node, max_w, max_h):
    w_prop = node.props.get('width')
    (pt, pb, pl, pr), (mt, mb, ml, mr) = layout_get_spacing(node)
    return (max_w or 40) + ml + mr, 5 + mt + mb


def _measure_toast(node, max_w, max_h):
    message = str(node.props.get('message', ''))
    w = len(message) + 4
    return w, 3


def _measure_dialog(node, max_w, max_h):
    w_prop = node.props.get('width')
    h_prop = node.props.get('height')
    w = layout_parse_dim(w_prop, max_w) if w_prop is not None else (max_w // 2 if max_w else 40)
    h = layout_parse_dim(h_prop, max_h) if h_prop is not None else (max_h // 2 if max_h else 10)
    return w, h


def _measure_modal(node, max_w, max_h):
    return _measure_dialog(node, max_w, max_h)


def _draw_text(node, canvas, style):
    text = str(node.props.get('text', ''))
    tt = node.props.get('text_transform')
    if tt == 'uppercase': text = text.upper()
    elif tt == 'lowercase': text = text.lower()
    elif tt == 'capitalize': text = text.capitalize()
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if node.screen_y + i < node.screen_y + node.h:
            canvas.draw_text(node.screen_x, node.screen_y + i, line[:node.w], style)


def _draw_tabselect(node, canvas, style):
    options = node.props.get('options', [])
    selected_idx = node.props.get('selected_index', 0)
    curr_x = node.screen_x
    for i, opt in enumerate(options):
        is_sel = (i == selected_idx)
        text = f" {opt} "
        tab_style = tui_core.Style(style.fg_r, style.fg_g, style.fg_b, style.bg_r, style.bg_g, style.bg_b, style.bold, style.italic, style.underline, style.strikethrough)
        if is_sel:
            tab_style.bg_r, tab_style.bg_g, tab_style.bg_b = 60, 60, 80
            tab_style.bold = True
        if curr_x + len(text) <= node.screen_x + node.w:
            canvas.draw_text(curr_x, node.screen_y, text, tab_style)
        curr_x += len(text) + 1


def _draw_textarea(node, canvas, style):
    val = str(node.props.get('value', ''))
    lines = val.split('\n')
    scroll_y = node.scroll_y if hasattr(node, 'scroll_y') else 0
    for i, line in enumerate(lines[scroll_y:scroll_y + node.h]):
        canvas.draw_text(node.screen_x, node.screen_y + i, line[:node.w], style)
    if node.is_focused:
        cursor_x = node.props.get('cursor_x', 0)
        cursor_y = node.props.get('cursor_y', 0)
        vis_y = cursor_y - scroll_y
        if 0 <= vis_y < node.h:
            display_x = min(cursor_x, node.w - 1)
            canvas.draw_text(node.screen_x + display_x, node.screen_y + vis_y, '_', style)


def _draw_code(node, canvas, style):
    import tree_sitter_python as tspython
    from tree_sitter import Language, Parser
    content = str(node.props.get('content', ''))
    try:
        lang = Language(tspython.language())
        parser = Parser(lang)
        tree = parser.parse(content.encode('utf-8'))

        color_map = {
            'def': (200, 100, 200),
            'class': (200, 100, 200),
            'return': (200, 100, 200),
            'import': (200, 100, 200),
            'from': (200, 100, 200),
            'if': (200, 100, 200),
            'else': (200, 100, 200),
            'elif': (200, 100, 200),
            'for': (200, 100, 200),
            'while': (200, 100, 200),
            'try': (200, 100, 200),
            'except': (200, 100, 200),
            'with': (200, 100, 200),
            'as': (200, 100, 200),
            'lambda': (200, 100, 200),
            'pass': (200, 100, 200),
            'in': (200, 100, 200),
            'is': (200, 100, 200),
            'not': (200, 100, 200),
            'and': (200, 100, 200),
            'or': (200, 100, 200),
            'string': (100, 200, 100),
            'integer': (200, 200, 100),
            'float': (200, 200, 100),
            'comment': (120, 120, 120),
            'identifier': (100, 200, 255),
            'function_definition': (100, 200, 255),
            'attribute': (255, 180, 100),
            'keyword_argument': (255, 150, 100),
        }

        highlights = {}
        def traverse(ts_node):
            if not ts_node.children or ts_node.type in ('string', 'comment'):
                if ts_node.type in color_map:
                    for i in range(ts_node.start_byte, ts_node.end_byte):
                        highlights[i] = color_map[ts_node.type]
            for child in ts_node.children:
                traverse(child)

        traverse(tree.root_node)

        lines = content.split('\n')
        byte_idx = 0
        for i, line in enumerate(lines[:node.h]):
            curr_x = node.screen_x
            for char in line:
                char_style = tui_core.Style(style.fg_r, style.fg_g, style.fg_b, style.bg_r, style.bg_g, style.bg_b, style.bold)
                if byte_idx in highlights:
                    r, g, b = highlights[byte_idx]
                    char_style.fg_r, char_style.fg_g, char_style.fg_b = r, g, b
                if curr_x < node.screen_x + node.w:
                    canvas.set_cell(curr_x, node.screen_y + i, char, char_style)
                curr_x += 1
                byte_idx += len(char.encode('utf-8'))
            byte_idx += 1
    except Exception:
        for i, line in enumerate(content.split('\n')[:node.h]):
            canvas.draw_text(node.screen_x, node.screen_y + i, line[:node.w], style)


def _draw_diff(node, canvas, style):
    content = str(node.props.get('content', ''))
    lines = content.split('\n')
    for i, line in enumerate(lines[:node.h]):
        line_style = tui_core.Style(style.fg_r, style.fg_g, style.fg_b, style.bg_r, style.bg_g, style.bg_b, style.bold, style.italic, style.underline, style.strikethrough)
        if line.startswith('+'):
            line_style.fg_r, line_style.fg_g, line_style.fg_b = 100, 255, 100
        elif line.startswith('-'):
            line_style.fg_r, line_style.fg_g, line_style.fg_b = 255, 100, 100
        canvas.draw_text(node.screen_x, node.screen_y + i, line[:node.w], line_style)


def _draw_asciifont(node, canvas, style):
    import pyfiglet
    text = str(node.props.get('text', ''))
    font = node.props.get('font', 'slant')
    try:
        f = pyfiglet.Figlet(font=font)
        rendered = f.renderText(text)
        lines = rendered.split('\n')
        for i, line in enumerate(lines[:node.h]):
            canvas.draw_text(node.screen_x, node.screen_y + i, line[:node.w], style)
    except:
        canvas.draw_text(node.screen_x, node.screen_y, text[:node.w], style)


def _draw_markdown(node, canvas, style):
    content = str(node.props.get('content', ''))
    cx, cy, cw, ch = canvas.clip_rect
    canvas.buffer.draw_markdown(node.screen_x, node.screen_y, node.w, node.h, content, style, cx, cy, cw, ch)


def _draw_linenumber(node, canvas, style):
    count = node.props.get('count', 0)
    num_style = tui_core.Style(style.fg_r, style.fg_g, style.fg_b, style.bg_r, style.bg_g, style.bg_b, style.bold, style.italic, style.underline, style.strikethrough)
    num_style.fg_r = num_style.fg_g = num_style.fg_b = 100
    for i in range(node.h):
        canvas.draw_text(node.screen_x, node.screen_y + i, str(i+1).rjust(node.w-1), num_style)


def _draw_radiobutton(node, canvas, style):
    label = str(node.props.get('label', ''))
    selected = node.props.get('selected', False)
    icon = "◉" if selected else "○"
    rb_style = tui_core.Style(style.fg_r, style.fg_g, style.fg_b, style.bg_r, style.bg_g, style.bg_b, style.bold, style.italic, style.underline, style.strikethrough)
    if node.is_focused:
        rb_style.fg_r, rb_style.fg_g, rb_style.fg_b = 0, 255, 255
    canvas.draw_text(node.screen_x, node.screen_y, f"{icon} {label}"[:node.w], rb_style)


def _draw_switch(node, canvas, style):
    label = str(node.props.get('label', ''))
    on = node.props.get('on', False)
    sw_text = "[ON ]" if on else "[OFF]"
    sw_style = tui_core.Style(style.fg_r, style.fg_g, style.fg_b, style.bg_r, style.bg_g, style.bg_b, style.bold, style.italic, style.underline, style.strikethrough)

    state_style = tui_core.Style(sw_style.fg_r, sw_style.fg_g, sw_style.fg_b, sw_style.bg_r, sw_style.bg_g, sw_style.bg_b, sw_style.bold, sw_style.italic, sw_style.underline, sw_style.strikethrough)
    if on:
        state_style.fg_r, state_style.fg_g, state_style.fg_b = 0, 255, 0
    else:
        state_style.fg_r, state_style.fg_g, state_style.fg_b = 255, 0, 0

    if node.is_focused:
        sw_style.fg_r, sw_style.fg_g, sw_style.fg_b = 0, 255, 255

    canvas.draw_text(node.screen_x, node.screen_y, sw_text, state_style)
    if label:
        canvas.draw_text(node.screen_x + len(sw_text) + 1, node.screen_y, label[:node.w - len(sw_text) - 1], sw_style)


def _draw_divider(node, canvas, style):
    canvas.draw_text(node.screen_x, node.screen_y, "─" * node.w, style)


def _draw_button(node, canvas, style):
    text = str(node.props.get('text', ''))
    btn_style = tui_core.Style(style.fg_r, style.fg_g, style.fg_b, style.bg_r, style.bg_g, style.bg_b, style.bold, style.italic, style.underline, style.strikethrough)
    if node.is_focused:
        btn_style.bg_r, btn_style.bg_g, btn_style.bg_b = 0, 100, 100
    canvas.fill_rect(node.screen_x, node.screen_y, node.w, node.h, btn_style)
    label_x = node.screen_x + (node.w - len(text)) // 2
    canvas.draw_text(max(node.screen_x, label_x), node.screen_y, text[:node.w], btn_style)


def _draw_checkbox(node, canvas, style):
    label = str(node.props.get('label', ''))
    checked = node.props.get('checked', False)
    box = "[x]" if checked else "[ ]"
    check_style = tui_core.Style(style.fg_r, style.fg_g, style.fg_b, style.bg_r, style.bg_g, style.bg_b, style.bold, style.italic, style.underline, style.strikethrough)
    if node.is_focused:
        check_style.fg_r, check_style.fg_g, check_style.fg_b = 0, 255, 255
    canvas.draw_text(node.screen_x, node.screen_y, f"{box} {label}"[:node.w], check_style)


def _draw_progressbar(node, canvas, style):
    progress = max(0.0, min(1.0, node.props.get('progress', 0.0)))
    bar_style = tui_core.Style(style.fg_r, style.fg_g, style.fg_b, style.bg_r, style.bg_g, style.bg_b, style.bold, style.italic, style.underline, style.strikethrough)

    width = node.w
    if width < 3:
        canvas.draw_text(node.screen_x, node.screen_y, "█" * width, bar_style)
    else:
        inner_w = width - 2
        filled_w = int(inner_w * progress)
        empty_w = inner_w - filled_w

        canvas.draw_text(node.screen_x, node.screen_y, "[", bar_style)
        if filled_w > 0:
            canvas.draw_text(node.screen_x + 1, node.screen_y, "█" * filled_w, bar_style)
        if empty_w > 0:
            canvas.draw_text(node.screen_x + 1 + filled_w, node.screen_y, " " * empty_w, bar_style)
        canvas.draw_text(node.screen_x + width - 1, node.screen_y, "]", bar_style)


def _draw_input(node, canvas, style):
    val = node.props.get('value', '')
    ph = node.props.get('placeholder', 'Type here...')
    display = val if val else ph
    input_style = tui_core.Style(style.fg_r, style.fg_g, style.fg_b, style.bg_r, style.bg_g, style.bg_b, style.bold, style.italic, style.underline, style.strikethrough)
    if node.is_focused:
        input_style.fg_r, input_style.fg_g, input_style.fg_b = 0, 255, 255
    off = 1 if node.props.get('border') else 0
    canvas.draw_text(node.screen_x + off, node.screen_y + off, display[:node.w-(off*2)], input_style)
    if node.is_focused:
        cursor_pos = len(val)
        if cursor_pos < node.w - (off * 2):
            canvas.draw_text(node.screen_x + off + cursor_pos, node.screen_y + off, "_", input_style)


def _click_tabselect(node, event, app):
    options = node.props.get('options', [])
    relative_x = event.x - node.screen_x
    curr_x = 0
    for i, opt in enumerate(options):
        tab_w = len(str(opt)) + 3
        if curr_x <= relative_x < curr_x + tab_w:
            on_change = node.props.get('on_change')
            if on_change:
                on_change(i)
            return True
        curr_x += tab_w
    return False


def _click_select(node, event, app):
    app._open_select_menu(node)
    return True


def _click_checkbox(node, event, app):
    on_change = node.props.get('on_change')
    if on_change:
        on_change(not node.props.get('checked', False))
    return True


def _click_radiobutton(node, event, app):
    on_change = node.props.get('on_change')
    if on_change:
        on_change(True)
    return True


def _click_scrollbox(node, event, app):
    if event.x == node.screen_x + node.w - 1 and node.content_h > node.h:
        track_h = node.h
        rel_y = event.y - node.screen_y
        ratio = rel_y / track_h
        max_scroll = max(0, node.content_h - node.h)
        node.scroll_y = int(ratio * max_scroll)
        on_scroll = node.props.get('on_scroll')
        if on_scroll:
            on_scroll(node.scroll_y, node.h)
        return True
    return False


def _click_switch(node, event, app):
    on_change = node.props.get('on_change')
    if on_change:
        on_change(not node.props.get('on', False))
    return True


def _key_tabselect(node, event):
    if event.key in ('LEFT', 'RIGHT', ' ', 'ENTER'):
        on_change = node.props.get('on_change')
        if on_change:
            opts = node.props.get('options', [])
            idx = node.props.get('selected_index', 0)
            if event.key in ('RIGHT', ' ', 'ENTER'):
                on_change((idx + 1) % len(opts) if opts else 0)
            elif event.key == 'LEFT':
                on_change((idx - 1) % len(opts) if opts else 0)
        return True
    return False


def _key_select(node, event):
    if event.key in (' ', 'ENTER', 'DOWN', 'UP'):
        return False  # Handled in app.py (needs app access)
    return False


def _key_checkbox(node, event):
    if event.key in (' ', 'ENTER'):
        on_change = node.props.get('on_change')
        if on_change:
            on_change(not node.props.get('checked', False))
        return True
    return False


def _key_radiobutton(node, event):
    if event.key in (' ', 'ENTER'):
        on_change = node.props.get('on_change')
        if on_change:
            on_change(True)
        return True
    return False


def _key_switch(node, event):
    if event.key in (' ', 'ENTER'):
        on_change = node.props.get('on_change')
        if on_change:
            on_change(not node.props.get('on', False))
        return True
    return False


def _key_input(node, event):
    val = node.props.get('value', '')
    if event.key == 'BACKSPACE':
        if val:
            val = val[:-1]
    elif event.key == 'ENTER':
        on_submit = node.props.get('on_submit')
        if on_submit:
            on_submit(val)
            return True
    elif len(event.key) == 1:
        val += event.key
    else:
        return False

    if val != node.props.get('value'):
        node.props['value'] = val
        on_change = node.props.get('on_change')
        if on_change:
            on_change(val)
    return True


def _key_textarea(node, event):
    val = str(node.props.get('value', ''))
    lines = val.split('\n')
    cursor_x = node.props.get('cursor_x', len(lines[-1]) if lines else 0)
    cursor_y = node.props.get('cursor_y', max(0, len(lines) - 1))

    if event.key == 'LEFT':
        if cursor_x > 0:
            cursor_x -= 1
        elif cursor_y > 0:
            cursor_y -= 1
            cursor_x = len(lines[cursor_y])
    elif event.key == 'RIGHT':
        if cursor_x < len(lines[cursor_y]):
            cursor_x += 1
        elif cursor_y < len(lines) - 1:
            cursor_y += 1
            cursor_x = 0
    elif event.key == 'UP' and cursor_y > 0:
        cursor_y -= 1
        cursor_x = min(cursor_x, len(lines[cursor_y]))
    elif event.key == 'DOWN' and cursor_y < len(lines) - 1:
        cursor_y += 1
        cursor_x = min(cursor_x, len(lines[cursor_y]))
    elif event.key == 'HOME':
        cursor_x = 0
    elif event.key == 'END':
        cursor_x = len(lines[cursor_y])
    elif event.key == 'BACKSPACE':
        if cursor_x > 0:
            line = lines[cursor_y]
            lines[cursor_y] = line[:cursor_x - 1] + line[cursor_x:]
            cursor_x -= 1
            val = '\n'.join(lines)
        elif cursor_y > 0:
            prev_line = lines[cursor_y - 1]
            cursor_x = len(prev_line)
            lines[cursor_y - 1] = prev_line + lines[cursor_y]
            del lines[cursor_y]
            cursor_y -= 1
            val = '\n'.join(lines)
    elif event.key == 'ENTER':
        line = lines[cursor_y]
        lines[cursor_y] = line[:cursor_x]
        lines.insert(cursor_y + 1, line[cursor_x:])
        cursor_y += 1
        cursor_x = 0
        val = '\n'.join(lines)
    elif len(event.key) == 1:
        line = lines[cursor_y]
        lines[cursor_y] = line[:cursor_x] + event.key + line[cursor_x:]
        cursor_x += 1
        val = '\n'.join(lines)
    else:
        return False

    node.props['value'] = val
    node.props['cursor_x'] = cursor_x
    node.props['cursor_y'] = cursor_y

    on_change = node.props.get('on_change')
    if on_change:
        on_change(val)
    return True


def _key_button(node, event):
    if event.key in (' ', 'ENTER'):
        on_click = node.props.get('on_click')
        if on_click:
            try:
                on_click(event)
            except TypeError:
                try:
                    on_click()
                except Exception as e:
                    pass
            except Exception as e:
                pass
        return True
    return False


def register(type_name, *, measure=None, draw=None, on_click=None, on_key=None):
    if measure:
        _MEASURE[type_name] = measure
    if draw:
        _DRAW[type_name] = draw
    if on_click:
        _CLICK[type_name] = on_click
    if on_key:
        _KEY[type_name] = on_key


register('text', measure=_measure_text)
register('span', measure=_measure_span)
register('input', measure=_measure_input)
register('textarea', measure=_measure_textarea)
register('progressbar', measure=_measure_progressbar)
register('button', measure=_measure_button)
register('checkbox', measure=_measure_checkbox)
register('divider', measure=_measure_divider)
register('radiobutton', measure=_measure_radiobutton)
register('switch', measure=_measure_switch)
register('select', measure=_measure_select)
register('tabselect', measure=_measure_tabselect)
register('code', measure=_measure_code)
register('diff', measure=_measure_diff)
register('markdown', measure=_measure_markdown)
register('linenumber', measure=_measure_linenumber)
register('asciifont', measure=_measure_asciifont)
register('toast', measure=_measure_toast)


register('text', draw=_draw_text)
register('span', draw=_draw_text)
register('tabselect', draw=_draw_tabselect)
register('textarea', draw=_draw_textarea)
register('code', draw=_draw_code)
register('diff', draw=_draw_diff)
register('asciifont', draw=_draw_asciifont)
register('markdown', draw=_draw_markdown)
register('linenumber', draw=_draw_linenumber)
register('radiobutton', draw=_draw_radiobutton)
register('switch', draw=_draw_switch)
register('divider', draw=_draw_divider)
register('button', draw=_draw_button)
register('checkbox', draw=_draw_checkbox)
register('progressbar', draw=_draw_progressbar)
register('input', draw=_draw_input)

# Click handlers
register('tabselect', on_click=_click_tabselect)
register('select', on_click=_click_select)
register('checkbox', on_click=_click_checkbox)
register('radiobutton', on_click=_click_radiobutton)
register('switch', on_click=_click_switch)
register('scrollbox', on_click=_click_scrollbox)

# Key handlers
register('tabselect', on_key=_key_tabselect)
register('select', on_key=_key_select)
register('checkbox', on_key=_key_checkbox)
register('radiobutton', on_key=_key_radiobutton)
register('switch', on_key=_key_switch)
register('input', on_key=_key_input)
register('textarea', on_key=_key_textarea)
register('button', on_key=_key_button)


def dispatch_widget_click(type_name, node, event, app):
    handler = _CLICK.get(type_name)
    if handler:
        return handler(node, event, app)
    return False


def dispatch_widget_key(type_name, node, event):
    handler = _KEY.get(type_name)
    if handler:
        return handler(node, event)
    return False
