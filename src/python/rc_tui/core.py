class StyleSheet:
    @staticmethod
    def create(styles):
        """
        Creates a StyleSheet object. Currently just returns the dict,
        but can be expanded for validation or performance (pre-processing).
        """
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
        self.state.update(state_update)
        if self.app:
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
