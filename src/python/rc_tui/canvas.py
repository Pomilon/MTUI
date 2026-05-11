from typing import Tuple, List
from . import tui_core

class Canvas:
    def __init__(self, buffer: tui_core.Buffer):
        self.buffer = buffer
        self.width = buffer.get_width()
        self.height = buffer.get_height()
        # Stack of clipping rects: (x, y, w, h)
        self._clip_stack: List[Tuple[int, int, int, int]] = [(0, 0, self.width, self.height)]

    @property
    def clip_rect(self) -> Tuple[int, int, int, int]:
        return self._clip_stack[-1]

    def push_clip_rect(self, x: int, y: int, w: int, h: int):
        # New clip rect is the intersection of the current one and the requested one
        cx, cy, cw, ch = self.clip_rect
        nx = max(x, cx)
        ny = max(y, cy)
        nw = max(0, min(x + w, cx + cw) - nx)
        nh = max(0, min(y + h, cy + ch) - ny)
        self._clip_stack.append((nx, ny, nw, nh))

    def pop_clip_rect(self):
        if len(self._clip_stack) > 1:
            self._clip_stack.pop()

    def set_cell(self, x: int, y: int, char: str, style: tui_core.Style):
        # Check screen boundaries (Buffer::setCell already does this, but we check here too for safety)
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        
        # Check clipping rect boundaries
        cx, cy, cw, ch = self.clip_rect
        if not (cx <= x < cx + cw and cy <= y < cy + ch):
            return

        # Ensure we only use the first character if a string is passed
        char_to_set = char[0] if char else ' '
        self.buffer.set_cell(x, y, char_to_set, style)

    def draw_text(self, x: int, y: int, text: str, style: tui_core.Style):
        cx, cy, cw, ch = self.clip_rect
        if y < cy or y >= cy + ch:
            return
            
        # Determine visible portion of the text relative to clip_rect
        start_x = max(x, cx)
        end_x = min(x + len(text), cx + cw)
        
        if start_x >= end_x:
            return
            
        visible_text = text[start_x - x : end_x - x]
        self.buffer.draw_text(start_x, y, visible_text, style)

    def draw_rect(self, x: int, y: int, w: int, h: int, style: tui_core.Style, 
                  type=0, top_left=None, top_right=None, bot_left=None, bot_right=None, 
                  horiz=None, vert=None):
        
        # If any custom characters are provided, we fallback to manual drawing
        if any(c is not None for c in (top_left, top_right, bot_left, bot_right, horiz, vert)):
            tl = top_left or '┌'
            tr = top_right or '┐'
            bl = bot_left or '└'
            br = bot_right or '┘'
            h_char = horiz or '─'
            v_char = vert or '│'
            
            for i in range(x, x + w):
                self.set_cell(i, y, h_char, style)
                self.set_cell(i, y + h - 1, h_char, style)
            for j in range(y, y + h):
                self.set_cell(x, j, v_char, style)
                self.set_cell(x + w - 1, j, v_char, style)
            self.set_cell(x, y, tl, style)
            self.set_cell(x + w - 1, y, tr, style)
            self.set_cell(x, y + h - 1, bl, style)
            self.set_cell(x + w - 1, y + h - 1, br, style)
        else:
            # We use optimized C++ implementation ONLY if the rect is fully inside the clip_rect
            # because C++ draw_rect doesn't respect the clip_rect yet.
            cx, cy, cw, ch = self.clip_rect
            if x >= cx and y >= cy and x + w <= cx + cw and y + h <= cy + ch:
                self.buffer.draw_rect(x, y, w, h, style, type)
            else:
                # Fallback to manual set_cell which respects self.clip_rect
                chars = {
                    0: ("┌", "┐", "└", "┘", "─", "│"),
                    1: ("╔", "╗", "╚", "╝", "═", "║"),
                    2: ("╭", "╮", "╰", "╯", "─", "│")
                }.get(type, ("┌", "┐", "└", "┘", "─", "│"))
                
                tl, tr, bl, br, hc, vc = chars
                for i in range(x, x + w):
                    self.set_cell(i, y, hc, style)
                    self.set_cell(i, y + h - 1, hc, style)
                for j in range(y, y + h):
                    self.set_cell(x, j, vc, style)
                    self.set_cell(x + w - 1, j, vc, style)
                self.set_cell(x, y, tl, style)
                self.set_cell(x + w - 1, y, tr, style)
                self.set_cell(x, y + h - 1, bl, style)
                self.set_cell(x + w - 1, y + h - 1, br, style)

    def fill_rect(self, x: int, y: int, w: int, h: int, style: tui_core.Style):
        # Intersection of rect and current clip_rect
        cx, cy, cw, ch = self.clip_rect
        x1 = max(x, cx)
        y1 = max(y, cy)
        x2 = min(x + w, cx + cw)
        y2 = min(y + h, cy + ch)
        
        if x1 < x2 and y1 < y2:
            self.buffer.fill_rect(x1, y1, x2 - x1, y2 - y1, style)

    def draw_panel(self, x: int, y: int, w: int, h: int, title: str, style: tui_core.Style):
        self.draw_rect(x, y, w, h, style)
        # Title
        for i, char in enumerate(title):
            self.set_cell(x + 2 + i, y, char, style)
