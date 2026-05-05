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
