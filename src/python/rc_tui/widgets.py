_MEASURE = {}
_DRAW = {}
_CLICK = {}
_KEY = {}

def register(type_name, *, measure=None, draw=None, on_click=None, on_key=None):
    if measure:
        _MEASURE[type_name] = measure
    if draw:
        _DRAW[type_name] = draw
    if on_click:
        _CLICK[type_name] = on_click
    if on_key:
        _KEY[type_name] = on_key

def dispatch_widget_click(type_name, node, event):
    handler = _CLICK.get(type_name)
    if handler:
        handler(node, event)

def dispatch_widget_key(type_name, node, event):
    handler = _KEY.get(type_name)
    if handler:
        handler(node, event)
