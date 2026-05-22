class StyleSheet:
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
    BOOL_PROPS = {'bold', 'italic', 'underline', 'strikethrough', 'border', 'dim'}
    INT_PROPS = {
        'padding', 'margin', 'gap',
        'padding_top', 'padding_bottom', 'padding_left', 'padding_right',
        'margin_top', 'margin_bottom', 'margin_left', 'margin_right',
        'flex_grow', 'x', 'y',
        'min', 'max', 'item_height', 'offset', 'count',
        'duration', 'selected_index',
    }

    @staticmethod
    def create(styles):
        import warnings
        for name, style in styles.items():
            if not isinstance(style, dict):
                raise TypeError(f"Style '{name}': expected dict, got {type(style).__name__}")
            for key, value in style.items():
                if key not in StyleSheet.RECOGNIZED:
                    warnings.warn(f"Style '{name}': unknown prop '{key}'")
                if key in StyleSheet.BOOL_PROPS and not isinstance(value, bool):
                    raise TypeError(f"Style '{name}.{key}': expected bool, got {type(value).__name__}")
                if key in StyleSheet.INT_PROPS and value is not None and not isinstance(value, (int, float)):
                    raise TypeError(f"Style '{name}.{key}': expected number, got {type(value).__name__}")
        return styles

def resolve_node_style(props):
    """
    Resolves the final style for a node by merging the 'style' prop 
    (which can be a dict or list of dicts) with the rest of the props.
    Props defined directly on the element take precedence.
    """
    style_prop = props.get('style', {})
    
    # Start with resolved style
    resolved = {}
    
    if isinstance(style_prop, list):
        for s in style_prop:
            if isinstance(s, dict):
                resolved.update(s)
    elif isinstance(style_prop, dict):
        resolved.update(style_prop)
        
    # Merge with inline props (inline takes precedence)
    for k, v in props.items():
        if k != 'children':
            resolved[k] = v
            
    return resolved

class Element:
    def __init__(self, type_, props, children=None):
        self.type = type_
        self.props = props or {}
        self.children = children or []

class Component:
    def __init__(self, props=None):
        self.props = props or {}
        self.state = {}
        self.app = None
        self._root_node = None
        self._hooks = []

    def set_state(self, state_update):
        changed = False
        for k, v in state_update.items():
            if self.state.get(k) != v:
                self.state[k] = v
                changed = True
        if changed and self.app:
            self.app.request_render()

    def run_effect(self, idx):
        hook = self._hooks[idx]
        if "pending_effect" in hook:
            # Run cleanup of previous effect if it exists
            if hook["cleanup"]:
                try:
                    hook["cleanup"]()
                except Exception:
                    pass
            
            # Run new effect
            cleanup = hook["pending_effect"]()
            hook["cleanup"] = cleanup if callable(cleanup) else None
            hook["deps"] = hook["pending_deps"]
            del hook["pending_effect"]
            del hook["pending_deps"]

    def render(self):
        return Element('box', {})

    def component_did_mount(self):
        pass

    def component_will_unmount(self):
        # Run all hook cleanups
        for hook in self._hooks:
            if hook.get("type") == "effect" and hook.get("cleanup"):
                try:
                    hook["cleanup"]()
                except Exception:
                    pass
        pass
