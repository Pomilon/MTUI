from .core import Element, Component, resolve_node_style

class LayoutNode:
    def __init__(self, element):
        self.element = element
        self.type = element.type
        self.props = resolve_node_style(element.props)
        self.children = []
        self.parent = None
        self.component = None
        self.key = element.props.get('key')
        
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.screen_x = 0
        self.screen_y = 0
        
        self.scroll_x = 0
        self.scroll_y = 0
        self.content_w = 0
        self.content_h = 0
        
        self.is_focused = False

class FunctionalComponentInstance:
    def __init__(self, func, props, app):
        self.func = func
        self.props = props
        self.app = app
        self._hooks = []
        self._root_node = None

    def render(self):
        from . import hooks
        prev_instance = hooks._current_instance
        prev_index = hooks._hook_index
        hooks._current_instance = self
        hooks._hook_index = 0
        try:
            res = self.func(self.props)
        finally:
            hooks._current_instance = prev_instance
            hooks._hook_index = prev_index
        return res

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

    def unmount(self):
        # Run all cleanups
        for hook in self._hooks:
            if hook.get("type") == "effect" and hook.get("cleanup"):
                try:
                    hook["cleanup"]()
                except Exception:
                    pass

def build_tree(element, app, old_node=None):
    if element is None:
        if old_node:
            _unmount_node(old_node)
        return None
        
    # Handle Component classes
    if isinstance(element.type, type) and issubclass(element.type, Component):
        if old_node and old_node.component and type(old_node.component) == element.type:
            comp = old_node.component
            comp.props = element.props
        else:
            if old_node and old_node.component:
                _unmount_node(old_node)
            comp = element.type(element.props)
            comp.app = app
            comp.component_did_mount()
            
        from . import hooks
        prev_instance = hooks._current_instance
        prev_index = hooks._hook_index
        hooks._current_instance = comp
        hooks._hook_index = 0
        try:
            rendered_element = comp.render()
        finally:
            hooks._current_instance = prev_instance
            hooks._hook_index = prev_index

        node = build_tree(rendered_element, app, old_node)
        node.component = comp
        comp._root_node = node
        return node
    
    # Handle Functional Components
    elif callable(element.type):
        if old_node and old_node.component and isinstance(old_node.component, FunctionalComponentInstance) and old_node.component.func == element.type:
            inst = old_node.component
            inst.props = element.props
        else:
            if old_node and old_node.component:
                _unmount_node(old_node)
            inst = FunctionalComponentInstance(element.type, element.props, app)
            
        rendered_element = inst.render()
        node = build_tree(rendered_element, app, old_node)
        node.component = inst
        inst._root_node = node
        return node
    
    # Handle Primitive Elements
    else:
        node = LayoutNode(element)
        
        # Key-based reconciliation
        old_children_by_key = {}
        old_children_ordered = []
        if old_node:
            for child in old_node.children:
                if child.key is not None:
                    old_children_by_key[child.key] = child
                else:
                    old_children_ordered.append(child)
        
        new_children = []
        for i, child_el in enumerate(element.children):
            key = child_el.props.get('key') if child_el is not None else None
            target_old_child = None
            
            if key is not None:
                if key in old_children_by_key:
                    target_old_child = old_children_by_key.pop(key)
            elif old_children_ordered:
                target_old_child = old_children_ordered.pop(0)
            
            child_node = build_tree(child_el, app, target_old_child)
            if child_node:
                child_node.parent = node
                new_children.append(child_node)
            
        # Unmount remaining old children
        for child in old_children_by_key.values():
            _unmount_node(child)
        for child in old_children_ordered:
            _unmount_node(child)
            
        node.children = new_children
            
        # Carry over state/focus for persistent primitives
        if old_node and old_node.type == element.type:
            node.is_focused = old_node.is_focused
            if node.is_focused:
                app.focused_node = node
                
            if element.type in ('input', 'textarea'):
                node.props['value'] = old_node.props.get('value', element.props.get('value', ''))
            
            if element.type == 'scrollbox':
                node.scroll_y = old_node.scroll_y
                node.scroll_x = old_node.scroll_x
                
        return node

def _unmount_node(node):
    if not node: return
    if node.component:
        if isinstance(node.component, Component):
            node.component.component_will_unmount()
        elif isinstance(node.component, FunctionalComponentInstance):
            node.component.unmount()
    for child in node.children:
        _unmount_node(child)
