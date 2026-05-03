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

    def set_state(self, state_update):
        self.state.update(state_update)
        if self.app:
            self.app.request_render()

    def render(self):
        return Element('box', {})

    def component_did_mount(self):
        pass

    def component_will_unmount(self):
        pass
