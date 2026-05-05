from . import tui_core
import pyfiglet
import difflib
import time
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

def resolve_style(props, parent_style=None):
    # Default fallback values
    d_fg = (255, 255, 255)
    d_bg = (0, 0, 0)
    d_bold = False
    
    # Inherit from parent if available
    if parent_style:
        d_fg = (parent_style.fg_r, parent_style.fg_g, parent_style.fg_b)
        d_bg = (parent_style.bg_r, parent_style.bg_g, parent_style.bg_b)
        d_bold = parent_style.bold

    # Check for a 'style' dictionary prop
    style_dict = props.get('style', {})
    
    # Override with current props or style_dict
    fg = props.get('fg', style_dict.get('fg', d_fg))
    bg = props.get('bg', style_dict.get('bg', d_bg))
    bold = props.get('bold', style_dict.get('bold', d_bold))

    # Handle individual components if provided
    fg_r = props.get('fg_r', style_dict.get('fg_r', fg[0] if isinstance(fg, (list, tuple)) else 255))
    fg_g = props.get('fg_g', style_dict.get('fg_g', fg[1] if isinstance(fg, (list, tuple)) else 255))
    fg_b = props.get('fg_b', style_dict.get('fg_b', fg[2] if isinstance(fg, (list, tuple)) else 255))
    
    bg_r = props.get('bg_r', style_dict.get('bg_r', bg[0] if isinstance(bg, (list, tuple)) else 0))
    bg_g = props.get('bg_g', style_dict.get('bg_g', bg[1] if isinstance(bg, (list, tuple)) else 0))
    bg_b = props.get('bg_b', style_dict.get('bg_b', bg[2] if isinstance(bg, (list, tuple)) else 0))

    return tui_core.Style(int(fg_r), int(fg_g), int(fg_b), int(bg_r), int(bg_g), int(bg_b), bool(bold))

def resolve_border_style(props, main_style):
    d_bfg = (main_style.fg_r, main_style.fg_g, main_style.fg_b)
    d_bbg = (main_style.bg_r, main_style.bg_g, main_style.bg_b)
    
    bfg = props.get('border_fg', d_bfg)
    bbg = props.get('border_bg', d_bbg)
    
    # Simple normalization
    if not isinstance(bfg, (list, tuple)) or len(bfg) != 3: bfg = d_bfg
    if not isinstance(bbg, (list, tuple)) or len(bbg) != 3: bbg = d_bbg
    
    return tui_core.Style(int(bfg[0]), int(bfg[1]), int(bfg[2]), int(bbg[0]), int(bbg[1]), int(bbg[2]), False)

def draw_tree(node, canvas, parent_style=None):
    if not node: return
    
    # Culling
    cx, cy, cw, ch = canvas.clip_rect
    if node.screen_x >= cx + cw or node.screen_x + node.w <= cx or \
       node.screen_y >= cy + ch or node.screen_y + node.h <= cy:
        return

    style = resolve_style(node.props, parent_style)
    
    # Fill background for containers
    if node.type in ('box', 'scrollbox', 'input', 'textarea', 'modal', 'dialog', 'code', 'asciifont', 'markdown'):
        # If the box has a border_bg but no bg, use border_bg as the fill color.
        fill_style = style
        if 'border_bg' in node.props and 'bg' not in node.props:
            bbg = node.props['border_bg']
            fill_style = tui_core.Style(style.fg_r, style.fg_g, style.fg_b, int(bbg[0]), int(bbg[1]), int(bbg[2]), style.bold)
        
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

    if node.type == 'text' or node.type == 'span':
        text = str(node.props.get('text', ''))
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if node.screen_y + i < node.screen_y + node.h:
                canvas.draw_text(node.screen_x, node.screen_y + i, line[:node.w], style)

    if node.type == 'tabselect':
        options = node.props.get('options', [])
        selected_idx = node.props.get('selected_index', 0)
        curr_x = node.screen_x
        for i, opt in enumerate(options):
            is_sel = (i == selected_idx)
            text = f" {opt} "
            tab_style = resolve_style(node.props, parent_style)
            if is_sel:
                tab_style.bg_r, tab_style.bg_g, tab_style.bg_b = 60, 60, 80
                tab_style.bold = True
            if curr_x + len(text) <= node.screen_x + node.w:
                canvas.draw_text(curr_x, node.screen_y, text, tab_style)
            curr_x += len(text) + 1

    if node.type == 'textarea':
        val = str(node.props.get('value', ''))
        lines = val.split('\n')
        for i, line in enumerate(lines[:node.h]):
            canvas.draw_text(node.screen_x, node.screen_y + i, line[:node.w], style)
            
        if node.is_focused:
            cursor_y = min(len(lines) - 1, node.h - 1)
            cursor_x = min(len(lines[cursor_y]), node.w - 1)
            canvas.draw_text(node.screen_x + cursor_x, node.screen_y + cursor_y, "_", style)

    if node.type == 'code':
        content = str(node.props.get('content', ''))
        try:
            # Language and Parser setup for tree-sitter 0.22+
            lang = Language(tspython.language())
            parser = Parser(lang)
            tree = parser.parse(content.encode('utf-8'))
            
            # Map tree-sitter node types to colors
            color_map = {
                # Keywords
                'def': (200, 100, 200),
                'class': (200, 100, 200),
                'return': (200, 100, 200),
                'import': (200, 100, 200),
                'from': (200, 100, 200),
                'if': (200, 100, 200),
                'else': (200, 100, 200),
                'elif': (200, 100, 200),
                'for': (200, 100, 200),
                'while': (200, 100, 200),
                'try': (200, 100, 200),
                'except': (200, 100, 200),
                'with': (200, 100, 200),
                'as': (200, 100, 200),
                'lambda': (200, 100, 200),
                'pass': (200, 100, 200),
                'in': (200, 100, 200),
                'is': (200, 100, 200),
                'not': (200, 100, 200),
                'and': (200, 100, 200),
                'or': (200, 100, 200),
                
                # Literals
                'string': (100, 200, 100),
                'integer': (200, 200, 100),
                'float': (200, 200, 100),
                'comment': (120, 120, 120),
                
                # Others
                'identifier': (100, 200, 255),
                'function_definition': (100, 200, 255),
                'attribute': (255, 180, 100),
                'keyword_argument': (255, 150, 100),
            }
            
            highlights = {}
            def traverse(ts_node):
                # Only color leaf nodes or specific types
                if not ts_node.children or ts_node.type in ('string', 'comment'):
                    if ts_node.type in color_map:
                        for i in range(ts_node.start_byte, ts_node.end_byte):
                            highlights[i] = color_map[ts_node.type]
                
                for child in ts_node.children:
                    traverse(child)
            
            traverse(tree.root_node)
            
            lines = content.split('\n')
            byte_idx = 0
            for i, line in enumerate(lines[:node.h]):
                curr_x = node.screen_x
                for char in line:
                    char_style = tui_core.Style(style.fg_r, style.fg_g, style.fg_b, style.bg_r, style.bg_g, style.bg_b, style.bold)
                    if byte_idx in highlights:
                        r, g, b = highlights[byte_idx]
                        char_style.fg_r, char_style.fg_g, char_style.fg_b = r, g, b
                    if curr_x < node.screen_x + node.w:
                        canvas.set_cell(curr_x, node.screen_y + i, char, char_style)
                    curr_x += 1
                    byte_idx += len(char.encode('utf-8'))
                byte_idx += 1 # newline
        except Exception:
            for i, line in enumerate(content.split('\n')[:node.h]):
                canvas.draw_text(node.screen_x, node.screen_y + i, line[:node.w], style)

    if node.type == 'diff':
        content = str(node.props.get('content', ''))
        lines = content.split('\n')
        for i, line in enumerate(lines[:node.h]):
            line_style = resolve_style(node.props, parent_style)
            if line.startswith('+'):
                line_style.fg_r, line_style.fg_g, line_style.fg_b = 100, 255, 100
            elif line.startswith('-'):
                line_style.fg_r, line_style.fg_g, line_style.fg_b = 255, 100, 100
            canvas.draw_text(node.screen_x, node.screen_y + i, line[:node.w], line_style)

    if node.type == 'asciifont':
        text = str(node.props.get('text', ''))
        font = node.props.get('font', 'slant')
        try:
            f = pyfiglet.Figlet(font=font)
            rendered = f.renderText(text)
            lines = rendered.split('\n')
            for i, line in enumerate(lines[:node.h]):
                canvas.draw_text(node.screen_x, node.screen_y + i, line[:node.w], style)
        except:
            canvas.draw_text(node.screen_x, node.screen_y, text[:node.w], style)

    if node.type == 'markdown':
        content = str(node.props.get('content', ''))
        # Use C++ side markdown renderer for efficiency
        canvas.buffer.draw_markdown(node.screen_x, node.screen_y, node.w, node.h, content, style, cx, cy, cw, ch)

    if node.type == 'linenumber':
        count = node.props.get('count', 0)
        num_style = resolve_style(node.props, parent_style)
        num_style.fg_r = num_style.fg_g = num_style.fg_b = 100
        for i in range(node.h):
            canvas.draw_text(node.screen_x, node.screen_y + i, str(i+1).rjust(node.w-1), num_style)

    if node.type == 'radiobutton':
        label = str(node.props.get('label', ''))
        selected = node.props.get('selected', False)
        icon = "◉" if selected else "○"
        rb_style = resolve_style(node.props, parent_style)
        if node.is_focused:
            rb_style.fg_r, rb_style.fg_g, rb_style.fg_b = 0, 255, 255
        canvas.draw_text(node.screen_x, node.screen_y, f"{icon} {label}"[:node.w], rb_style)

    if node.type == 'switch':
        label = str(node.props.get('label', ''))
        on = node.props.get('on', False)
        sw_text = "[ON ]" if on else "[OFF]"
        sw_style = resolve_style(node.props, parent_style)
        
        state_style = tui_core.Style(sw_style.fg_r, sw_style.fg_g, sw_style.fg_b, sw_style.bg_r, sw_style.bg_g, sw_style.bg_b, sw_style.bold)
        if on:
            state_style.fg_r, state_style.fg_g, state_style.fg_b = 0, 255, 0
        else:
            state_style.fg_r, state_style.fg_g, state_style.fg_b = 255, 0, 0
            
        if node.is_focused:
            sw_style.fg_r, sw_style.fg_g, sw_style.fg_b = 0, 255, 255
            
        canvas.draw_text(node.screen_x, node.screen_y, sw_text, state_style)
        if label:
            canvas.draw_text(node.screen_x + len(sw_text) + 1, node.screen_y, label[:node.w - len(sw_text) - 1], sw_style)

    if node.type == 'divider':
        canvas.draw_text(node.screen_x, node.screen_y, "─" * node.w, style)

    if node.type == 'button':
        text = str(node.props.get('text', ''))
        btn_style = resolve_style(node.props, parent_style)
        if node.is_focused:
            btn_style.bg_r, btn_style.bg_g, btn_style.bg_b = 0, 100, 100
        canvas.fill_rect(node.screen_x, node.screen_y, node.w, node.h, btn_style)
        label_x = node.screen_x + (node.w - len(text)) // 2
        canvas.draw_text(max(node.screen_x, label_x), node.screen_y, text[:node.w], btn_style)

    if node.type == 'checkbox':
        label = str(node.props.get('label', ''))
        checked = node.props.get('checked', False)
        box = "[x]" if checked else "[ ]"
        check_style = resolve_style(node.props, parent_style)
        if node.is_focused:
            check_style.fg_r, check_style.fg_g, check_style.fg_b = 0, 255, 255
        canvas.draw_text(node.screen_x, node.screen_y, f"{box} {label}"[:node.w], check_style)

    if node.type == 'progressbar':
        progress = max(0.0, min(1.0, node.props.get('progress', 0.0)))
        bar_style = resolve_style(node.props, parent_style)
        
        width = node.w
        if width < 3:
            canvas.draw_text(node.screen_x, node.screen_y, "█" * width, bar_style)
        else:
            inner_w = width - 2
            filled_w = int(inner_w * progress)
            empty_w = inner_w - filled_w
            
            canvas.draw_text(node.screen_x, node.screen_y, "[", bar_style)
            if filled_w > 0:
                canvas.draw_text(node.screen_x + 1, node.screen_y, "█" * filled_w, bar_style)
            if empty_w > 0:
                canvas.draw_text(node.screen_x + 1 + filled_w, node.screen_y, " " * empty_w, bar_style)
            canvas.draw_text(node.screen_x + width - 1, node.screen_y, "]", bar_style)

    if node.type == 'input':
        val = node.props.get('value', '')
        ph = node.props.get('placeholder', 'Type here...')
        display = val if val else ph
        input_style = resolve_style(node.props, parent_style)
        if node.is_focused:
            input_style.fg_r, input_style.fg_g, input_style.fg_b = 0, 255, 255
        off = 1 if node.props.get('border') else 0
        canvas.draw_text(node.screen_x + off, node.screen_y + off, display[:node.w-(off*2)], input_style)
        if node.is_focused:
            cursor_pos = len(val)
            if cursor_pos < node.w - (off * 2):
                canvas.draw_text(node.screen_x + off + cursor_pos, node.screen_y + off, "_", input_style)

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
            track_style = resolve_style(node.props, parent_style)
            tr, tg, tb = track_style.bg_r, track_style.bg_g, track_style.bg_b
            track_style.fg_r, track_style.fg_g, track_style.fg_b = min(255, tr+20), min(255, tg+20), min(255, tb+20)
            for j in range(node.h):
                canvas.set_cell(node.screen_x + node.w - 1, node.screen_y + j, '▒', track_style)
            thumb_h = max(1, int(node.h * (node.h / node.content_h)))
            thumb_y = int(node.scroll_y * (node.h / node.content_h))
            thumb_style = resolve_style(node.props, parent_style)
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
