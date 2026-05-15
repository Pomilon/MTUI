from .layout import parse_dim as layout_parse_dim, get_spacing as layout_get_spacing

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
register('dialog', measure=_measure_dialog)
register('modal', measure=_measure_modal)


def dispatch_widget_click(type_name, node, event):
    handler = _CLICK.get(type_name)
    if handler:
        handler(node, event)


def dispatch_widget_key(type_name, node, event):
    handler = _KEY.get(type_name)
    if handler:
        handler(node, event)
