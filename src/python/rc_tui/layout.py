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


def _apply_constraints(node, avail_w, avail_h):
    w_prop = node.props.get('width')
    h_prop = node.props.get('height')
    w = parse_dim(w_prop, avail_w) if w_prop is not None else avail_w
    h = parse_dim(h_prop, avail_h) if h_prop is not None else avail_h
    min_w = node.props.get('min_width', 0)
    max_w = node.props.get('max_width', avail_w)
    min_h = node.props.get('min_height', 0)
    max_h = node.props.get('max_height', avail_h)
    return max(min_w, min(w, max_w)), max(min_h, min(h, max_h))


def measure(node, max_w, max_h):
    if node.type in ('text', 'span'):
        text = str(node.props.get('text', ''))
        lines = text.split('\n')
        w = max((len(l) for l in lines), default=0)
        h = len(lines)
        return w, h

    from .widgets import _MEASURE
    handler = _MEASURE.get(node.type)
    if handler:
        return handler(node, max_w, max_h)

    (pt, pb, pl, pr), (mt, mb, ml, mr) = get_spacing(node)
    inner_max_w = max_w - pl - pr - ml - mr if max_w is not None else None
    inner_max_h = max_h - pt - pb - mt - mb if max_h is not None else None

    if inner_max_h is not None and inner_max_h <= 0:
        return 0, 0
    if inner_max_w is not None and inner_max_w <= 0:
        return 0, 0

    flex_dir = node.props.get('flex_direction', 'column')
    measured_w = 0
    measured_h = 0

    for child in node.children:
        if child is None:
            continue
        cw, ch = measure(child, inner_max_w, inner_max_h)
        (cpt, cpb, cpl, cpr), (cmt, cmb, cml, cmr) = get_spacing(child)
        child_main = (ch + cpt + cpb + cmt + cmb) if flex_dir == 'column' else (cw + cpl + cpr + cml + cmr)
        child_cross = (cw + cpl + cpr + cml + cmr) if flex_dir == 'column' else (ch + cpt + cpb + cmt + cmb)
        if flex_dir == 'column':
            measured_w = max(measured_w, child_cross)
            measured_h += child_main
        else:
            measured_w += child_main
            measured_h = max(measured_h, child_cross)

    w_prop = node.props.get('width')
    h_prop = node.props.get('height')
    if w_prop is not None:
        w = max(0, parse_dim(w_prop, max_w) - pl - pr - ml - mr)
    else:
        w = measured_w
    if h_prop is not None:
        h = max(0, parse_dim(h_prop, max_h) - pt - pb - mt - mb)
    else:
        h = measured_h
    return w, h


def layout(node, x, y, avail_w, avail_h, parent_screen_x=0, parent_screen_y=0):
    (pt, pb, pl, pr), (mt, mb, ml, mr) = get_spacing(node)

    if node.type in ('dialog', 'modal'):
        cw, ch = measure(node, avail_w, avail_h)
        cw, ch = _apply_constraints(node, avail_w - ml - mr, avail_h - mt - mb)
        if node.props.get('x') is None:
            x = (avail_w - cw) // 2
        if node.props.get('y') is None:
            y = (avail_h - ch) // 2
        avail_w = cw + ml + mr
        avail_h = ch + mt + mb

    assigned_w, assigned_h = _apply_constraints(node, avail_w - ml - mr, avail_h - mt - mb)

    node.x = x + ml
    node.y = y + mt
    node.w = assigned_w
    node.h = assigned_h
    node.screen_x = parent_screen_x + node.x
    node.screen_y = parent_screen_y + node.y

    inner_w = node.w - pl - pr
    inner_h = node.h - pt - pb

    if inner_w <= 0 or inner_h <= 0:
        node.content_w = 0
        node.content_h = 0
        return

    if not node.children:
        node.content_w = 0
        node.content_h = 0
        return

    child_data = []
    for child in node.children:
        if child is None:
            continue
        grow = child.props.get('flex_grow', 0)
        cw, ch = measure(child, inner_w, inner_h)
        (cpt, cpb, cpl, cpr), (cmt, cmb, cml, cmr) = get_spacing(child)
        child_data.append((child, cw, ch, grow, cpt, cpb, cpl, cpr, cmt, cmb, cml, cmr))

    flex_dir = node.props.get('flex_direction', 'column')
    gap = node.props.get('gap', 0)
    justify = node.props.get('justify_content', 'flex-start')
    align = node.props.get('align_items', 'stretch')

    flex_total = 0
    fixed_main = 0
    for _child, cw, ch, grow, cpt, cpb, cpl, cpr, cmt, cmb, cml, cmr in child_data:
        total_main = (ch + cpt + cpb + cmt + cmb) if flex_dir == 'column' else (cw + cpl + cpr + cml + cmr)
        if grow > 0:
            flex_total += grow
        else:
            fixed_main += total_main

    gap_count = max(0, len(child_data) - 1)
    fixed_main += gap_count * gap
    available_main = inner_h if flex_dir == 'column' else inner_w
    remaining = max(0, available_main - fixed_main)

    justify_offset = 0
    justify_gap = gap
    if justify == 'center':
        justify_offset = remaining // 2
    elif justify == 'flex-end':
        justify_offset = remaining
    elif justify == 'space-between' and len(child_data) > 1:
        justify_gap = remaining // (len(child_data) - 1)
    elif justify == 'space-around' and len(child_data) > 0:
        justify_gap = remaining // len(child_data)
        justify_offset = justify_gap // 2

    current_x = pl + (justify_offset if flex_dir == 'row' else 0)
    current_y = pt + (justify_offset if flex_dir == 'column' else 0)
    content_w = 0
    content_h = 0

    for child, cw, ch, grow, cpt, cpb, cpl, cpr, cmt, cmb, cml, cmr in child_data:
        total_main = (ch + cpt + cpb + cmt + cmb) if flex_dir == 'column' else (cw + cpl + cpr + cml + cmr)

        if grow > 0:
            share = int(remaining * (grow / flex_total)) if flex_total > 0 else 0
            if flex_dir == 'column':
                child_h = share
                child_w = inner_w
            else:
                child_w = share
                child_h = inner_h
        else:
            if flex_dir == 'column':
                child_h = total_main
                child_w = cw + cpl + cpr + cml + cmr
                if child.props.get('width') is None and align == 'stretch':
                    child_w = inner_w
            else:
                child_w = total_main
                child_h = ch + cpt + cpb + cmt + cmb
                if child.props.get('height') is None and align == 'stretch':
                    child_h = inner_h

        cross_offset = 0
        if align == 'center':
            if flex_dir == 'column':
                cross_offset = (inner_w - child_w) // 2
            else:
                cross_offset = (inner_h - child_h) // 2
        elif align == 'flex-end':
            if flex_dir == 'column':
                cross_offset = inner_w - child_w
            else:
                cross_offset = inner_h - child_h

        scroll_off_y = node.scroll_y if node.type == 'scrollbox' else 0
        scroll_off_x = node.scroll_x if node.type == 'scrollbox' else 0

        layout(child,
               current_x + (cross_offset if flex_dir == 'column' else 0),
               current_y + (cross_offset if flex_dir == 'row' else 0),
               child_w, child_h,
               node.screen_x - scroll_off_x, node.screen_y - scroll_off_y)

        if flex_dir == 'column':
            current_y += child_h + gap
            content_w = max(content_w, child_w)
            content_h += child_h
        else:
            current_x += child_w + gap
            content_w += child_w
            content_h = max(content_h, child_h)

    node.content_w = content_w
    node.content_h = content_h


do_layout = layout
