def parse_dim(val, parent_dim):
    if isinstance(val, int):
        return val
    if isinstance(val, str) and val.endswith('%') and parent_dim is not None:
        return int(parent_dim * float(val[:-1]) / 100)
    return None

def get_spacing(node):
    pad = node.props.get('padding', 0)
    mar = node.props.get('margin', 0)
    
    pad_t = node.props.get('padding_top', pad)
    pad_b = node.props.get('padding_bottom', pad)
    pad_l = node.props.get('padding_left', pad)
    pad_r = node.props.get('padding_right', pad)
    
    mar_t = node.props.get('margin_top', mar)
    mar_b = node.props.get('margin_bottom', mar)
    mar_l = node.props.get('margin_left', mar)
    mar_r = node.props.get('margin_right', mar)
    
    if node.props.get('border'):
        pad_t += 1
        pad_b += 1
        pad_l += 1
        pad_r += 1
        
    return (pad_t, pad_b, pad_l, pad_r), (mar_t, mar_b, mar_l, mar_r)

def measure(node, max_w, max_h):
    if node.type in ('text', 'span'):
        text = str(node.props.get('text', ''))
        lines = text.split('\n')
        w = max((len(l) for l in lines), default=0)
        h = len(lines)
        return w, h
    
    (pt, pb, pl, pr), (mt, mb, ml, mr) = get_spacing(node)
    
    w_prop = node.props.get('width')
    h_prop = node.props.get('height')
    
    # Intrinsic size components
    if node.type in ('input', 'textarea', 'progressbar'):
        w = parse_dim(w_prop, max_w) if w_prop is not None else (max_w if max_w is not None else 20)
        h = parse_dim(h_prop, max_h) if h_prop is not None else (5 if node.type == 'textarea' else 1)
        return w + pl + pr + ml + mr, h + pt + pb + mt + mb
    
    if node.type == 'button':
        text = str(node.props.get('text', ''))
        w = parse_dim(w_prop, max_w) if w_prop is not None else (len(text) + 4)
        h = parse_dim(h_prop, max_h) if h_prop is not None else 1
        return w + pl + pr + ml + mr, h + pt + pb + mt + mb

    if node.type == 'checkbox':
        label = str(node.props.get('label', ''))
        w = parse_dim(w_prop, max_w) if w_prop is not None else (len(label) + 4)
        h = parse_dim(h_prop, max_h) if h_prop is not None else 1
        return w + pl + pr + ml + mr, h + pt + pb + mt + mb
        
    if node.type == 'divider':
        w = max_w if max_w is not None else 1
        h = 1
        return w, h
    
    if node.type == 'radiobutton':
        label = str(node.props.get('label', ''))
        w = parse_dim(w_prop, max_w) if w_prop is not None else (len(label) + 4)
        h = 1
        return w + ml + mr, h + mt + mb
        
    if node.type == 'switch':
        label = str(node.props.get('label', ''))
        w = parse_dim(w_prop, max_w) if w_prop is not None else (len(label) + 10)
        h = 1
        return w + ml + mr, h + mt + mb
        
    if node.type == 'select':
        options = node.props.get('options', [])
        max_opt_w = max((len(str(o)) for o in options), default=0)
        w = parse_dim(w_prop, max_w) if w_prop is not None else (max_opt_w + 6)
        h = 1
        return w + pl + pr + ml + mr, h + pt + pb + mt + mb

    if node.type == 'tabselect':
        options = node.props.get('options', [])
        total_w = sum(len(str(o)) + 4 for o in options)
        return total_w + ml + mr, 1 + mt + mb

    if node.type in ('code', 'diff', 'markdown'):
        w = parse_dim(w_prop, max_w) if w_prop is not None else (max_w if max_w is not None else 40)
        content = str(node.props.get('content', ''))
        if node.type == 'markdown':
            h = parse_dim(h_prop, max_h) if h_prop is not None else len(content.split('\n')) + 2
        else:
            h = parse_dim(h_prop, max_h) if h_prop is not None else 10
        return w + ml + mr, h + mt + mb
    
    if node.type == 'linenumber':
        count = node.props.get('count', 0)
        w = len(str(count)) + 2
        return w, 1

    if node.type == 'asciifont':
        return (max_w or 40) + ml + mr, 5 + mt + mb
        
    if node.type == 'toast':
        message = str(node.props.get('message', ''))
        w = len(message) + 4
        h = 3
        return w, h

    if node.type in ('dialog', 'modal'):
        w = parse_dim(w_prop, max_w) if w_prop is not None else (max_w // 2 if max_w else 40)
        h = parse_dim(h_prop, max_h) if h_prop is not None else (max_h // 2 if max_h else 10)
        measured_w, measured_h = w, h
    else:
        w = parse_dim(w_prop, max_w)
        h = parse_dim(h_prop, max_h)
    
    if w is not None and h is not None and node.type not in ('dialog', 'modal', 'box', 'scrollbox'):
        node.w = w + pl + pr + ml + mr
        node.h = h + pt + pb + mt + mb
        return node.w, node.h
        
    flex_dir = node.props.get('flex_direction', 'column')
    inner_max_w = max_w - pl - pr - ml - mr if max_w is not None else None
    inner_max_h = max_h - pt - pb - mt - mb if max_h is not None else None
    
    measured_w = 0
    measured_h = 0
    
    for child in node.children:
        cw, ch = measure(child, inner_max_w, inner_max_h)
        if flex_dir == 'column':
            measured_w = max(measured_w, cw)
            measured_h += ch
        else:
            measured_w += cw
            measured_h = max(measured_h, ch)
            
    if w is None:
        w = measured_w + pl + pr + ml + mr
    if h is None:
        h = measured_h + pt + pb + mt + mb
        
    node.w = w
    node.h = h
    node.content_w = measured_w
    node.content_h = measured_h
    return w, h

def do_layout(node, x, y, assigned_w, assigned_h, parent_screen_x=0, parent_screen_y=0):
    if node.type in ('dialog', 'modal'):
        if node.props.get('x') is None:
            x = (assigned_w - node.w) // 2
        else:
            x = parse_dim(node.props.get('x'), assigned_w)
            
        if node.props.get('y') is None:
            y = (assigned_h - node.h) // 2
        else:
            y = parse_dim(node.props.get('y'), assigned_h)
            
        assigned_w = node.w
        assigned_h = node.h

    (pt, pb, pl, pr), (mt, mb, ml, mr) = get_spacing(node)

    # Note: assigned_w includes margin
    node.x = x + ml
    node.y = y + mt
    node.w = assigned_w - ml - mr
    node.h = assigned_h - mt - mb
    node.screen_x = parent_screen_x + node.x
    node.screen_y = parent_screen_y + node.y
    
    inner_w = node.w - pl - pr
    inner_h = node.h - pt - pb
    
    flex_dir = node.props.get('flex_direction', 'column')
    gap = node.props.get('gap', 0)
    
    flex_total = 0
    fixed_space = 0
    
    child_measures = []
    non_null_children = [c for c in node.children if c is not None]
    gap_count = max(0, len(non_null_children) - 1)
    fixed_space += gap_count * gap

    for child in non_null_children:
        grow = child.props.get('flex_grow', 0)
        if grow > 0:
            flex_total += grow
            child_measures.append((child, 0, 0, grow))
        else:
            cw, ch = measure(child, inner_w, inner_h)
            if flex_dir == 'column':
                fixed_space += ch
            else:
                fixed_space += cw
            child_measures.append((child, cw, ch, 0))
            
    remaining_space = max(0, (inner_h if flex_dir == 'column' else inner_w) - fixed_space)
    
    current_x = pl
    current_y = pt
    
    for i, (child, cw, ch, grow) in enumerate(child_measures):
        if grow > 0:
            share = int(remaining_space * (grow / flex_total)) if flex_total > 0 else 0
            if flex_dir == 'column':
                ch = share
                cw = inner_w
            else:
                cw = share
                ch = inner_h
        else:
            if flex_dir == 'column' and child.props.get('width') is None:
                cw = inner_w
            if flex_dir == 'row' and child.props.get('height') is None:
                ch = inner_h
                
        scroll_off_y = node.scroll_y if node.type == 'scrollbox' else 0
        scroll_off_x = node.scroll_x if node.type == 'scrollbox' else 0
        
        do_layout(child, current_x, current_y, cw, ch, node.screen_x - scroll_off_x, node.screen_y - scroll_off_y)
        
        if flex_dir == 'column':
            current_y += ch + gap
        else:
            current_x += cw + gap
