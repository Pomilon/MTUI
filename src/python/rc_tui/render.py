from . import tui_core

COLOR_NAMES = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'yellow': (255, 255, 0),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
    'gray': (128, 128, 128),
    'grey': (128, 128, 128),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
    'pink': (255, 192, 203),
}

def parse_color(c, default):
    if isinstance(c, (list, tuple)) and len(c) == 3:
        return c
    if isinstance(c, str):
        c = c.lower()
        if c in COLOR_NAMES:
            return COLOR_NAMES[c]
        if c.startswith('#'):
            try:
                if len(c) == 7:
                    return (int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16))
                if len(c) == 4:
                    r = int(c[1], 16); g = int(c[2], 16); b = int(c[3], 16)
                    return (r * 17, g * 17, b * 17)
            except ValueError:
                pass
    return default

def resolve_style(node, canvas, parent_style=None):
    props = node.props.copy()
    
    # Check if this node or any of its descendants are hovered
    is_hovered = False
    if canvas.app and canvas.app.hovered_node:
        curr = canvas.app.hovered_node
        while curr:
            if curr == node:
                is_hovered = True
                break
            curr = curr.parent

    # Apply pseudo-classes (Focus takes precedence over Hover)
    if is_hovered and 'hover_style' in props:
        hover = props['hover_style']
        if isinstance(hover, dict):
            props.update(hover)
            
    if node.is_focused and 'focus_style' in props:
        focus = props['focus_style']
        if isinstance(focus, dict):
            props.update(focus)

    # Default fallback values
    d_fg = (255, 255, 255)
    d_bg = (0, 0, 0)
    d_bold = False
    d_italic = False
    d_underline = False
    d_strikethrough = False
    
    # Inherit from parent if available
    if parent_style:
        d_fg = (parent_style.fg_r, parent_style.fg_g, parent_style.fg_b)
        d_bg = (parent_style.bg_r, parent_style.bg_g, parent_style.bg_b)
        d_bold = parent_style.bold
        d_italic = parent_style.italic
        d_underline = parent_style.underline
        d_strikethrough = parent_style.strikethrough

    fg = parse_color(props.get('fg'), d_fg)
    bg = parse_color(props.get('bg'), d_bg)
    bold = props.get('bold', d_bold)
    italic = props.get('italic', d_italic)
    underline = props.get('underline', d_underline)
    strikethrough = props.get('strikethrough', d_strikethrough)

    return tui_core.Style(
        int(fg[0]), int(fg[1]), int(fg[2]), 
        int(bg[0]), int(bg[1]), int(bg[2]), 
        bool(bold), bool(italic), bool(underline), bool(strikethrough)
    )

def resolve_border_style(props, main_style):
    d_bfg = (main_style.fg_r, main_style.fg_g, main_style.fg_b)
    d_bbg = (main_style.bg_r, main_style.bg_g, main_style.bg_b)
    
    bfg = parse_color(props.get('border_fg'), d_bfg)
    bbg = parse_color(props.get('border_bg'), d_bbg)
    
    return tui_core.Style(int(bfg[0]), int(bfg[1]), int(bfg[2]), int(bbg[0]), int(bbg[1]), int(bbg[2]), False, False, False, False)

def draw_tree(node, canvas, parent_style=None):
    if not node: return
    
    # Culling
    cx, cy, cw, ch = canvas.clip_rect
    if node.screen_x >= cx + cw or node.screen_x + node.w <= cx or \
       node.screen_y >= cy + ch or node.screen_y + node.h <= cy:
        return

    style = resolve_style(node, canvas, parent_style)
    
    # Fill background for containers
    if node.type in ('box', 'scrollbox', 'input', 'textarea', 'modal', 'dialog', 'code', 'asciifont', 'markdown'):
        # Box Shadow
        if node.props.get('box_shadow'):
            shadow_style = tui_core.Style(0, 0, 0, 15, 15, 15, False, False, False, False)
            canvas.fill_rect(node.screen_x + 1, node.screen_y + 1, node.w, node.h, shadow_style)

        # If the box has a border_bg but no bg, use border_bg as the fill color.
        fill_style = style
        if 'border_bg' in node.props and 'bg' not in node.props:
            bbg_raw = node.props['border_bg']
            bbg = parse_color(bbg_raw, (style.bg_r, style.bg_g, style.bg_b))
            fill_style = tui_core.Style(
                style.fg_r, style.fg_g, style.fg_b, 
                int(bbg[0]), int(bbg[1]), int(bbg[2]), 
                style.bold, style.italic, style.underline, style.strikethrough
            )
        
        canvas.fill_rect(node.screen_x, node.screen_y, node.w, node.h, fill_style)
        
        # Draw border
        if node.props.get('border'):
            b_style = resolve_border_style(node.props, style)
            b_type = node.props.get('border_type', 0)
            if isinstance(b_type, str):
                b_type = {"single": 0, "double": 1, "rounded": 2}.get(b_type.lower(), 0)
            
            title = node.props.get('title', '')
            canvas.draw_rect(node.screen_x, node.screen_y, node.w, node.h, b_style, b_type)
            if title:
                canvas.draw_text(node.screen_x + 2, node.screen_y, f" {title} ", b_style)

    # Per-type draw handler
    from .widgets import _DRAW
    handler = _DRAW.get(node.type)
    if handler:
        handler(node, canvas, style)

    # Handle clipping for containers
    is_container = node.type in ('box', 'scrollbox', 'modal', 'dialog')
    if is_container:
        canvas.push_clip_rect(node.screen_x, node.screen_y, node.w, node.h)
        if node.props.get('border'):
            canvas.push_clip_rect(node.screen_x + 1, node.screen_y + 1, node.w - 2, node.h - 2)

    # Draw children
    for child in node.children:
        draw_tree(child, canvas, style)

    # Pop clipping rects
    if is_container:
        if node.props.get('border'):
            canvas.pop_clip_rect()
        canvas.pop_clip_rect()

    # Draw scrollbars for ScrollBox
    if node.type == 'scrollbox':
        if node.content_h > node.h:
            track_style = resolve_style(node, canvas, parent_style)
            tr, tg, tb = track_style.bg_r, track_style.bg_g, track_style.bg_b
            track_style.fg_r, track_style.fg_g, track_style.fg_b = min(255, tr+20), min(255, tg+20), min(255, tb+20)
            for j in range(node.h):
                canvas.set_cell(node.screen_x + node.w - 1, node.screen_y + j, '▒', track_style)
            thumb_h = max(1, int(node.h * (node.h / node.content_h)))
            thumb_y = int(node.scroll_y * (node.h / node.content_h))
            thumb_style = resolve_style(node, canvas, parent_style)
            thumb_style.fg_r, thumb_style.fg_g, thumb_style.fg_b = 0, 255, 255
            for j in range(thumb_h):
                canvas.set_cell(node.screen_x + node.w - 1, node.screen_y + thumb_y + j, '█', thumb_style)

def draw_inspector(node, canvas):
    if not node: return
    inspect_style = tui_core.Style(0, 255, 255, 0, 0, 0, True)
    canvas.draw_rect(node.screen_x, node.screen_y, node.w, node.h, inspect_style, 2)
    info = f" {node.type.upper()} [{node.w}x{node.h}] @ ({node.screen_x},{node.screen_y}) "
    tag_x = max(0, min(canvas.width - len(info), node.screen_x))
    tag_y = node.screen_y - 1 if node.screen_y > 0 else node.screen_y + node.h
    if tag_y < 0: tag_y = 0
    if tag_y >= canvas.height: tag_y = canvas.height - 1
    tag_style = tui_core.Style(0, 0, 0, 0, 255, 255, True)
    canvas.draw_text(tag_x, tag_y, info, tag_style)
