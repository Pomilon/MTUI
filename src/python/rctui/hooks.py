import time

_current_instance = None
_hook_index = 0

def useState(initial_val):
    global _hook_index
    instance = _current_instance
    idx = _hook_index
    _hook_index += 1
    
    if idx >= len(instance._hooks):
        instance._hooks.append({"type": "state", "value": initial_val})
        
    hook = instance._hooks[idx]
    
    def set_state(new_val):
        if callable(new_val):
            new_val = new_val(hook["value"])
        if hook["value"] != new_val:
            hook["value"] = new_val
            instance.app.request_render()
            
    return hook["value"], set_state

def useEffect(effect_fn, deps=None):
    global _hook_index
    instance = _current_instance
    idx = _hook_index
    _hook_index += 1
    
    if idx >= len(instance._hooks):
        instance._hooks.append({"type": "effect", "deps": None, "cleanup": None})
        
    hook = instance._hooks[idx]
    
    changed = False
    if deps is None or hook["deps"] is None:
        changed = True
    else:
        if len(deps) != len(hook["deps"]):
            changed = True
        else:
            for d1, d2 in zip(deps, hook["deps"]):
                if d1 != d2:
                    changed = True
                    break
    
    if changed:
        hook["pending_effect"] = effect_fn
        hook["pending_deps"] = deps
        instance.app._pending_effects.append((instance, idx))

def useMemo(factory, deps):
    global _hook_index
    instance = _current_instance
    idx = _hook_index
    _hook_index += 1
    
    if idx >= len(instance._hooks):
        instance._hooks.append({"type": "memo", "deps": None, "value": None})
        
    hook = instance._hooks[idx]
    
    changed = False
    if hook["deps"] is None or len(deps) != len(hook["deps"]):
        changed = True
    else:
        for d1, d2 in zip(deps, hook["deps"]):
            if d1 != d2:
                changed = True
                break
                
    if changed:
        hook["value"] = factory()
        hook["deps"] = deps
        
    return hook["value"]

def useCallback(callback, deps):
    return useMemo(lambda: callback, deps)

def useRef(initial_val):
    global _hook_index
    instance = _current_instance
    idx = _hook_index
    _hook_index += 1
    
    if idx >= len(instance._hooks):
        instance._hooks.append({"type": "ref", "value": initial_val})
        
    return instance._hooks[idx]
